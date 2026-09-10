"""
Position Persistence Manager
Salva e carica posizioni come V37
"""
import json
import math
import os
from datetime import datetime


class StatePersistenceError(RuntimeError):
    """Stato persistito assente, corrotto o strutturalmente non valido."""
    pass


class PositionsPersistence:
    """Gestisce salvataggio posizioni e trade"""
    
    def __init__(self, data_dir='perpetual_data'):
        self.data_dir = data_dir
        self.positions_file = os.path.join(data_dir, 'positions.json')
        self.trades_file = os.path.join(data_dir, 'trades.json')
        self.capital_file = os.path.join(data_dir, 'capital.json')
        self.transaction_file = os.path.join(
            data_dir, 'transaction_pending.json'
        )
        
        # Crea directory se non esiste
        os.makedirs(data_dir, exist_ok=True)

        # Se un crash ha lasciato una transazione completa nel journal,
        # completa deterministicamente il commit prima di caricare lo stato.
        self._recover_pending_transaction()

        positions_exists = os.path.exists(self.positions_file)
        trades_exists = os.path.exists(self.trades_file)
        capital_exists = os.path.exists(self.capital_file)

        # Stato parziale = situazione ambigua e potenzialmente pericolosa.
        if positions_exists != trades_exists:
            raise StatePersistenceError(
                "Partial Perpetual state: positions.json and trades.json "
                "must either both exist or both be absent"
            )

        # Se esiste capitale precedente, l'assenza simultanea dei due ledger
        # NON può essere interpretata come fresh install.
        if not positions_exists and not trades_exists and capital_exists:
            raise StatePersistenceError(
                "positions.json and trades.json are both missing while "
                "capital.json exists"
            )

        # Fresh install reale: nessuno stato persistito esistente.
        if not positions_exists and not trades_exists:
            self._save_json(self.positions_file, {})
            self._save_json(self.trades_file, [])
    
    def _positions_to_data(self, positions):
        """Converte le posizioni RAM nel formato JSON persistito."""
        if not isinstance(positions, dict):
            raise StatePersistenceError("positions must be a dict")

        data = {}

        for symbol, pos in positions.items():
            pos_data = {
                'symbol': pos['symbol'],
                'direction': pos['direction'],
                'entry_price': pos['entry_price'],
                'entry_time': pos['entry_time'].isoformat(),
                'quantity': pos['quantity'],
                'notional': pos['notional'],
                'leverage': pos['leverage'],
                'stop_loss': pos['stop_loss'],
                'take_profit': pos['take_profit'],
                'trailing_stop': {
                    'enabled': pos['trailing_stop']['enabled'],
                    'activation_price': pos['trailing_stop']['activation_price'],
                    'trail_distance_pct': pos['trailing_stop']['trail_distance_pct'],
                    'active': pos['trailing_stop']['active'],
                    'current_stop': pos['trailing_stop']['current_stop']
                },
                'rr_ratio': pos['rr_ratio']
            }
            data[symbol] = pos_data

        return data

    def save_positions(self, positions):
        """Salva atomicamente le posizioni aperte."""
        data = self._positions_to_data(positions)
        self._save_json(self.positions_file, data)
        return True

    def load_positions(self):
        """
        Carica posizioni salvate
        Returns: dict con posizioni
        """
        data = self._load_json(self.positions_file, dict)
        
        if not data:
            return {}
        
        positions = {}
        for symbol, pos_data in data.items():
            # Converti string in datetime
            pos_data['entry_time'] = datetime.fromisoformat(pos_data['entry_time'])
            positions[symbol] = pos_data
        
        return positions
    
    def save_trade(self, trade):
        """
        Salva trade completato (come V37)
        """
        trades = self._load_json(self.trades_file, list)
        
        # Aggiungi nuovo trade
        trades.append(trade)
        
        self._save_json(self.trades_file, trades)
        return True
    
    def load_trades(self):
        """Carica tutti i trade"""
        return self._load_json(self.trades_file, list)
    
    def get_trade_count(self):
        """Conta trade totali"""
        trades = self.load_trades()
        return len(trades)
    
    def get_capital_from_trades(self):
        """Recupera capitale dall'ultimo trade (come V37)"""
        trades = self.load_trades()
        
        if not trades:
            return None
        
        # Ultimo trade ha il capitale finale
        last_trade = trades[-1]
        return last_trade.get('final_capital')
    
    def _build_close_transaction(self, positions, trade, new_capital):
        """Costruisce lo stato finale completo di una chiusura."""
        if not isinstance(trade, dict):
            raise StatePersistenceError("trade must be a dict")

        required = {
            'symbol',
            'entry_time',
            'exit_time',
            'pnl_usd',
            'final_capital',
        }

        missing = required - set(trade)

        if missing:
            raise StatePersistenceError(
                f"trade missing required fields: {sorted(missing)}"
            )

        try:
            capital = float(new_capital)
            trade_capital = float(trade['final_capital'])
        except (TypeError, ValueError) as exc:
            raise StatePersistenceError(
                "invalid capital in close transaction"
            ) from exc

        if not math.isfinite(capital) or capital <= 0:
            raise StatePersistenceError(
                f"invalid transaction capital: {capital}"
            )

        if not math.isfinite(trade_capital):
            raise StatePersistenceError(
                "trade final_capital is not finite"
            )

        if abs(trade_capital - capital) > 1e-9:
            raise StatePersistenceError(
                "trade final_capital does not match transaction capital"
            )

        current_trades = self.load_trades()

        same_id = [
            existing
            for existing in current_trades
            if existing.get('entry_time') == trade['entry_time']
            and existing.get('exit_time') == trade['exit_time']
        ]

        if same_id:
            if any(existing != trade for existing in same_id):
                raise StatePersistenceError(
                    "conflicting trade with same entry_time/exit_time"
                )
            target_trades = list(current_trades)
        else:
            target_trades = list(current_trades) + [trade]

        return {
            'version': 1,
            'kind': 'close_position',
            'created_at': datetime.now().isoformat(),
            'positions': self._positions_to_data(positions),
            'trades': target_trades,
            'capital': {
                'capital': capital,
                'updated': trade['exit_time'],
            },
        }

    def _validate_close_transaction(self, transaction):
        """Valida un journal prima di applicarlo."""
        if not isinstance(transaction, dict):
            raise StatePersistenceError(
                "transaction journal must be a dict"
            )

        if transaction.get('version') != 1:
            raise StatePersistenceError(
                "unsupported transaction journal version"
            )

        if transaction.get('kind') != 'close_position':
            raise StatePersistenceError(
                "unsupported transaction journal kind"
            )

        positions = transaction.get('positions')
        trades = transaction.get('trades')
        capital_data = transaction.get('capital')

        if not isinstance(positions, dict):
            raise StatePersistenceError(
                "transaction positions must be a dict"
            )

        if not isinstance(trades, list) or not trades:
            raise StatePersistenceError(
                "transaction trades must be a non-empty list"
            )

        if not all(isinstance(t, dict) for t in trades):
            raise StatePersistenceError(
                "transaction contains invalid trade entries"
            )

        if not isinstance(capital_data, dict):
            raise StatePersistenceError(
                "transaction capital must be a dict"
            )

        if 'capital' not in capital_data:
            raise StatePersistenceError(
                "transaction capital field missing"
            )

        try:
            capital = float(capital_data['capital'])
        except (TypeError, ValueError) as exc:
            raise StatePersistenceError(
                "invalid transaction capital"
            ) from exc

        if not math.isfinite(capital) or capital <= 0:
            raise StatePersistenceError(
                f"invalid transaction capital: {capital}"
            )

        last = trades[-1]

        if 'final_capital' not in last:
            raise StatePersistenceError(
                "last transaction trade has no final_capital"
            )

        try:
            final_capital = float(last['final_capital'])
        except (TypeError, ValueError) as exc:
            raise StatePersistenceError(
                "invalid final_capital in transaction trade"
            ) from exc

        if (
            not math.isfinite(final_capital)
            or abs(final_capital - capital) > 1e-9
        ):
            raise StatePersistenceError(
                "transaction trade/capital mismatch"
            )

    def _apply_close_transaction(self, transaction):
        """Applica idempotentemente lo stato finale del journal."""
        self._validate_close_transaction(transaction)

        # Finché il journal esiste, qualunque crash è recuperabile.
        self._save_json(
            self.trades_file,
            transaction['trades']
        )
        self._save_json(
            self.positions_file,
            transaction['positions']
        )
        self._save_json(
            self.capital_file,
            transaction['capital']
        )

    def _clear_transaction_file(self):
        """Rimuove il journal e rende durevole la rimozione."""
        try:
            os.unlink(self.transaction_file)
        except FileNotFoundError:
            return
        except OSError as exc:
            raise StatePersistenceError(
                f"unable to remove transaction journal: {exc}"
            ) from exc

        try:
            dir_fd = os.open(self.data_dir, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except OSError:
            pass

    def _recover_pending_transaction(self):
        """Roll-forward di una transazione rimasta pendente."""
        if not os.path.exists(self.transaction_file):
            return False

        transaction = self._load_json(
            self.transaction_file,
            dict
        )

        self._validate_close_transaction(transaction)
        self._apply_close_transaction(transaction)
        self._clear_transaction_file()

        return True

    def commit_close_transaction(self, positions, trade, new_capital):
        """Commit WAL di positions + trades + capital."""
        transaction = self._build_close_transaction(
            positions,
            trade,
            new_capital,
        )

        # 1. Journal completo e durevole.
        self._save_json(
            self.transaction_file,
            transaction
        )

        # 2. Stato finale. In caso di crash il journal resta disponibile.
        self._apply_close_transaction(transaction)

        # 3. Solo dopo tutti i file completati il journal viene eliminato.
        self._clear_transaction_file()

        return transaction['trades']

    def _save_json(self, filename, data):
        """Salva JSON atomicamente: il file precedente resta valido fino al replace."""
        directory = os.path.dirname(filename) or '.'
        tmp_file = f"{filename}.tmp.{os.getpid()}"

        try:
            with open(tmp_file, 'w') as f:
                json.dump(data, f, indent=2, allow_nan=False)
                f.flush()
                os.fsync(f.fileno())

            os.replace(tmp_file, filename)

            # Persisti anche il rename sul filesystem quando supportato.
            try:
                dir_fd = os.open(directory, os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
            except OSError:
                pass

        except Exception:
            try:
                if os.path.exists(tmp_file):
                    os.unlink(tmp_file)
            except OSError:
                pass
            raise
    
    def _load_json(self, filename, expected_type):
        """Carica JSON fallendo esplicitamente su assenza/corruzione/schema errato."""
        try:
            with open(filename) as f:
                data = json.load(f)

        except FileNotFoundError as exc:
            raise StatePersistenceError(
                f"Required state file missing: {filename}"
            ) from exc

        except json.JSONDecodeError as exc:
            raise StatePersistenceError(
                f"Invalid JSON state file: {filename}: {exc}"
            ) from exc

        except OSError as exc:
            raise StatePersistenceError(
                f"Unable to read state file: {filename}: {exc}"
            ) from exc

        if not isinstance(data, expected_type):
            raise StatePersistenceError(
                f"Invalid state type for {filename}: "
                f"expected {expected_type.__name__}, "
                f"got {type(data).__name__}"
            )

        return data

if __name__ == "__main__":
    # Test
    print("🧪 Testing Persistence...")
    
    pm = PositionsPersistence()
    
    # Test save positions
    test_pos = {
        'BTC/USDT:USDT': {
            'symbol': 'BTC/USDT:USDT',
            'direction': 'LONG',
            'entry_price': 78000,
            'entry_time': datetime.now(),
            'quantity': 0.001,
            'notional': 78,
            'leverage': 2,
            'stop_loss': 75660,
            'take_profit': 83460,
            'trailing_stop': {
                'enabled': True,
                'activation_price': 81120,
                'trail_distance_pct': 0.02,
                'active': False,
                'current_stop': 75660
            },
            'rr_ratio': 2.33
        }
    }
    
    pm.save_positions(test_pos)
    print("✅ Positions saved")
    
    # Test load
    loaded = pm.load_positions()
    print(f"✅ Positions loaded: {len(loaded)} position(s)")
    
    # Test trade
    test_trade = {
        'symbol': 'BTC/USDT:USDT',
        'direction': 'LONG',
        'entry_price': 78000,
        'exit_price': 80000,
        'entry_time': datetime.now().isoformat(),
        'exit_time': datetime.now().isoformat(),
        'quantity': 0.001,
        'pnl_usd': 2.0,
        'pnl_pct': 0.026,
        'exit_reason': 'TAKE_PROFIT',
        'final_capital': 102.0
    }
    
    pm.save_trade(test_trade)
    print("✅ Trade saved")
    
    trades = pm.load_trades()
    print(f"✅ Total trades: {pm.get_trade_count()}")
    
    print("")
    print("✅ Persistence working!")

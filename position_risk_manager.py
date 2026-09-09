import json
import tempfile
import shutil
import os
import math
from datetime import datetime


class StatePersistenceError(RuntimeError):
    """Errore fatale di persistenza dello stato PAPER."""
    pass


class PositionRiskManager:
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.MAX_POSITIONS = 3
        self.MAX_PORTFOLIO_EXPOSURE = 0.30
        self.MAX_RISK_PER_TRADE = 0.005
        self.MAX_DAILY_LOSS = 0.02
        
        # 🆕 NUOVE CONFIG TRAILING STOP
        self.TRAILING_ACTIVATION_PROFIT = 0.015  # Attiva trailing dopo +1.5%
        self.TRAILING_STOP_DISTANCE = 0.012      # Distanza 1.2% dal massimo
        self.BREAKEVEN_ACTIVATION = 0.01         # Sposta SL a breakeven dopo +1%
        self.TAKE_PROFIT_1 = 0.02                # TP1 a +2%
        self.TAKE_PROFIT_2 = 0.04                # TP2 a +4%

        self.positions_file = 'paper_trading_30d/positions.json'
        self.trades_file = 'paper_trading_30d/trades.json'
        self.portfolio_file = 'paper_trading_30d/portfolio.json'

        # B14: write-ahead journal per transazioni multi-file
        self.transaction_file = 'paper_trading_30d/transaction_pending.json'

        # Se il processo precedente è morto durante un commit,
        # completa il roll-forward PRIMA del load fail-safe B19.
        self._recover_pending_transaction()

        # B19: i file persistenti costituiscono un unico stato logico.
        # Tutti assenti = primo avvio consentito.
        # Solo alcuni presenti = stato incompleto, avvio vietato.
        state_files = [
            self.positions_file,
            self.trades_file,
            self.portfolio_file,
        ]
        existing_state_files = [
            path for path in state_files if os.path.exists(path)
        ]

        if existing_state_files and len(existing_state_files) != len(state_files):
            missing = [
                path for path in state_files if not os.path.exists(path)
            ]
            raise RuntimeError(
                "Persisted state incompleto. "
                f"Presenti: {existing_state_files}; mancanti: {missing}"
            )

        self._fresh_state = not existing_state_files

        # Load existing data
        self.positions = self._load_positions()
        self.trades = self._load_trades()
        saved_capital = self._load_capital()

        if saved_capital is not None:
            self.current_capital = saved_capital
        self.daily_pnl = 0
        self.max_drawdown = 0

    def _validate_position(self, symbol, pos):
        """Valida integrità posizione al caricamento"""
        required = ['entry', 'size', 'side', 'stop_loss']
        for field in required:
            if field not in pos:
                return False, f'Campo mancante: {field}'
        # Validazione numerica: nessuna soglia assoluta sul prezzo.
        # Un asset valido può avere prezzo inferiore a $100.
        for field in ('entry', 'size', 'stop_loss'):
            value = pos[field]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return False, f"{field} non numerico: {value}"
            if not math.isfinite(value) or value <= 0:
                return False, f"{field} invalido: {value}"

        if pos['side'] not in ['BUY', 'SELL']:
            return False, f"Side invalido: {pos['side']}"

        # take_profit è opzionale, ma se presente deve essere valido.
        take_profit = pos.get('take_profit')
        if take_profit is not None:
            if isinstance(take_profit, bool) or not isinstance(take_profit, (int, float)):
                return False, f"Take profit non numerico: {take_profit}"
            if not math.isfinite(take_profit) or take_profit <= 0:
                return False, f"Take profit invalido: {take_profit}"

        return True, 'OK'

    def _fsync_directory(self, directory):
        """Forza su disco anche le modifiche alla directory."""
        flags = os.O_RDONLY
        if hasattr(os, 'O_DIRECTORY'):
            flags |= os.O_DIRECTORY

        fd = os.open(directory, flags)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def _atomic_write_json(self, path, data):
        """Scrive un JSON atomicamente e propaga qualsiasi errore."""
        directory = os.path.dirname(os.path.abspath(path))
        os.makedirs(directory, exist_ok=True)

        fd, tmp_path = tempfile.mkstemp(
            dir=directory,
            prefix='.tmp_state_'
        )

        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())

            os.replace(tmp_path, path)
            self._fsync_directory(directory)

        except Exception as e:
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except OSError:
                pass

            raise StatePersistenceError(
                f"Atomic write fallita per {path}: {e}"
            ) from e

    def _validate_transaction_payload(self, journal):
        """Valida il journal prima di usarlo per il recovery."""
        if not isinstance(journal, dict):
            raise RuntimeError("Transaction journal non è un dict")

        if journal.get('version') != 1:
            raise RuntimeError(
                f"Transaction journal version non valida: "
                f"{journal.get('version')}"
            )

        positions = journal.get('positions')
        trades = journal.get('trades')
        portfolio = journal.get('portfolio')

        if not isinstance(positions, dict):
            raise RuntimeError(
                "Transaction journal: positions non è dict"
            )

        if not isinstance(trades, list):
            raise RuntimeError(
                "Transaction journal: trades non è list"
            )

        if len(trades) > 10000:
            raise RuntimeError(
                f"Transaction journal: troppi trade ({len(trades)})"
            )

        if not isinstance(portfolio, dict):
            raise RuntimeError(
                "Transaction journal: portfolio non è dict"
            )

        for symbol, pos in positions.items():
            if not isinstance(symbol, str) or not symbol:
                raise RuntimeError(
                    f"Transaction journal: symbol invalido {symbol!r}"
                )

            if not isinstance(pos, dict):
                raise RuntimeError(
                    f"Transaction journal: posizione {symbol} non è dict"
                )

            valid, reason = self._validate_position(symbol, pos)
            if not valid:
                raise RuntimeError(
                    f"Transaction journal: posizione {symbol} "
                    f"invalida: {reason}"
                )

        required_trade = (
            'symbol', 'entry', 'exit', 'size',
            'pnl', 'pnl_pct', 'closed_at'
        )

        for index, trade in enumerate(trades):
            if not isinstance(trade, dict):
                raise RuntimeError(
                    f"Transaction journal: trade #{index + 1} non è dict"
                )

            for field in required_trade:
                if field not in trade:
                    raise RuntimeError(
                        f"Transaction journal: trade #{index + 1} "
                        f"manca {field}"
                    )

            for field in ('entry', 'exit', 'size'):
                value = trade[field]
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                    or value <= 0
                ):
                    raise RuntimeError(
                        f"Transaction journal: trade #{index + 1} "
                        f"{field} invalido"
                    )

            for field in ('pnl', 'pnl_pct'):
                value = trade[field]
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                ):
                    raise RuntimeError(
                        f"Transaction journal: trade #{index + 1} "
                        f"{field} invalido"
                    )

            if (
                'side' in trade
                and trade['side'] not in ('BUY', 'SELL')
            ):
                raise RuntimeError(
                    f"Transaction journal: trade #{index + 1} "
                    f"side invalido"
                )

        for field in ('capital', 'initial_capital', 'total_pnl'):
            if field not in portfolio:
                raise RuntimeError(
                    f"Transaction journal: portfolio manca {field}"
                )

            value = portfolio[field]
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise RuntimeError(
                    f"Transaction journal: portfolio {field} invalido"
                )

        capital = float(portfolio['capital'])
        initial = float(portfolio['initial_capital'])
        total = float(portfolio['total_pnl'])

        if capital <= 0 or initial <= 0:
            raise RuntimeError(
                "Transaction journal: capitale non positivo"
            )

        if not math.isclose(
            total,
            capital - initial,
            rel_tol=1e-12,
            abs_tol=1e-9
        ):
            raise RuntimeError(
                "Transaction journal: portfolio aritmeticamente incoerente"
            )

        return positions, trades, portfolio

    def _recover_pending_transaction(self):
        """
        Roll-forward idempotente di una transazione interrotta.

        Journal presente = il commit precedente non è stato
        definitivamente completato.
        """
        if not os.path.exists(self.transaction_file):
            return False

        print(
            "⚠️ B14: transazione incompleta rilevata - "
            "avvio recovery"
        )

        try:
            with open(self.transaction_file, 'r') as f:
                journal = json.load(f)
        except Exception as e:
            raise StatePersistenceError(
                f"Transaction journal illeggibile: {e}"
            ) from e

        positions, trades, portfolio = (
            self._validate_transaction_payload(journal)
        )

        # Roll-forward: operazione idempotente.
        self._atomic_write_json(self.positions_file, positions)
        self._atomic_write_json(self.trades_file, trades)
        self._atomic_write_json(self.portfolio_file, portfolio)

        directory = os.path.dirname(
            os.path.abspath(self.transaction_file)
        )

        try:
            os.unlink(self.transaction_file)
            self._fsync_directory(directory)
        except Exception as e:
            raise StatePersistenceError(
                f"Impossibile finalizzare recovery B14: {e}"
            ) from e

        print("✅ B14: recovery transazione completato")
        return True

    def _commit_state_transaction(
        self,
        positions,
        trades,
        portfolio
    ):
        """
        Commit recuperabile di positions + trades + portfolio.

        1. journal atomicamente
        2. tre file atomicamente
        3. rimozione journal
        """
        if os.path.exists(self.transaction_file):
            raise StatePersistenceError(
                "Esiste già transaction_pending.json: "
                "rifiuto nuovo commit"
            )

        journal = {
            'version': 1,
            'created_at': datetime.now().isoformat(),
            'positions': positions,
            'trades': trades,
            'portfolio': portfolio,
        }

        # Valida prima di toccare qualsiasi file persistente.
        try:
            self._validate_transaction_payload(journal)
        except Exception as e:
            raise StatePersistenceError(
                f"Payload transazione B14 invalido: {e}"
            ) from e

        # WAL: il journal deve esistere PRIMA del primo file dati.
        self._atomic_write_json(
            self.transaction_file,
            journal
        )

        try:
            self._atomic_write_json(
                self.positions_file,
                positions
            )
            self._atomic_write_json(
                self.trades_file,
                trades
            )
            self._atomic_write_json(
                self.portfolio_file,
                portfolio
            )

            directory = os.path.dirname(
                os.path.abspath(self.transaction_file)
            )

            os.unlink(self.transaction_file)
            self._fsync_directory(directory)

        except Exception as e:
            # NON rimuovere il journal:
            # servirà per il roll-forward al prossimo avvio.
            raise StatePersistenceError(
                "Commit stato B14 interrotto. "
                "Journal conservato per recovery: "
                f"{e}"
            ) from e

    def _load_positions(self):
        """Load positions fail-safe"""
        if not os.path.exists(self.positions_file):
            if self._fresh_state:
                return {}
            raise RuntimeError(
                f"File posizioni mancante: {self.positions_file}"
            )

        try:
            with open(self.positions_file, 'r') as f:
                raw = json.load(f)
        except Exception as e:
            raise RuntimeError(
                f"Impossibile leggere {self.positions_file}: {e}"
            ) from e

        if not isinstance(raw, dict):
            raise RuntimeError(
                f"{self.positions_file}: schema invalido, atteso dict "
                f"ma trovato {type(raw).__name__}"
            )

        clean = {}

        for symbol, pos in raw.items():
            if not isinstance(symbol, str) or not symbol:
                raise RuntimeError(
                    f"{self.positions_file}: simbolo posizione invalido: {symbol!r}"
                )

            if not isinstance(pos, dict):
                raise RuntimeError(
                    f"{self.positions_file}: posizione {symbol} non è un dict"
                )

            valid, reason = self._validate_position(symbol, pos)

            if not valid:
                raise RuntimeError(
                    f"{self.positions_file}: posizione {symbol} invalida: {reason}"
                )

            clean[symbol] = pos

        return clean

    def _save_positions(self):
        """Save positions - B14 atomic/fail-fast"""
        self._atomic_write_json(
            self.positions_file,
            self.positions
        )

    def _load_trades(self):
        """Load trade history fail-safe, compatibile con record legacy"""
        if not os.path.exists(self.trades_file):
            if self._fresh_state:
                return []
            raise RuntimeError(
                f"File trade mancante: {self.trades_file}"
            )

        try:
            with open(self.trades_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            raise RuntimeError(
                f"Impossibile leggere {self.trades_file}: {e}"
            ) from e

        if not isinstance(data, list):
            raise RuntimeError(
                f"{self.trades_file}: schema invalido, atteso list "
                f"ma trovato {type(data).__name__}"
            )

        required = (
            'symbol', 'entry', 'exit', 'size',
            'pnl', 'pnl_pct', 'closed_at'
        )

        numeric_positive = ('entry', 'exit', 'size')
        numeric_finite = ('pnl', 'pnl_pct')

        for index, trade in enumerate(data):
            if not isinstance(trade, dict):
                raise RuntimeError(
                    f"{self.trades_file}: trade #{index + 1} non è un dict"
                )

            for field in required:
                if field not in trade:
                    raise RuntimeError(
                        f"{self.trades_file}: trade #{index + 1} "
                        f"manca il campo {field}"
                    )

            symbol = trade['symbol']
            if not isinstance(symbol, str) or not symbol:
                raise RuntimeError(
                    f"{self.trades_file}: trade #{index + 1} "
                    f"symbol invalido: {symbol!r}"
                )

            for field in numeric_positive:
                value = trade[field]
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise RuntimeError(
                        f"{self.trades_file}: trade #{index + 1} "
                        f"{field} non numerico"
                    )
                if not math.isfinite(value) or value <= 0:
                    raise RuntimeError(
                        f"{self.trades_file}: trade #{index + 1} "
                        f"{field} invalido: {value}"
                    )

            for field in numeric_finite:
                value = trade[field]
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise RuntimeError(
                        f"{self.trades_file}: trade #{index + 1} "
                        f"{field} non numerico"
                    )
                if not math.isfinite(value):
                    raise RuntimeError(
                        f"{self.trades_file}: trade #{index + 1} "
                        f"{field} non finito: {value}"
                    )

            closed_at = trade['closed_at']
            if not isinstance(closed_at, str) or not closed_at:
                raise RuntimeError(
                    f"{self.trades_file}: trade #{index + 1} "
                    "closed_at invalido"
                )

            # Compatibilità legacy: i primi trade possono non avere side.
            # Se side esiste, però, deve essere valido.
            if 'side' in trade and trade['side'] not in ('BUY', 'SELL'):
                raise RuntimeError(
                    f"{self.trades_file}: trade #{index + 1} "
                    f"side invalido: {trade['side']}"
                )

        return data

    def _load_capital(self):
        """Load capital from portfolio.json fail-safe"""
        if not os.path.exists(self.portfolio_file):
            if self._fresh_state:
                return None
            raise RuntimeError(
                f"File portfolio mancante: {self.portfolio_file}"
            )

        try:
            with open(self.portfolio_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            raise RuntimeError(
                f"Impossibile leggere {self.portfolio_file}: {e}"
            ) from e

        if not isinstance(data, dict):
            raise RuntimeError(
                f"{self.portfolio_file}: schema invalido, atteso dict "
                f"ma trovato {type(data).__name__}"
            )

        required = ('capital', 'initial_capital', 'total_pnl')

        for field in required:
            if field not in data:
                raise RuntimeError(
                    f"{self.portfolio_file}: campo mancante: {field}"
                )

            value = data[field]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise RuntimeError(
                    f"{self.portfolio_file}: {field} non numerico"
                )

            if not math.isfinite(value):
                raise RuntimeError(
                    f"{self.portfolio_file}: {field} non finito"
                )

        capital = float(data['capital'])
        initial = float(data['initial_capital'])
        total_pnl = float(data['total_pnl'])

        if capital <= 0:
            raise RuntimeError(
                f"{self.portfolio_file}: capital invalido: {capital}"
            )

        if initial <= 0:
            raise RuntimeError(
                f"{self.portfolio_file}: initial_capital invalido: {initial}"
            )

        expected_total = capital - initial

        if not math.isclose(
            total_pnl,
            expected_total,
            rel_tol=1e-12,
            abs_tol=1e-9
        ):
            raise RuntimeError(
                f"{self.portfolio_file}: total_pnl incoerente. "
                f"Salvato={total_pnl}, atteso={expected_total}"
            )

        return capital

    def _save_capital(self):
        """Save capital - B14 atomic/fail-fast"""
        data = {
            'capital': self.current_capital,
            'initial_capital': self.initial_capital,
            'total_pnl': (
                self.current_capital - self.initial_capital
            ),
            'last_updated': datetime.now().isoformat()
        }

        self._atomic_write_json(
            self.portfolio_file,
            data
        )

    def _save_trades(self):
        """Save trade history - B14 atomic/fail-fast"""
        if len(self.trades) > 10000:
            raise RuntimeError(
                f"trades.json anomalo: {len(self.trades)} trade "
                "- possibile loop"
            )

        self._atomic_write_json(
            self.trades_file,
            self.trades
        )

    def can_open_position(self, symbol):
        """Check if can open new position"""
        if len(self.positions) >= self.MAX_POSITIONS:
            return False, f"Max positions reached ({self.MAX_POSITIONS})"

        if symbol in self.positions:
            return False, f"Already have position in {symbol}"

        total_exposure = sum(p['size'] * p['entry'] for p in self.positions.values())
        if total_exposure / self.current_capital > self.MAX_PORTFOLIO_EXPOSURE:
            return False, "Max portfolio exposure reached"

        daily_loss_limit = self.MAX_DAILY_LOSS * self.initial_capital
        if self.daily_pnl <= -daily_loss_limit:
            return False, "Daily loss limit reached"

        return True, "OK"

    def calculate_position_size(self, signal, symbol):
        """Calculate position size from configured risk per trade"""
        risk_amount = self.current_capital * self.MAX_RISK_PER_TRADE

        side = signal.get('signal')
        if side not in ['BUY', 'SELL']:
            return 0

        try:
            entry = float(signal['entry'])
        except (KeyError, TypeError, ValueError):
            return 0

        if not math.isfinite(entry) or entry <= 0:
            return 0

        if side == 'BUY':
            default_stop_loss = entry * 0.97
        else:
            default_stop_loss = entry * 1.03

        try:
            stop_loss = float(
                signal.get('stop_loss', default_stop_loss)
            )
        except (TypeError, ValueError):
            return 0

        if not math.isfinite(stop_loss) or stop_loss <= 0:
            return 0

        risk_per_unit = abs(entry - stop_loss)

        if not math.isfinite(risk_per_unit) or risk_per_unit <= 0:
            return 0

        size = risk_amount / risk_per_unit
        max_position_value = self.current_capital * 0.10
        max_size = max_position_value / entry

        if not math.isfinite(size) or not math.isfinite(max_size):
            return 0

        return min(size, max_size)

    def open_position(self, symbol, signal, size):
        """Open new position"""
        try:
            size = float(size)
        except (TypeError, ValueError):
            return False, "Invalid size"

        if not math.isfinite(size) or size <= 0:
            return False, "Invalid size"

        can_open, reason = self.can_open_position(symbol)
        if not can_open:
            return False, reason

        side = signal.get('signal')
        if side not in ['BUY', 'SELL']:
            return False, f"Invalid side: {side}"

        try:
            entry = float(signal['entry'])
        except (KeyError, TypeError, ValueError):
            return False, "Invalid entry price"

        # B4: niente soglia universale $100.
        # Il prezzo deve semplicemente essere positivo e finito.
        if not math.isfinite(entry) or entry <= 0:
            return False, f"Invalid entry price: {entry}"

        # B6/B7: fallback direction-aware.
        if side == 'BUY':
            default_stop_loss = entry * 0.97
            default_take_profit = entry * (1 + self.TAKE_PROFIT_2)
        else:
            default_stop_loss = entry * 1.03
            default_take_profit = entry * (1 - self.TAKE_PROFIT_2)

        try:
            initial_stop_loss = float(
                signal.get('stop_loss', default_stop_loss)
            )
            take_profit = float(
                signal.get('take_profit', default_take_profit)
            )
        except (TypeError, ValueError):
            return False, "Invalid stop loss/take profit"

        if not math.isfinite(initial_stop_loss) or initial_stop_loss <= 0:
            return False, f"Invalid stop loss: {initial_stop_loss}"

        if not math.isfinite(take_profit) or take_profit <= 0:
            return False, f"Invalid take profit: {take_profit}"

        # B5: geometria obbligatoria al momento dell'apertura.
        if side == 'BUY':
            if initial_stop_loss >= entry:
                return False, (
                    f"Invalid BUY stop loss: SL ${initial_stop_loss:.4f} "
                    f"must be below entry ${entry:.4f}"
                )
            if take_profit <= entry:
                return False, (
                    f"Invalid BUY take profit: TP ${take_profit:.4f} "
                    f"must be above entry ${entry:.4f}"
                )
        else:
            if initial_stop_loss <= entry:
                return False, (
                    f"Invalid SELL stop loss: SL ${initial_stop_loss:.4f} "
                    f"must be above entry ${entry:.4f}"
                )
            if take_profit >= entry:
                return False, (
                    f"Invalid SELL take profit: TP ${take_profit:.4f} "
                    f"must be below entry ${entry:.4f}"
                )

        self.positions[symbol] = {
            'entry': entry,
            'size': size,
            'side': side,
            'stop_loss': initial_stop_loss,
            'take_profit': take_profit,
            'opened_at': datetime.now().isoformat(),
            'highest_price': entry,
            'trailing_active': False,
            'breakeven_activated': False
        }

        self._save_positions()
        return True, f"Position opened: {symbol}"

    def update_trailing_stop(self, symbol, current_price):
        """🆕 NUOVA FUNZIONE: Aggiorna trailing stop dinamicamente - FIX SHORT"""
        if symbol not in self.positions:
            return

        pos = self.positions[symbol]
        entry = pos['entry']
        side = pos.get('side', 'BUY')
        is_long = (side == 'BUY')

        # ✅ FIX: Profit direction-aware
        if is_long:
            current_profit_pct = (current_price - entry) / entry
        else:  # SHORT: profit quando prezzo scende
            current_profit_pct = (entry - current_price) / entry

        # ✅ FIX: Traccia best price (max LONG, min SHORT)
        if is_long:
            if current_price > pos.get('highest_price', entry):
                pos['highest_price'] = current_price
        else:
            if current_price < pos.get('highest_price', entry):
                pos['highest_price'] = current_price

        if not pos.get('breakeven_activated', False) and current_profit_pct >= self.BREAKEVEN_ACTIVATION:
            pos['stop_loss'] = entry
            pos['breakeven_activated'] = True
            print(f"   💚 {symbol}: Breakeven activated (SL moved to entry)")

        elif current_profit_pct >= self.TRAILING_ACTIVATION_PROFIT:
            pos['trailing_active'] = True
            best_price = pos.get('highest_price', current_price)

            if is_long:
                new_stop = best_price * (1 - self.TRAILING_STOP_DISTANCE)
                if new_stop > pos['stop_loss']:
                    pos['stop_loss'] = new_stop
                    print(f"   📈 {symbol}: Trailing stop → ${new_stop:.2f} (from high ${best_price:.2f})")
            else:  # SHORT: stop scende col prezzo
                new_stop = best_price * (1 + self.TRAILING_STOP_DISTANCE)
                if new_stop < pos['stop_loss']:
                    pos['stop_loss'] = new_stop
                    print(f"   📉 {symbol}: Trailing stop → ${new_stop:.2f} (from low ${best_price:.2f})")

        self._save_positions()
    def check_position_exits(self, symbol, current_price):
        print(f"[DEBUG] check_position_exits called for {symbol} at {current_price}")
        """Check if should exit position (con trailing stop)"""
        if symbol not in self.positions:
            return 'HOLD', 'No position'

        pos = self.positions[symbol]
        entry = pos['entry']
        
        self.update_trailing_stop(symbol, current_price)

        side = pos.get('side', 'BUY')
        is_long = (side == 'BUY')

        # ✅ FIX: Stop loss direction-aware (era sempre <= anche per SHORT)
        if pos.get('stop_loss'):
            stop_hit = (current_price <= pos['stop_loss']) if is_long else (current_price >= pos['stop_loss'])
            if stop_hit:
                if pos.get('trailing_active'):
                    return 'EXIT', 'Trailing stop hit'
                elif pos.get('breakeven_activated'):
                    return 'EXIT', 'Breakeven stop hit'
                else:
                    return 'EXIT', 'Hard stop loss hit'

        # ✅ FIX: Take profit direction-aware (era sempre >= anche per SHORT)
        tp1_price = entry * (1 + self.TAKE_PROFIT_1) if is_long else entry * (1 - self.TAKE_PROFIT_1)
        tp1_hit = (current_price >= tp1_price) if is_long else (current_price <= tp1_price)
        if tp1_hit and not pos.get('tp1_hit'):
            pos['tp1_hit'] = True
            self._save_positions()
            print(f"   🎯 {symbol}: TP1 reached (+{self.TAKE_PROFIT_1*100}%)")

        tp2_price = entry * (1 + self.TAKE_PROFIT_2) if is_long else entry * (1 - self.TAKE_PROFIT_2)
        tp2_hit = (current_price >= tp2_price) if is_long else (current_price <= tp2_price)
        if tp2_hit:
            return 'EXIT', 'Take profit 2 reached'

        if pos.get('take_profit'):
            if (current_price >= pos['take_profit'] and is_long) or \
               (current_price <= pos['take_profit'] and not is_long):
                return 'EXIT', 'Target reached'

        return 'HOLD', 'Holding'

    def _classify_exit_reason(self, reason, pnl_pct):
        """Classifica exit reason"""
        reason_lower = reason.lower()
        
        if "trailing stop" in reason_lower:
            return "TRAILING_STOP_PROFIT" if pnl_pct > 0 else "TRAILING_STOP_LOSS"
        elif "breakeven" in reason_lower:
            return "BREAKEVEN_STOP"
        elif "hard stop" in reason_lower or "stop loss" in reason_lower:
            return "HARD_STOP_LOSS"
        elif "take profit" in reason_lower or "target" in reason_lower:
            return "TAKE_PROFIT"
        
        return reason

    def close_position(self, symbol, exit_price, reason):
        """Close position"""
        if symbol not in self.positions:
            return False, "No position to close"

        pos = self.positions[symbol]
        side = pos.get('side', 'BUY')
        is_long = (side == 'BUY')
        if is_long:
            pnl = (exit_price - pos['entry']) * pos['size']
            pnl_pct = ((exit_price - pos['entry']) / pos['entry']) * 100
        else:
            pnl = (pos['entry'] - exit_price) * pos['size']
            pnl_pct = ((pos['entry'] - exit_price) / pos['entry']) * 100
        # 🛡️ WARNING PnL anomalo (solo log)
        if abs(pnl_pct) > 1000:
            import logging
            logging.getLogger('PositionRiskManager').error(
                f"🚨 PnL ANOMALO RILEVATO: {symbol} "
                f"pnl={pnl_pct:.2f}% entry={pos['entry']} exit={exit_price}"
            )

        trade = {
            'symbol': symbol,
            'side': side,
            'entry': pos['entry'],
            'exit': exit_price,
            'size': pos['size'],
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'reason': reason,
            'exit_reason': self._classify_exit_reason(reason, pnl_pct),
            'closed_at': datetime.now().isoformat(),
            'highest_price': pos.get('highest_price', exit_price),
            'trailing_was_active': pos.get('trailing_active', False),
            'breakeven_was_active': pos.get('breakeven_activated', False)
        }

        # B14: costruisci lo stato futuro SENZA modificare
        # ancora lo stato RAM corrente.
        new_trades = list(self.trades)
        new_trades.append(trade)

        new_positions = dict(self.positions)
        del new_positions[symbol]

        new_capital = self.current_capital + pnl
        new_daily_pnl = self.daily_pnl + pnl

        new_portfolio = {
            'capital': new_capital,
            'initial_capital': self.initial_capital,
            'total_pnl': new_capital - self.initial_capital,
            'last_updated': datetime.now().isoformat()
        }

        # Commit recuperabile su disco.
        # Se fallisce, solleva eccezione e conserva il journal.
        self._commit_state_transaction(
            positions=new_positions,
            trades=new_trades,
            portfolio=new_portfolio
        )

        # Solo DOPO commit completato aggiorna la RAM.
        self.positions = new_positions
        self.trades = new_trades
        self.current_capital = new_capital
        self.daily_pnl = new_daily_pnl

        return True, f"Closed with PnL: {pnl_pct:+.2f}%"

    def get_portfolio_metrics(self):
        """Get portfolio metrics"""
        total_pnl = sum(t['pnl'] for t in self.trades)
        winning_trades = [t for t in self.trades if t['pnl'] > 0]

        return {
            'capital': self.current_capital,
            'total_pnl': total_pnl,
            'total_pnl_pct': (total_pnl / self.initial_capital) * 100,
            'daily_pnl': self.daily_pnl,
            'total_trades': len(self.trades),
            'win_rate': (len(winning_trades) / len(self.trades) * 100) if self.trades else 0,
            'max_drawdown': self.max_drawdown,
            'active_positions': len(self.positions)
        }

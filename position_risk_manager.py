import json
import tempfile
import shutil
import os
from datetime import datetime

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

        # Load existing data
        self.positions = self._load_positions()
        self.trades = self._load_trades()
        self.portfolio_file = 'paper_trading_30d/portfolio.json'
        saved_capital = self._load_capital()
        if saved_capital and saved_capital > 0:
            self.current_capital = saved_capital
        self.daily_pnl = 0
        self.max_drawdown = 0

    def _validate_position(self, symbol, pos):
        """Valida integrità posizione al caricamento"""
        required = ['entry', 'size', 'side', 'stop_loss']
        for field in required:
            if field not in pos:
                return False, f'Campo mancante: {field}'
        if pos['entry'] < 100:
            return False, f"Entry anomala: ${pos['entry']}"
        if pos['size'] <= 0:
            return False, f"Size invalida: {pos['size']}"
        if pos['stop_loss'] <= 0:
            return False, f"Stop loss invalido: {pos['stop_loss']}"
        if pos['side'] not in ['BUY', 'SELL']:
            return False, f"Side invalido: {pos['side']}"
        return True, 'OK'

    def _load_positions(self):
        """Load positions from file"""
        if os.path.exists(self.positions_file):
            try:
                with open(self.positions_file, 'r') as f:
                    raw = json.load(f)
                    clean = {}
                    for symbol, pos in raw.items():
                        valid, reason = self._validate_position(symbol, pos)
                        if valid:
                            clean[symbol] = pos
                        else:
                            import logging
                            logging.getLogger('PositionRiskManager').error(
                                f'🚨 POSIZIONE SCARTATA: {symbol} - {reason}'
                            )
                    return clean
            except:
                pass
        return {}

    def _save_positions(self):
        """Save positions to file - ATOMIC WRITE"""
        try:
            os.makedirs('paper_trading_30d', exist_ok=True)
            dir_name = os.path.dirname(os.path.abspath(self.positions_file))
            fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix='.tmp_positions_')
            try:
                with os.fdopen(fd, 'w') as f:
                    json.dump(self.positions, f, indent=2)
                shutil.move(tmp_path, self.positions_file)
            except Exception:
                os.unlink(tmp_path)
                raise
        except Exception as e:
            print(f"Error saving positions: {e}")

    def _load_trades(self):
        """Load trade history"""
        if os.path.exists(self.trades_file):
            try:
                with open(self.trades_file, 'r') as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    import logging
                    logging.getLogger('PositionRiskManager').error(
                        f'🚨 trades.json schema errato: atteso list, trovato {type(data)}'
                    )
                    return []
                return data
            except Exception as e:
                import logging
                logging.getLogger('PositionRiskManager').error(
                    f'❌ Errore caricamento trades.json: {e}'
                )
        return []

    def _load_capital(self):
        """Load capital from portfolio.json"""
        try:
            if os.path.exists(self.portfolio_file):
                with open(self.portfolio_file, 'r') as f:
                    data = json.load(f)
                capital = data.get('capital', 0)
                if capital > 0:
                    return capital
        except:
            pass
        return None

    def _save_capital(self):
        """Save capital to portfolio.json"""
        try:
            os.makedirs('paper_trading_30d', exist_ok=True)
            data = {
                'capital': self.current_capital,
                'initial_capital': self.initial_capital,
                'total_pnl': self.current_capital - self.initial_capital,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.portfolio_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving capital: {e}")

    def _save_trades(self):
        if len(self.trades) > 10000:
            import logging
            logging.getLogger('PositionRiskManager').error(
                f'🚨 trades.json anomalo: {len(self.trades)} trade - possibile loop'
            )
            return
        """Save trade history"""
        try:
            os.makedirs('paper_trading_30d', exist_ok=True)
            with open(self.trades_file, 'w') as f:
                json.dump(self.trades, f, indent=2)
        except Exception as e:
            print(f"Error saving trades: {e}")

    def can_open_position(self, symbol):
        """Check if can open new position"""
        if len(self.positions) >= self.MAX_POSITIONS:
            return False, f"Max positions reached ({self.MAX_POSITIONS})"

        if symbol in self.positions:
            return False, f"Already have position in {symbol}"

        total_exposure = sum(p['size'] * p['entry'] for p in self.positions.values())
        if total_exposure / self.current_capital > self.MAX_PORTFOLIO_EXPOSURE:
            return False, "Max portfolio exposure reached"

        if abs(self.daily_pnl) > self.MAX_DAILY_LOSS * self.initial_capital:
            return False, "Daily loss limit reached"

        return True, "OK"

    def calculate_position_size(self, signal, symbol):
        """Calculate position size using Kelly Criterion"""
        risk_amount = self.current_capital * self.MAX_RISK_PER_TRADE

        entry = signal['entry']
        stop_loss = signal.get('stop_loss', entry * 0.97)
        risk_per_unit = abs(entry - stop_loss)

        if risk_per_unit == 0:
            return 0

        size = risk_amount / risk_per_unit
        max_position_value = self.current_capital * 0.10
        max_size = max_position_value / entry

        return min(size, max_size)

    def open_position(self, symbol, signal, size):
        """Open new position"""
        if size <= 0:
            return False, "Invalid size"

        can_open, reason = self.can_open_position(symbol)
        if not can_open:
            return False, reason

        entry = signal['entry']
        # 🛡️ VALIDAZIONE ENTRY PRICE
        if entry < 100:
            import logging
            logging.getLogger('PositionRiskManager').error(
                f"🚨 ENTRY ANOMALA BLOCCATA: {symbol} entry=${entry}"
            )
            return False, f"Entry anomala bloccata: ${entry}"
        initial_stop_loss = signal.get('stop_loss', entry * 0.97)
        
        self.positions[symbol] = {
            'entry': entry,
            'size': size,
            'side': signal['signal'],
            'stop_loss': initial_stop_loss,
            'take_profit': signal.get('take_profit', entry * (1 + self.TAKE_PROFIT_2)),
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
        pnl = (exit_price - pos['entry']) * pos['size']
        pnl_pct = ((exit_price - pos['entry']) / pos['entry']) * 100
        # 🛡️ WARNING PnL anomalo (solo log)
        if abs(pnl_pct) > 1000:
            import logging
            logging.getLogger('PositionRiskManager').error(
                f"🚨 PnL ANOMALO RILEVATO: {symbol} "
                f"pnl={pnl_pct:.2f}% entry={pos['entry']} exit={exit_price}"
            )

        trade = {
            'symbol': symbol,
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

        self.trades.append(trade)
        self.current_capital += pnl
        self.daily_pnl += pnl
        self._save_capital()

        del self.positions[symbol]

        self._save_positions()
        self._save_trades()

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

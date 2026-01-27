import json
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
        
        self.positions_file = 'paper_trading_30d/positions.json'
        self.trades_file = 'paper_trading_30d/trades.json'
        
        # Load existing data
        self.positions = self._load_positions()
        self.trades = self._load_trades()
        self.daily_pnl = 0
        self.max_drawdown = 0
    
    def _load_positions(self):
        """Load positions from file"""
        if os.path.exists(self.positions_file):
            try:
                with open(self.positions_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_positions(self):
        """Save positions to file"""
        try:
            os.makedirs('paper_trading_30d', exist_ok=True)
            with open(self.positions_file, 'w') as f:
                json.dump(self.positions, f, indent=2)
        except Exception as e:
            print(f"Error saving positions: {e}")
    
    def _load_trades(self):
        """Load trade history"""
        if os.path.exists(self.trades_file):
            try:
                with open(self.trades_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_trades(self):
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
        
        self.positions[symbol] = {
            'entry': signal['entry'],
            'size': size,
            'side': signal['signal'],
            'stop_loss': signal.get('stop_loss'),
            'take_profit': signal.get('take_profit'),
            'opened_at': datetime.now().isoformat()
        }
        
        self._save_positions()
        return True, f"Position opened: {symbol}"
    
    def check_position_exits(self, symbol, current_price):
        """Check if should exit position"""
        if symbol not in self.positions:
            return 'HOLD', 'No position'
        
        pos = self.positions[symbol]
        entry = pos['entry']
        
        # Check stop loss
        if pos.get('stop_loss'):
            if current_price <= pos['stop_loss']:
                return 'EXIT', 'Stop loss hit'
        
        # Check take profit
        if pos.get('take_profit'):
            if current_price >= pos['take_profit']:
                return 'EXIT', 'Target reached'
        
        return 'HOLD', 'Holding'
    
    def _classify_exit_reason(self, reason, pnl_pct):
        """Classifica exit reason"""
        if "stop loss" in reason.lower():
            return "TRAILING_STOP_PROFIT" if pnl_pct > 0 else "HARD_STOP_LOSS"
        elif "target" in reason.lower():
            return "TAKE_PROFIT"
        return reason
    
    def close_position(self, symbol, exit_price, reason):
        """Close position"""
        if symbol not in self.positions:
            return False, "No position to close"
        
        pos = self.positions[symbol]
        pnl = (exit_price - pos['entry']) * pos['size']
        pnl_pct = ((exit_price - pos['entry']) / pos['entry']) * 100
        
        trade = {
            'symbol': symbol,
            'entry': pos['entry'],
            'exit': exit_price,
            'size': pos['size'],
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'reason': reason,
            'exit_reason': self._classify_exit_reason(reason, pnl_pct),
            'closed_at': datetime.now().isoformat()
        }
        
        self.trades.append(trade)
        self.current_capital += pnl
        self.daily_pnl += pnl
        
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

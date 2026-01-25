#!/usr/bin/env python3
"""
Position & Risk Manager - Fixed con exit_reason
"""
import json
import os
from datetime import datetime

class PositionRiskManager:
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.trades = []
        self.daily_pnl = 0
        self.max_drawdown = 0
        
        # Files
        self.positions_file = 'paper_trading_30d/positions.json'
        self.trades_file = 'paper_trading_30d/trades.json'
        
        # Load existing
        self.positions = self._load_positions()
        self.trades = self._load_trades()
        
        # Risk params
        self.MAX_POSITIONS = 5
        self.MAX_RISK_PER_TRADE = 0.005
        self.MAX_PORTFOLIO_EXPOSURE = 0.7
        self.MAX_DAILY_LOSS = 0.03
    
    def _load_positions(self):
        """Load positions from file"""
        try:
            if os.path.exists(self.positions_file):
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
        try:
            if os.path.exists(self.trades_file):
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
        stop = signal.get('stop_loss', entry * 0.98)
        risk_per_unit = abs(entry - stop)
        if risk_per_unit == 0:
            return 0
        size = risk_amount / risk_per_unit
        max_size = (self.current_capital * 0.15) / entry
        return min(size, max_size)
    
    def open_position(self, symbol, entry_price, size):
        """Open new position"""
        self.positions[symbol] = {
            'entry': entry_price,
            'size': size,
            'opened_at': datetime.now().isoformat()
        }
        self._save_positions()
        return True
    
    def _classify_exit_reason(self, reason, pnl_pct):
        """
        Classifica exit reason in modo preciso
        """
        reason_lower = reason.lower()
        
        if "stop loss" in reason_lower or "stop" in reason_lower:
            if pnl_pct > 0:
                return "TRAILING_STOP_PROFIT"
            else:
                return "HARD_STOP_LOSS"
        elif "target" in reason_lower or "profit" in reason_lower:
            return "TAKE_PROFIT"
        else:
            # Mantieni originale se sconosciuto
            return reason
    
    def close_position(self, symbol, exit_price, reason):
        """Close position with proper exit_reason classification"""
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
            'reason': reason,  # Manteniamo per compatibilità
            'exit_reason': self._classify_exit_reason(reason, pnl_pct),  # NUOVO!
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
    
    def update_daily_reset(self):
        """Reset daily counters"""
        self.daily_pnl = 0

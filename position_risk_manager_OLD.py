#!/usr/bin/env python3
"""
Position & Risk Manager
Gestisce sizing, esposizione, limiti
"""

import numpy as np
from datetime import datetime, timedelta

class PositionRiskManager:
    """
    Risk management a livello portfolio
    - Kelly Criterion sizing
    - Max exposure limits
    - Correlation checks
    - Daily loss limits
    """
    
    def __init__(self, initial_capital=1000):
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.positions = {}
        self.daily_pnl = {}
        self.trade_history = []
        
        # RISK LIMITS (NON NEGOZIABILI)
        self.MAX_RISK_PER_TRADE = 0.005  # 0.5% per trade
        self.MAX_DAILY_LOSS = 0.02       # 2% daily loss limit
        self.MAX_POSITIONS = 3           # Max concurrent positions
        self.MAX_PORTFOLIO_EXPOSURE = 0.30  # Max 30% capital deployed
        
    def calculate_position_size(self, signal, symbol, win_rate=None, avg_win=None, avg_loss=None):
        """
        Calcola size ottimale usando Kelly Criterion (half-Kelly)
        """
        
        # Default conservativo
        if win_rate is None or avg_win is None or avg_loss is None:
            # Use fixed 0.5% risk
            risk_amount = self.capital * self.MAX_RISK_PER_TRADE
            
            if 'stop_loss' in signal and 'entry' in signal:
                risk_per_unit = abs(signal['entry'] - signal['stop_loss'])
                size = risk_amount / risk_per_unit if risk_per_unit > 0 else 0
            else:
                # Default 10% of capital
                size = (self.capital * 0.1) / signal['entry']
        
        else:
            # Kelly Criterion
            kelly = (win_rate * avg_win - (1-win_rate) * abs(avg_loss)) / avg_win
            kelly_half = max(kelly * 0.5, 0)  # Half-Kelly più conservativo
            kelly_half = min(kelly_half, 0.1)  # Max 10%
            
            size = (self.capital * kelly_half) / signal['entry']
        
        # Apply limits
        max_position_value = self.capital * self.MAX_PORTFOLIO_EXPOSURE / self.MAX_POSITIONS
        max_size = max_position_value / signal['entry']
        
        return min(size, max_size)
    
    def can_open_position(self, symbol):
        """
        Pre-trade compliance checks
        """
        checks = []
        
        # 1. Check max positions
        if len(self.positions) >= self.MAX_POSITIONS:
            return False, "Max positions limit reached"
        
        # 2. Check daily loss limit
        today = datetime.now().date()
        daily_loss = self.daily_pnl.get(today, 0)
        
        if daily_loss < -self.capital * self.MAX_DAILY_LOSS:
            return False, f"Daily loss limit reached: {daily_loss:.2f}"
        
        # 3. Check total exposure
        total_exposure = sum(
            pos['size'] * pos['entry'] 
            for pos in self.positions.values()
        )
        
        if total_exposure > self.capital * self.MAX_PORTFOLIO_EXPOSURE:
            return False, "Max portfolio exposure reached"
        
        # 4. Check if already have position on this symbol
        if symbol in self.positions:
            return False, "Already have position on this symbol"
        
        return True, "All checks passed"
    
    def open_position(self, symbol, signal, size):
        """
        Open new position with full tracking
        """
        can_open, reason = self.can_open_position(symbol)
        
        if not can_open:
            return False, reason
        
        self.positions[symbol] = {
            'entry': signal['entry'],
            'size': size,
            'stop_loss': signal.get('stop_loss'),
            'take_profit': signal.get('take_profit'),
            'entry_time': datetime.now(),
            'side': signal['signal'],  # BUY or SELL
            'initial_capital': self.capital
        }
        
        return True, "Position opened"
    
    def close_position(self, symbol, exit_price, reason):
        """
        Close position and update metrics
        """
        if symbol not in self.positions:
            return False, "Position not found"
        
        pos = self.positions[symbol]
        
        # Calculate PnL
        if pos['side'] == 'BUY':
            pnl = pos['size'] * (exit_price - pos['entry'])
        else:
            pnl = pos['size'] * (pos['entry'] - exit_price)
        
        pnl_pct = (pnl / (pos['size'] * pos['entry'])) * 100
        
        # Update capital
        self.capital += pnl
        
        # Update daily PnL
        today = datetime.now().date()
        self.daily_pnl[today] = self.daily_pnl.get(today, 0) + pnl
        
        # Record trade
        self.trade_history.append({
            'symbol': symbol,
            'entry': pos['entry'],
            'exit': exit_price,
            'size': pos['size'],
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'duration': (datetime.now() - pos['entry_time']).total_seconds() / 3600,
            'exit_reason': reason,
            'timestamp': datetime.now()
        })
        
        # Remove position
        del self.positions[symbol]
        
        return True, f"Position closed: PnL {pnl:.2f} ({pnl_pct:.2f}%)"
    
    def check_position_exits(self, symbol, current_price):
        """
        Check TP/SL for existing position
        """
        if symbol not in self.positions:
            return None, None
        
        pos = self.positions[symbol]
        
        # Check take profit
        if pos['take_profit']:
            if pos['side'] == 'BUY' and current_price >= pos['take_profit']:
                return 'EXIT', 'Take Profit Hit'
            elif pos['side'] == 'SELL' and current_price <= pos['take_profit']:
                return 'EXIT', 'Take Profit Hit'
        
        # Check stop loss
        if pos['stop_loss']:
            if pos['side'] == 'BUY' and current_price <= pos['stop_loss']:
                return 'EXIT', 'Stop Loss Hit'
            elif pos['side'] == 'SELL' and current_price >= pos['stop_loss']:
                return 'EXIT', 'Stop Loss Hit'
        
        return 'HOLD', None
    
    def get_portfolio_metrics(self):
        """
        Real-time portfolio metrics
        """
        total_pnl = self.capital - self.initial_capital
        total_pnl_pct = (total_pnl / self.initial_capital) * 100
        
        # Calculate max drawdown
        equity_curve = [self.initial_capital]
        running_capital = self.initial_capital
        
        for trade in self.trade_history:
            running_capital += trade['pnl']
            equity_curve.append(running_capital)
        
        peak = equity_curve[0]
        max_dd = 0
        
        for val in equity_curve:
            if val > peak:
                peak = val
            dd = (peak - val) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        # Win rate
        wins = [t for t in self.trade_history if t['pnl'] > 0]
        win_rate = len(wins) / len(self.trade_history) * 100 if self.trade_history else 0
        
        return {
            'capital': self.capital,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'max_drawdown': max_dd,
            'total_trades': len(self.trade_history),
            'win_rate': win_rate,
            'active_positions': len(self.positions),
            'daily_pnl': self.daily_pnl.get(datetime.now().date(), 0)
        }
    
    def get_risk_status(self):
        """
        Risk dashboard
        """
        metrics = self.get_portfolio_metrics()
        
        print("\n" + "="*70)
        print("🛡️  RISK MANAGEMENT STATUS")
        print("="*70)
        
        print(f"\n💰 Capital: ${self.capital:.2f}")
        print(f"   Total PnL: ${metrics['total_pnl']:.2f} ({metrics['total_pnl_pct']:.2f}%)")
        print(f"   Daily PnL: ${metrics['daily_pnl']:.2f}")
        
        print(f"\n📊 Risk Metrics:")
        print(f"   Max Drawdown: {metrics['max_drawdown']:.2f}%")
        print(f"   Active Positions: {metrics['active_positions']}/{self.MAX_POSITIONS}")
        print(f"   Win Rate: {metrics['win_rate']:.1f}%")
        
        # Risk alerts
        print(f"\n⚠️  Risk Alerts:")
        
        today = datetime.now().date()
        daily_loss_pct = (self.daily_pnl.get(today, 0) / self.capital) * 100
        
        if daily_loss_pct < -1.5:
            print(f"   🔴 Daily loss approaching limit: {daily_loss_pct:.2f}%")
        
        if metrics['max_drawdown'] > 15:
            print(f"   🔴 Drawdown elevated: {metrics['max_drawdown']:.2f}%")
        
        if metrics['active_positions'] >= self.MAX_POSITIONS:
            print(f"   🟡 Max positions reached")
        
        if not any([daily_loss_pct < -1.5, metrics['max_drawdown'] > 15, metrics['active_positions'] >= self.MAX_POSITIONS]):
            print("   ✅ All risk parameters healthy")
        
        print("="*70 + "\n")

# Test
if __name__ == "__main__":
    risk_mgr = PositionRiskManager(initial_capital=1000)
    
    # Simulate trade
    signal = {
        'signal': 'BUY',
        'entry': 100,
        'stop_loss': 98,
        'take_profit': 103
    }
    
    size = risk_mgr.calculate_position_size(signal, 'BTC/USDT')
    print(f"Position size calculated: {size:.4f} units")
    
    can_open, reason = risk_mgr.can_open_position('BTC/USDT')
    print(f"Can open: {can_open}, Reason: {reason}")
    
    if can_open:
        risk_mgr.open_position('BTC/USDT', signal, size)
        print("✅ Position opened")
    
    risk_mgr.get_risk_status()


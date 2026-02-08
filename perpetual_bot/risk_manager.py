"""
Risk Manager for Perpetual Bot
"""
import json
from datetime import datetime, timedelta

class RiskManager:
    """Manage position sizing, stops, and risk limits"""
    
    def __init__(self, config_file='perpetual_config.json'):
        with open(config_file) as f:
            self.config = json.load(f)
        
        self.current_capital = self.config['capital']['initial']
        self.daily_pnl = 0
        self.daily_trades = 0
        self.consecutive_losses = 0
        self.last_trade_time = None
        self.cooldown_until = None
    
    def can_open_position(self):
        """Check if bot can open a new position"""
        
        # Check daily loss limit
        daily_loss_limit = self.config['limits']['daily_loss_limit_pct']
        if self.daily_pnl < -self.current_capital * daily_loss_limit:
            return False, f"Daily loss limit hit: {self.daily_pnl:.2f}"
        
        # Check max trades per day
        max_trades = self.config['limits']['max_trades_per_day']
        if self.daily_trades >= max_trades:
            return False, f"Max trades per day reached: {self.daily_trades}/{max_trades}"
        
        # Check cooldown
        if self.cooldown_until and datetime.now() < self.cooldown_until:
            remaining = (self.cooldown_until - datetime.now()).total_seconds() / 3600
            return False, f"In cooldown for {remaining:.1f} more hours"
        
        return True, "OK"
    
    def calculate_position_size(self, signal, leverage=None):
        """
        Calculate position size based on risk per trade
        Returns: (quantity, notional_value, leverage_used)
        """
        if leverage is None:
            leverage = self.config['leverage']['default']
        
        # Max position size as % of capital
        max_size_pct = self.config['position']['max_size_pct']
        max_position_value = self.current_capital * max_size_pct
        
        # Risk-based sizing
        risk_per_trade = self.config['limits']['risk_per_trade_pct']
        risk_amount = self.current_capital * risk_per_trade
        
        # Calculate based on stop loss
        stop_loss_pct = self.config['risk']['stop_loss_pct']
        position_value = risk_amount / stop_loss_pct
        
        # Apply leverage
        position_value_with_leverage = position_value * leverage
        
        # Cap at max size
        final_position_value = min(position_value_with_leverage, max_position_value * leverage)
        
        # Calculate quantity
        entry_price = signal['entry_price']
        quantity = final_position_value / entry_price
        
        return quantity, final_position_value, leverage
    
    def calculate_stops(self, signal, entry_price):
        """
        Calculate stop loss and take profit levels
        Returns: (stop_loss, take_profit, trailing_config)
        """
        direction = signal['direction']
        
        sl_pct = self.config['risk']['stop_loss_pct']
        tp_pct = self.config['risk']['take_profit_pct']
        
        if direction == 'LONG':
            stop_loss = entry_price * (1 - sl_pct)
            take_profit = entry_price * (1 + tp_pct)
        else:  # SHORT
            stop_loss = entry_price * (1 + sl_pct)
            take_profit = entry_price * (1 - tp_pct)
        
        # Trailing stop config
        trailing = {
            'enabled': True,
            'activation_price': entry_price * (1 + self.config['risk']['trailing_stop']['activation_pct']) if direction == 'LONG' 
                               else entry_price * (1 - self.config['risk']['trailing_stop']['activation_pct']),
            'trail_distance_pct': self.config['risk']['trailing_stop']['trail_distance_pct'],
            'active': False,
            'current_stop': stop_loss
        }
        
        return stop_loss, take_profit, trailing
    
    def record_trade(self, pnl, is_win):
        """Record trade result and update stats"""
        self.daily_pnl += pnl
        self.daily_trades += 1
        self.last_trade_time = datetime.now()
        
        if is_win:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            
            # Check if cooldown needed
            max_consec = self.config['limits']['max_consecutive_losses']
            if self.consecutive_losses >= max_consec:
                cooldown_hours = self.config['limits']['cooldown_hours']
                self.cooldown_until = datetime.now() + timedelta(hours=cooldown_hours)
                print(f"⚠️ COOLDOWN ACTIVATED: {cooldown_hours}h after {max_consec} consecutive losses")
    
    def reset_daily_stats(self):
        """Reset daily counters (call at start of new day)"""
        self.daily_pnl = 0
        self.daily_trades = 0
    
    def update_capital(self, new_capital):
        """Update current capital"""
        self.current_capital = new_capital

if __name__ == "__main__":
    # Test risk manager
    print("🧪 TESTING RISK MANAGER...")
    print("")
    
    rm = RiskManager()
    
    # Test position opening
    can_open, reason = rm.can_open_position()
    print(f"✅ Can open position: {can_open} ({reason})")
    
    # Test position sizing
    signal = {
        'direction': 'LONG',
        'entry_price': 78000
    }
    
    qty, value, lev = rm.calculate_position_size(signal)
    print(f"✅ Position size: {qty:.6f} BTC (${value:.2f} @ {lev}x leverage)")
    
    # Test stops
    sl, tp, trail = rm.calculate_stops(signal, 78000)
    print(f"✅ Stop Loss: ${sl:.2f}")
    print(f"✅ Take Profit: ${tp:.2f}")
    print(f"✅ Trailing activation: ${trail['activation_price']:.2f}")
    
    # Test trade recording
    rm.record_trade(-2.0, False)
    rm.record_trade(-1.5, False)
    print(f"✅ Consecutive losses: {rm.consecutive_losses}")
    print(f"✅ Cooldown until: {rm.cooldown_until}")
    
    print("")
    print("✅ Risk manager working!")

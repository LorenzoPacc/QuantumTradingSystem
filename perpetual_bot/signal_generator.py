"""
Signal Generator for Perpetual Bot
"""
import json
from indicators import TechnicalIndicators

class SignalGenerator:
    """Generate LONG/SHORT/NO_TRADE signals"""
    
    def __init__(self, config_file='perpetual_config.json'):
        with open(config_file) as f:
            self.config = json.load(f)
    
    def evaluate(self, df, symbol):
        """
        Main evaluation function
        Returns: (can_trade, direction, signal_dict, reason)
        """
        # Calculate indicators
        ind = TechnicalIndicators.calculate_all(df, self.config)
        
        # Get current values
        price = df['close'].iloc[-1]
        ema_200 = ind['ema_200'].iloc[-1]
        ema_50 = ind['ema_50'].iloc[-1]
        ema_20 = ind['ema_20'].iloc[-1]
        rsi = ind['rsi'].iloc[-1]
        atr_pct = ind['atr_pct'].iloc[-1]
        volume = df['volume'].iloc[-1]
        volume_ma = ind['volume_ma'].iloc[-1]
        
        # Check blockers first
        blocker, reason = self._check_blockers(atr_pct, volume, volume_ma)
        if blocker:
            return False, None, None, reason
        
        # Determine trend (LONG/SHORT/RANGE)
        trend_direction = self._determine_trend(price, ema_200, ema_50)
        
        if trend_direction == 'RANGE':
            return False, None, None, "Market is RANGING - no clear trend"
        
        # Check entry conditions
        can_enter, signal_data = self._check_entry_conditions(
            trend_direction, price, ema_20, rsi, volume, volume_ma
        )
        
        if can_enter:
            signal_data['atr_pct'] = atr_pct
            return True, trend_direction, signal_data, f"{trend_direction} signal confirmed"
        else:
            return False, None, None, f"{trend_direction} trend but entry conditions not met"
    
    def _check_blockers(self, atr_pct, volume, volume_ma):
        """Check if any blocker prevents trading"""
        
        # ATR too high (too volatile)
        max_atr = self.config['blockers']['max_atr_pct']
        if atr_pct > max_atr * 100:  # Convert to percentage
            return True, f"ATR too high: {atr_pct:.2f}% > {max_atr*100:.2f}%"
        
        # Volume too low
        if volume < volume_ma * 0.35:
            return True, f"Volume too low: {volume:.0f} < {volume_ma*0.35:.0f}"
        
        return False, None
    
    def _determine_trend(self, price, ema_200, ema_50):
        """Determine market trend: LONG/SHORT/RANGE"""
        
        # LONG trend
        if price > ema_200 and ema_50 > ema_200:
            # Check strength
            trend_strength = ((ema_50 - ema_200) / ema_200) * 100
            if trend_strength > 1.0:  # At least 1% separation
                return 'LONG'
        
        # SHORT trend
        elif price < ema_200 and ema_50 < ema_200:
            # Check strength
            trend_strength = ((ema_200 - ema_50) / ema_200) * 100
            if trend_strength > 1.0:
                return 'SHORT'
        
        # Otherwise RANGE
        return 'RANGE'
    
    def _check_entry_conditions(self, direction, price, ema_20, rsi, volume, volume_ma):
        """Check if entry conditions are met"""
        
        entry_config = self.config['entry']
        
        # RSI in range
        rsi_min, rsi_max = entry_config['rsi_range']
        if not (rsi_min <= rsi <= rsi_max):
            return False, None
        
        # Volume confirmation
        vol_multiplier = entry_config['volume_multiplier']
        if volume < volume_ma * vol_multiplier:
            return False, None
        
        # Pullback to EMA20
        distance_to_ema20 = abs(price - ema_20) / price
        
        if direction == 'LONG':
            # Want price near or just above EMA20
            if distance_to_ema20 > 0.02:  # More than 2% away
                return False, None
            if price < ema_20 * 0.98:  # Too far below
                return False, None
        
        elif direction == 'SHORT':
            # Want price near or just below EMA20
            if distance_to_ema20 > 0.02:
                return False, None
            if price > ema_20 * 1.02:  # Too far above
                return False, None
        
        # All conditions met - build signal
        signal_data = {
            'symbol': None,  # Will be set by caller
            'direction': direction,
            'entry_price': price,
            'ema_20': ema_20,
            'rsi': rsi,
            'volume_ratio': volume / volume_ma
        }
        
        return True, signal_data

if __name__ == "__main__":
    # Test signal generator
    import ccxt
    import pandas as pd
    
    print("🧪 TESTING SIGNAL GENERATOR...")
    print("")
    
    exchange = ccxt.binance()
    generator = SignalGenerator()
    
    for symbol in ['BTC/USDT', 'ETH/USDT']:
        print(f"📊 {symbol}:")
        ohlcv = exchange.fetch_ohlcv(symbol, '1h', limit=250)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        can_trade, direction, signal, reason = generator.evaluate(df, symbol)
        
        print(f"   Can Trade: {can_trade}")
        print(f"   Direction: {direction}")
        print(f"   Reason: {reason}")
        if signal:
            print(f"   Entry: ${signal['entry_price']:.2f}")
            print(f"   RSI: {signal['rsi']:.2f}")
        print("")
    
    print("✅ Signal generator working!")

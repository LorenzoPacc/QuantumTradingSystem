#!/usr/bin/env python3
"""
Strategia Core: Trend Following 4H
Gira SOLO se Market State = ACTIVE
"""

import ccxt
import numpy as np

class TrendFollowingStrategy:
    """
    Strategia semplice ma robusta:
    1. Trend > EMA200 (4h)
    2. Pullback a EMA20
    3. RSI conferma (40-60)
    4. Volume > media
    """
    
    def __init__(self):
        self.exchange = ccxt.binance()
        self.name = "Trend Following 4H"
    
    def calculate_signal(self, symbol, market_state):
        """
        Genera segnale SOLO se market_state == ACTIVE
        """
        
        # Check prerequisito
        if market_state['state'] != 'ACTIVE':
            return {
                'signal': 'NO_TRADE',
                'reason': f"Market state is {market_state['state']}, not ACTIVE"
            }
        
        # Get data
        candles = self.exchange.fetch_ohlcv(symbol, '4h', limit=200)
        closes = np.array([c[4] for c in candles])
        volumes = np.array([c[5] for c in candles])
        
        # Indicators
        ema20 = self._ema(closes, 20)
        ema200 = self._ema(closes, 200)
        rsi = self._rsi(closes, 14)
        vol_sma = np.mean(volumes[-20:])
        
        current_price = closes[-1]
        
        # LONG Conditions
        long_conditions = [
            current_price > ema200[-1],  # Trend UP
            current_price < ema20[-1] * 1.02,  # Near EMA20 (pullback)
            40 < rsi[-1] < 60,  # RSI neutral zone
            volumes[-1] > vol_sma * 0.8  # Volume OK
        ]
        
        # SHORT Conditions
        short_conditions = [
            current_price < ema200[-1],
            current_price > ema20[-1] * 0.98,
            40 < rsi[-1] < 60,
            volumes[-1] > vol_sma * 0.8
        ]
        
        if all(long_conditions):
            return {
                'signal': 'BUY',
                'confidence': 0.8,
                'entry': current_price,
                'stop_loss': ema20[-1] * 0.98,
                'take_profit': current_price * 1.03,
                'reason': 'Trend UP + Pullback + RSI OK'
            }
        
        elif all(short_conditions):
            return {
                'signal': 'SELL',
                'confidence': 0.8,
                'entry': current_price,
                'stop_loss': ema20[-1] * 1.02,
                'take_profit': current_price * 0.97,
                'reason': 'Trend DOWN + Pullback + RSI OK'
            }
        
        return {
            'signal': 'NO_TRADE',
            'reason': 'Conditions not met',
            'details': {
                'long_score': sum(long_conditions),
                'short_score': sum(short_conditions)
            }
        }
    
    def _ema(self, data, period):
        """EMA calculation"""
        ema = np.zeros_like(data)
        ema[0] = data[0]
        multiplier = 2 / (period + 1)
        
        for i in range(1, len(data)):
            ema[i] = (data[i] * multiplier) + (ema[i-1] * (1 - multiplier))
        
        return ema
    
    def _rsi(self, closes, period=14):
        """RSI calculation"""
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.convolve(gains, np.ones(period)/period, mode='valid')
        avg_loss = np.convolve(losses, np.ones(period)/period, mode='valid')
        
        rs = avg_gain / np.where(avg_loss != 0, avg_loss, 1)
        rsi = 100 - (100 / (1 + rs))
        
        # Pad to match length
        rsi = np.pad(rsi, (len(closes)-len(rsi), 0), constant_values=50)
        
        return rsi

# Test
if __name__ == "__main__":
    from market_state_engine import MarketStateEngine
    
    market_engine = MarketStateEngine()
    strategy = TrendFollowingStrategy()
    
    symbol = 'BTC/USDT'
    
    # 1. Check market state
    market_state = market_engine.calculate_market_state(symbol, '4h')
    market_engine.log_decision(market_state)
    
    # 2. If ACTIVE, check strategy
    signal = strategy.calculate_signal(symbol, market_state)
    
    print(f"\n📈 STRATEGY SIGNAL:")
    print(f"   Signal: {signal['signal']}")
    print(f"   Reason: {signal['reason']}")
    if 'entry' in signal:
        print(f"   Entry: {signal['entry']:.2f}")
        print(f"   TP: {signal['take_profit']:.2f}")
        print(f"   SL: {signal['stop_loss']:.2f}")


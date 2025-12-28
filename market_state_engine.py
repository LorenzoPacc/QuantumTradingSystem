#!/usr/bin/env python3
"""Market State Engine - Decide SE il mercato è tradabile"""

import ccxt
import numpy as np
from datetime import datetime

class MarketStateEngine:
    def __init__(self):
        self.exchange = ccxt.binance()
        self.state_history = []
    
    def calculate_market_state(self, symbol='BTC/USDT', timeframe='4h'):
        candles = self.exchange.fetch_ohlcv(symbol, timeframe, limit=50)
        closes = np.array([c[4] for c in candles])
        highs = np.array([c[2] for c in candles])
        lows = np.array([c[3] for c in candles])
        volumes = np.array([c[5] for c in candles])
        
        # ATR
        tr = np.maximum(highs[1:] - lows[1:], np.maximum(abs(highs[1:] - closes[:-1]), abs(lows[1:] - closes[:-1])))
        atr = np.mean(tr[-14:])
        atr_pct = (atr / closes[-1]) * 100
        
        # Trend
        sma20 = np.mean(closes[-20:])
        sma50 = np.mean(closes[-50:]) if len(closes) >= 50 else np.mean(closes)
        trend_diff = ((sma20 - sma50) / sma50) * 100
        
        # Volume
        vol_sma = np.mean(volumes[-20:])
        vol_ratio = volumes[-1] / vol_sma if vol_sma > 0 else 1.0
        
        # Returns - FIX: usa solo le ultime 19 per evitare shape mismatch
        recent_closes = closes[-20:]
        returns = np.diff(recent_closes) / recent_closes[:-1]
        returns_std = np.std(returns) * 100
        
        # DECISION
        state = "UNKNOWN"
        confidence = 0.0
        reasons = []
        
        if atr_pct < 0.5:
            state = "DEAD"
            confidence = 0.9
            reasons.append(f"ATR too low: {atr_pct:.2f}%")
        elif atr_pct > 5.0:
            state = "CRISIS"
            confidence = 0.9
            reasons.append(f"ATR too high: {atr_pct:.2f}%")
        elif abs(trend_diff) < 1.0 and atr_pct < 2.0:
            state = "RANGE"
            confidence = 0.7
            reasons.append(f"No trend: {trend_diff:.2f}%")
        elif abs(trend_diff) > 2.0 and 0.8 < atr_pct < 4.0:
            state = "ACTIVE"
            confidence = 0.8
            reasons.append(f"Clear trend: {trend_diff:.2f}%")
        else:
            state = "RANGE"
            confidence = 0.5
            reasons.append("Mixed signals")
        
        result = {
            'state': state,
            'confidence': confidence,
            'metrics': {'atr_pct': atr_pct, 'trend_diff': trend_diff, 'vol_ratio': vol_ratio, 'returns_std': returns_std},
            'reasons': reasons,
            'timestamp': datetime.now()
        }
        
        self.state_history.append(result)
        return result
    
    def should_strategy_run(self, state_result):
        if state_result['state'] == 'ACTIVE':
            return True, "Market is active and tradeable"
        elif state_result['state'] == 'RANGE':
            return False, "Market is ranging"
        elif state_result['state'] == 'DEAD':
            return False, "Market is dead"
        elif state_result['state'] == 'CRISIS':
            return False, "Market in crisis"
        return False, "Unknown market state"
    
    def get_current_state(self):
        if self.state_history:
            return self.state_history[-1]
        return None
    
    def log_decision(self, state_result):
        print(f"\n{'='*70}")
        print(f"🌍 MARKET STATE: {state_result['state']} ({state_result['confidence']*100:.0f}%)")
        print(f"📊 ATR: {state_result['metrics']['atr_pct']:.2f}% | Trend: {state_result['metrics']['trend_diff']:.2f}%")
        can_trade, reason = self.should_strategy_run(state_result)
        print(f"🎯 {'✅ TRADE ALLOWED' if can_trade else '❌ NO TRADE'}: {reason}")
        print(f"{'='*70}\n")

if __name__ == "__main__":
    engine = MarketStateEngine()
    for sym in ['BTC/USDT', 'ETH/USDT']:
        state = engine.calculate_market_state(sym, '4h')
        engine.log_decision(state)
        import time; time.sleep(1)

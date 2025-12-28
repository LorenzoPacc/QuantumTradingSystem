#!/usr/bin/env python3
"""
Test strategia SEMPLIFICATA
Mean reversion su RSI 4h
"""

import ccxt
import time
from datetime import datetime

class SimpleStrategy:
    def __init__(self):
        self.exchange = ccxt.binance()
        self.position = None
        self.entry_price = 0
        
    def get_rsi(self, symbol, timeframe='4h', periods=14):
        """Calcola RSI"""
        candles = self.exchange.fetch_ohlcv(symbol, timeframe, limit=periods+1)
        closes = [c[4] for c in candles]
        
        gains = []
        losses = []
        
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-periods:]) / periods
        avg_loss = sum(losses[-periods:]) / periods
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def check_signal(self, symbol):
        """Signal semplice: RSI < 30 = BUY, RSI > 70 = SELL"""
        rsi = self.get_rsi(symbol, '4h')
        
        print(f"{symbol} RSI 4h: {rsi:.1f}")
        
        if rsi < 30 and not self.position:
            return "BUY"
        elif rsi > 70 and self.position:
            return "SELL"
        elif self.position:
            # Check TP/SL
            current_price = self.exchange.fetch_ticker(symbol)['last']
            pnl_pct = ((current_price - self.entry_price) / self.entry_price) * 100
            
            if pnl_pct >= 3.0:  # TP 3%
                return "SELL"
            elif pnl_pct <= -2.0:  # SL 2%
                return "SELL"
        
        return "HOLD"
    
    def run_test(self, symbols, cycles=5):
        """Test semplice per N cicli"""
        print("🧪 Test Strategia Semplificata")
        print("="*60)
        
        for cycle in range(cycles):
            print(f"\nCycle {cycle+1}/{cycles} - {datetime.now()}")
            
            for symbol in symbols:
                signal = self.check_signal(symbol)
                print(f"  {symbol}: {signal}")
            
            time.sleep(120)  # 2 minuti
        
        print("\n✅ Test completato")

# Run test
if __name__ == "__main__":
    strategy = SimpleStrategy()
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    strategy.run_test(symbols, cycles=3)

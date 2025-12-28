#!/usr/bin/env python3
import ccxt
import time
from datetime import datetime

exchange = ccxt.binance()

def get_rsi(symbol, tf='4h'):
    candles = exchange.fetch_ohlcv(symbol, tf, limit=15)
    closes = [c[4] for c in candles]
    
    gains, losses = [], []
    for i in range(1, len(closes)):
        change = closes[i] - closes[i-1]
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))
    
    avg_gain = sum(gains[-14:]) / 14
    avg_loss = sum(losses[-14:]) / 14
    
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

print("🧪 SIMPLE RSI STRATEGY TEST (10 min)")
print("="*60)

symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'AVAX/USDT']

for cycle in range(5):  # 5 cicli x 2min = 10min
    print(f"\n🔄 Cycle {cycle+1}/5 - {datetime.now().strftime('%H:%M:%S')}")
    
    for sym in symbols:
        try:
            rsi = get_rsi(sym, '4h')
            ticker = exchange.fetch_ticker(sym)
            price = ticker['last']
            
            signal = "HOLD"
            if rsi < 30:
                signal = "🟢 BUY"
            elif rsi > 70:
                signal = "🔴 SELL"
            
            print(f"  {sym:12} RSI:{rsi:5.1f} Price:{price:8.2f} → {signal}")
        except Exception as e:
            print(f"  {sym:12} ERROR: {e}")
    
    if cycle < 4:
        time.sleep(120)

print("\n✅ Test completato")

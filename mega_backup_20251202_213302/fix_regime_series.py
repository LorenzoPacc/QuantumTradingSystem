#!/usr/bin/env python3
"""
Fix per Series ambiguity in regime_detection
"""

with open('regime_detection.py', 'r') as f:
    content = f.read()

# Fix 1: ADX comparison
content = content.replace(
    'if adx > 25',
    'if float(adx) > 25'
)

# Fix 2: ATR comparison
content = content.replace(
    'if atr > atr_mean',
    'if float(atr) > float(atr_mean)'
)

content = content.replace(
    'if atr < atr_mean',
    'if float(atr) < float(atr_mean)'
)

# Fix 3: RSI comparison
content = content.replace(
    'if fear_greed < 25 and rsi < 35',
    'if fear_greed < 25 and float(rsi) < 35'
)

# Fix 4: Price vs EMA
content = content.replace(
    'if current_price < ema_20 < ema_50',
    'if float(current_price) < float(ema_20) < float(ema_50)'
)

content = content.replace(
    'if current_price > ema_20 > ema_50',
    'if float(current_price) > float(ema_20) > float(ema_50)'
)

# Salva
with open('regime_detection.py', 'w') as f:
    f.write(content)

print("✅ Fix Series ambiguity applicato a regime_detection.py")

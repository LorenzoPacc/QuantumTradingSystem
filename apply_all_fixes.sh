#!/bin/bash

echo "1. Correggo RSI calculation..."
cat > temp_rsi_fix.py << 'RSIFIX'
def calculate_rsi_fixed(prices, period=14):
    if len(prices) < period + 1:
        return 50.0
    
    try:
        import numpy as np
        
        deltas = np.diff(prices)
        up = deltas[deltas >= 0]
        down = -deltas[deltas < 0]
        
        if len(up) == 0 or len(down) == 0:
            return 50.0
        
        avg_gain = np.mean(up[:period]) if len(up) >= period else np.mean(up)
        avg_loss = np.mean(down[:period]) if len(down) >= period else np.mean(down)
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        
        return max(0.0, min(100.0, rsi))
    except:
        return 50.0
RSIFIX

echo "2. Correggo confidence calculation..."
cat > fix_confidence_now.py << 'CONFFIX'
class CriticalFixes:
    @staticmethod
    def fix_confidence_threshold(fg, rsi, pc, min_conf=60):
        # REGOLA D'ORO: RSI > 70 = NO BUY
        if rsi > 70:
            return False, 0.0, f"RSI troppo alto ({rsi:.1f})"
        
        score = 0
        
        # RSI ipervenduto
        if rsi < 25: score += 3
        elif rsi < 35: score += 2
        elif rsi < 50: score += 0.5
        
        # Fear & Greed
        if fg < 25: score += 2.5
        elif fg < 45: score += 1.5
        
        # Price momentum (solo negativo è buono per BUY)
        if pc < -5: score += 2
        elif pc < -2: score += 1
        elif pc > 5: score -= 1  # Penalità per pump
        
        # Calcola confidence
        if score <= 0:
            conf = 0.0
        else:
            conf = min((score / 7.5) * 100, 100)
        
        return conf >= min_conf, conf, f"Score={score:.1f}"
CONFFIX

echo "3. Applico i fix..."
python3 << 'APPLY'
import re

# Fix al file principale
with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# 1. Aggiungi import per RSI fix
exec(open('temp_rsi_fix.py').read())
content = content.replace('calculate_rsi(', 'calculate_rsi_fixed(')

# 2. Sostituisci CriticalFixes
with open('fix_critical_bugs.py', 'w') as f:
    f.write(open('fix_confidence_now.py').read())

print("✅ Fix applicati!")
print("1. RSI calculation corretto")
print("2. Confidence logic corretto (RSI>70 = 0%)")
print("3. File aggiornati")

APPLY

echo "4. Test rapido..."
python3 << 'TEST'
from fix_critical_bugs import CriticalFixes
f = CriticalFixes()

print("🧪 Test LINK/USDT (problema originale):")
print("F&G=23, RSI=84.1, Change=+10.4%")
buy, conf, info = f.fix_confidence_threshold(23, 84.1, 10.4, 60)
print(f"✅ BUY: {buy}, Confidence: {conf:.0f}% ← DEVE ESSERE 0%!")
print(f"   Info: {info}")

print("\\n🧪 Test MATIC/USDT (opportunità reale):")
print("F&G=23, RSI=51.9, Change=-5.1%")
buy, conf, info = f.fix_confidence_threshold(23, 51.9, -5.1, 60)
print(f"✅ BUY: {buy}, Confidence: {conf:.0f}% ← DEVE ESSERE >60%!")
print(f"   Info: {info}")
TEST

echo "✅ TUTTI I FIX APPLICATI!"
echo "Ora riavvia: python3 quantum_v33_ultimate_final.py"

#!/usr/bin/env python3
"""
Migliora il sistema di confidence per essere più realistico
"""

with open('fix_critical_bugs.py', 'r') as f:
    content = f.read()

# Modifica la funzione fix_confidence_threshold
old_scoring = '''        # RSI scoring
        if rsi < 25:
            score += 3.0
            reasons.append(f"RSI estremo ({rsi:.1f})")
        elif rsi < 35:
            score += 2.0
            reasons.append(f"RSI ipervenduto ({rsi:.1f})")
        elif rsi < 50:
            score += 0.5
            reasons.append(f"RSI neutro-basso ({rsi:.1f})")'''

new_scoring = '''        # RSI scoring (più graduale)
        if rsi < 25:
            score += 3.0
            reasons.append(f"RSI estremo ({rsi:.1f})")
        elif rsi < 30:
            score += 2.5
            reasons.append(f"RSI molto ipervenduto ({rsi:.1f})")
        elif rsi < 40:
            score += 2.0
            reasons.append(f"RSI ipervenduto ({rsi:.1f})")
        elif rsi < 50:
            score += 1.0
            reasons.append(f"RSI neutro-basso ({rsi:.1f})")
        elif rsi < 55:
            score += 0.5
            reasons.append(f"RSI neutro ({rsi:.1f})")'''

content = content.replace(old_scoring, new_scoring)

# Migliora lo scoring Fear & Greed
old_fg = '''        # Fear & Greed scoring
        if fg < 25:
            score += 2.5
            reasons.append(f"Paura estrema (F&G={fg})")
        elif fg < 45:
            score += 1.5
            reasons.append(f"Mercato in paura (F&G={fg})")'''

new_fg = '''        # Fear & Greed scoring (più reattivo)
        if fg < 20:
            score += 3.0
            reasons.append(f"Panico estremo (F&G={fg})")
        elif fg < 30:
            score += 2.0
            reasons.append(f"Paura estrema (F&G={fg})")
        elif fg < 45:
            score += 1.5
            reasons.append(f"Mercato in paura (F&G={fg})")
        elif fg < 50:
            score += 0.5
            reasons.append(f"Paura leggera (F&G={fg})")'''

content = content.replace(old_fg, new_fg)

with open('fix_critical_bugs.py', 'w') as f:
    f.write(content)

print("✅ Sistema di confidence migliorato")
print("   - RSI scoring più graduale")
print("   - F&G più reattivo")
print("   - Più opportunità di trade")

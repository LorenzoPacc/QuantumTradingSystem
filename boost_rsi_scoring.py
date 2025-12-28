#!/usr/bin/env python3

with open('fix_critical_bugs.py', 'r') as f:
    content = f.read()

# Aumenta il punteggio per RSI < 50
old_rsi = '''        elif rsi < 50:
            score += 1.0
            reasons.append(f"RSI neutro-basso ({rsi:.1f})")'''

new_rsi = '''        elif rsi < 50:
            score += 1.5
            reasons.append(f"RSI neutro-basso ({rsi:.1f})")'''

if old_rsi in content:
    content = content.replace(old_rsi, new_rsi)
    
    with open('fix_critical_bugs.py', 'w') as f:
        f.write(content)
    
    print("✅ RSI < 50 ora dà 1.5 punti invece di 1.0")
    print("   Confidence passerà da ~40% a ~50%")
else:
    print("⚠️ Pattern non trovato")
    print("Cerco varianti...")
    if 'rsi < 50' in content:
        print("✓ Trovato 'rsi < 50' nel codice")

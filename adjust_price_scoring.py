#!/usr/bin/env python3
"""
Aggiusta lo scoring per i price change in contesto di paura
"""

with open('fix_critical_bugs.py', 'r') as f:
    content = f.read()

# Trova e migliora lo scoring del price change
old_price = '''        # Price change scoring
        if pc < -5:
            score += 2.0
            reasons.append(f"Forte correzione ({pc:.1f}%)")
        elif pc < -2:
            score += 1.0
            reasons.append(f"Correzione ({pc:.1f}%)")
        elif pc > 5:
            score -= 1.0
            reasons.append(f"Pump eccessivo (+{pc:.1f}%)")'''

new_price = '''        # Price change scoring (più permissivo in paura)
        if pc < -5:
            score += 2.5
            reasons.append(f"Forte correzione ({pc:.1f}%)")
        elif pc < -2:
            score += 1.5
            reasons.append(f"Correzione ({pc:.1f}%)")
        elif pc < 0:
            score += 0.5
            reasons.append(f"Leggera correzione ({pc:.1f}%)")
        elif pc < 3:
            # Pump leggero OK in paura estrema
            if fg < 35:
                score += 0.5
                reasons.append(f"Pump moderato in paura (+{pc:.1f}%)")
            # Altrimenti neutro (no penalty, no bonus)
        elif pc > 8:
            score -= 1.5
            reasons.append(f"Pump eccessivo (+{pc:.1f}%)")
        elif pc > 5:
            score -= 0.5
            reasons.append(f"Pump elevato (+{pc:.1f}%)")'''

if old_price in content:
    content = content.replace(old_price, new_price)
    
    with open('fix_critical_bugs.py', 'w') as f:
        f.write(content)
    
    print("✅ Price scoring aggiustato")
    print("   - Pump < 3% in paura estrema ora dà bonus")
    print("   - Correzioni danno più punti")
else:
    print("⚠️ Pattern non trovato esattamente")
    print("\nContenuto attuale price scoring:")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'Price change scoring' in line:
            for j in range(10):
                if i+j < len(lines):
                    print(lines[i+j])
            break

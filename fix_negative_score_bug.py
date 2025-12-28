#!/usr/bin/env python3
"""
FIX CRITICO: Score negativo non deve mai essere BUY
"""

with open('fix_critical_bugs.py', 'r') as f:
    content = f.read()

# Trova la riga che calcola confidence
old_confidence_calc = '''        # Calcola confidence (normalizzata su score massimo 11)
        confidence = min(abs(score) / 11 * 100, 100)
        score_info = f"Score: {score:.1f} | {' | '.join(reasons)}"
        
        return confidence >= min_confidence, confidence, score_info'''

# Nuova logica: score negativo = automaticamente NO
new_confidence_calc = '''        # Calcola confidence (normalizzata su score massimo 11)
        confidence = min(abs(score) / 11 * 100, 100)
        score_info = f"Score: {score:.1f} | {' | '.join(reasons)}"
        
        # ✅ FIX CRITICO: Score negativo = NO TRADE (condizioni pessime)
        if score < 0:
            return False, confidence, score_info + " [NEGATIVE SCORE - NO TRADE]"
        
        return confidence >= min_confidence, confidence, score_info'''

if old_confidence_calc in content:
    content = content.replace(old_confidence_calc, new_confidence_calc)
    
    with open('fix_critical_bugs.py', 'w') as f:
        f.write(content)
    
    print("✅ FIX APPLICATO: Score negativo → NO TRADE")
else:
    print("⚠️  Pattern non trovato, applico fix alternativo...")
    
    # Cerca solo "return confidence >="
    if 'return confidence >= min_confidence, confidence, score_info' in content:
        content = content.replace(
            'return confidence >= min_confidence, confidence, score_info',
            '''# ✅ Score negativo = NO TRADE
        if score < 0:
            return False, confidence, score_info + " [NEGATIVE]"
        return confidence >= min_confidence, confidence, score_info'''
        )
        
        with open('fix_critical_bugs.py', 'w') as f:
            f.write(content)
        
        print("✅ Fix alternativo applicato")


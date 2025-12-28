#!/usr/bin/env python3
"""
Aumenta i pesi per raggiungere 60%+ confidence in condizioni buone
"""

with open('fix_critical_bugs.py', 'r') as f:
    content = f.read()

# Vecchia formula con pesi bassi
old_formula = '''    def fix_confidence_threshold(fear_greed, rsi, price_change, min_confidence=60.0):
        score = 0.0
        if rsi < 25:
            score += 3
        elif rsi < 35:
            score += 2
        elif rsi > 80:
            score -= 3
        elif rsi > 70:
            score -= 2
        if fear_greed < 25:
            score += 2.5
        elif fear_greed < 45:
            score += 1.5
        elif fear_greed > 75:
            score -= 2.5
        if price_change < -5:
            score += 2
        elif price_change < -2:
            score += 1
        confidence = min(abs(score) / 10 * 100, 100)
        return confidence >= min_confidence, confidence, f"Score: {score}"'''

# Nuova formula con pesi aumentati
new_formula = '''    def fix_confidence_threshold(fear_greed, rsi, price_change, min_confidence=60.0):
        score = 0.0
        reasons = []
        
        # RSI (peso aumentato)
        if rsi < 25:
            score += 4
            reasons.append(f"RSI estremo ({rsi:.0f})")
        elif rsi < 35:
            score += 3
            reasons.append(f"RSI ipervenduto ({rsi:.0f})")
        elif rsi < 55:
            score += 2
            reasons.append(f"RSI neutro-basso ({rsi:.0f})")
        elif rsi > 80:
            score -= 4
            reasons.append(f"RSI estremo alto ({rsi:.0f})")
        elif rsi > 70:
            score -= 3
            reasons.append(f"RSI ipercomprato ({rsi:.0f})")
        
        # Fear & Greed (peso aumentato)
        if fear_greed < 25:
            score += 4
            reasons.append(f"Paura estrema ({fear_greed})")
        elif fear_greed < 45:
            score += 2.5
            reasons.append(f"Paura ({fear_greed})")
        elif fear_greed > 75:
            score -= 4
            reasons.append(f"Euforia ({fear_greed})")
        elif fear_greed > 60:
            score -= 2
            reasons.append(f"Greed ({fear_greed})")
        
        # Price momentum (peso aumentato)
        if price_change < -5:
            score += 3
            reasons.append(f"Forte calo ({price_change:.1f}%)")
        elif price_change < -2:
            score += 2
            reasons.append(f"Correzione ({price_change:.1f}%)")
        elif price_change > 10:
            score -= 3
            reasons.append(f"Pump eccessivo ({price_change:.1f}%)")
        elif price_change > 5:
            score -= 2
            reasons.append(f"Forte rialzo ({price_change:.1f}%)")
        
        # Calcola confidence (normalizzata su score massimo 11)
        confidence = min(abs(score) / 11 * 100, 100)
        score_info = f"Score: {score:.1f} | {' | '.join(reasons)}"
        
        return confidence >= min_confidence, confidence, score_info'''

if old_formula in content:
    content = content.replace(old_formula, new_formula)
    
    with open('fix_critical_bugs.py', 'w') as f:
        f.write(content)
    
    print("✅ Pesi aumentati in fix_critical_bugs.py")
    print("\n📊 CAMBIAMENTI:")
    print("   RSI < 35: 2 → 3 punti")
    print("   RSI < 55: 0 → 2 punti (nuovo)")
    print("   F&G < 25: 2.5 → 4 punti")
    print("   F&G < 45: 1.5 → 2.5 punti")
    print("   Price < -5: 2 → 3 punti")
    print("   Price < -2: 1 → 2 punti")
    print("\n🎯 Max score: 10 → 11")
else:
    print("❌ Pattern non trovato, applico fix manuale...")
    
    # Fix alternativo: sovrascrivi tutto il metodo
    import_line = content.find('class CriticalFixes:')
    if import_line != -1:
        # Trova fix_confidence_threshold
        method_start = content.find('def fix_confidence_threshold', import_line)
        if method_start != -1:
            # Trova fine metodo (prossimo @staticmethod o fine classe)
            method_end = content.find('@staticmethod', method_start + 1)
            if method_end == -1:
                method_end = content.find('\n\nclass ', method_start)
            if method_end == -1:
                method_end = len(content)
            
            # Sostituisci
            indent = '    '
            new_method_full = f'''{indent}@staticmethod
{new_formula}
    
'''
            content = content[:method_start-5] + new_method_full + content[method_end:]
            
            with open('fix_critical_bugs.py', 'w') as f:
                f.write(content)
            
            print("✅ Metodo sostituito completamente")


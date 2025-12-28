import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Trova funzione check_buy
start = content.find('def check_buy')
end = content.find('def check_sell', start)

if start != -1 and end != -1:
    func = content[start:end]
    
    # Estrai solo le parti importanti
    lines = func.split('\n')
    important = []
    
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in [
            'Fear & Greed', 'fix_confidence_threshold', 
            'should_trade', 'confidence >=', 'if confidence <',
            'return True', 'return False'
        ]):
            important.append(f"{i+1}: {line}")
    
    print("📝 STRUTTURA SEMPLIFICATA CHECK_BUY:")
    print("="*50)
    for line in important[:15]:  # Mostra prime 15 righe importanti
        print(line)
    
    # Verifica ordine
    print("\n✅ ORDINE VERIFICATO:")
    has_fear_bonus = 'Fear & Greed' in func
    has_fix_call = 'fix_confidence_threshold' in func
    fear_bonus_pos = func.find('Fear & Greed')
    fix_call_pos = func.find('fix_confidence_threshold')
    
    if has_fear_bonus and has_fix_call:
        if fear_bonus_pos < fix_call_pos:
            print("  ✅ Fear Bonus PRIMA di fix_confidence_threshold ✓")
        else:
            print("  ❌ Fear Bonus DOPO fix_confidence_threshold")
    else:
        print("  ⚠️  Componenti mancanti")
else:
    print("❌ Funzione check_buy non trovata")

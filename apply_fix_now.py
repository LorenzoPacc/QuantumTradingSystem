#!/usr/bin/env python3
"""Fix immediato per l'errore del parametro fear_greed"""

import re

print("🔧 APPLICAZIONE FIX IMMEDIATO...")

# 1. Leggi il file fix_critical_bugs.py
with open('fix_critical_bugs.py', 'r') as f:
    fixes_content = f.read()

# 2. Trova la definizione della funzione e modifica la signature
old_signature = r'def fix_confidence_threshold\(fg: int = None,'
new_signature = 'def fix_confidence_threshold(fg: int = None, fear_greed: int = None,'

if re.search(old_signature, fixes_content):
    # Modifica la signature
    fixes_content = re.sub(old_signature, new_signature, fixes_content)
    
    # Aggiungi la compatibilità all'inizio della funzione
    # Trova la prima linea dopo la docstring
    pattern = r'(def fix_confidence_threshold.*?\n.*?""".*?""")\n'
    replacement = r'\1\n        # Supporta sia fg che fear_greed\n        if fear_greed is not None and fg is None:\n            fg = fear_greed\n'
    
    fixes_content = re.sub(pattern, replacement, fixes_content, flags=re.DOTALL)
    
    # Salva il file modificato
    with open('fix_critical_bugs.py', 'w') as f:
        f.write(fixes_content)
    
    print("✅ fix_critical_bugs.py aggiornato con supporto per 'fear_greed'")
else:
    print("⚠️ Signature non trovata, applico fix alternativo...")
    
    # Alternativa: modifica direttamente il bot
    with open('quantum_v33_ultimate_final.py', 'r') as f:
        bot_content = f.read()
    
    # Sostituisci fear_greed= con fg=
    bot_content = bot_content.replace('fear_greed=', 'fg=')
    
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.write(bot_content)
    
    print("✅ Bot aggiornato: 'fear_greed=' → 'fg='")

# 3. Test rapido
print("\n🧪 TEST DEL FIX...")
try:
    from fix_critical_bugs import CriticalFixes
    fixes = CriticalFixes()
    
    # Test con fear_greed
    result = fixes.fix_confidence_threshold(
        fear_greed=23, 
        rsi=84.8, 
        price_change=10.8, 
        min_confidence=60
    )
    print(f"✅ Test con fear_greed: BUY={result[0]}, Conf={result[1]:.0f}%")
    
    # Test con fg
    result = fixes.fix_confidence_threshold(
        fg=23, 
        rsi=51.9, 
        price_change=-5.1, 
        min_confidence=60
    )
    print(f"✅ Test con fg: BUY={result[0]}, Conf={result[1]:.0f}%")
    
    print("\n🎉 FIX APPLICATO CON SUCCESSO!")
    
except Exception as e:
    print(f"❌ Errore: {e}")

print("\n🚀 Ora puoi riavviare il bot:")
print("pkill -f quantum_v33 && python3 quantum_v33_ultimate_final.py")

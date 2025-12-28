import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

print("🔧 Aggiungo debug dettagliato...")

# Trova la linea con il check modificato
for i, line in enumerate(lines):
    if 'if should_trade or confidence >= 45.0:' in line:
        print(f"✅ Trovato check modificato a riga {i+1}")
        
        # Aggiungi logging PRIMA del check
        debug_before = '''        # DEBUG: Values before decision
        logging.debug(f"DEBUG_PRE_DECISION: {symbol} - should_trade={should_trade}, confidence={confidence:.2f}%, threshold_check={confidence >= 45.0}")
        
'''
        lines.insert(i, debug_before)
        print(f"✅ Aggiunto debug logging a riga {i+1}")
        break

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(lines)

print("🎉 Debug logging aggiunto!")
print("Ora vedremo i valori REALI di should_trade e confidence")

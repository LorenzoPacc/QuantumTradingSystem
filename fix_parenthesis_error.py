import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

print("🔧 Correggo errore parentesi...")

# Trova le righe problematiche (945-955)
for i in range(945, 955):
    if i < len(lines):
        if 'EXTREME_GREED"' in lines[i] and not lines[i].strip().endswith(')'):
            print(f"✅ Trovata riga {i+1} con EXTREME_GREED")
            # Aggiungi parentesi chiusa alla riga corretta
            if ')' not in lines[i]:
                lines[i] = lines[i].rstrip() + ')\n'
                print(f"✅ Aggiunta parentesi ) a riga {i+1}")
        
        # Rimuovi parentesi extra dopo fix_confidence_threshold
        if lines[i].strip() == ')' and 'fix_confidence_threshold' in lines[i-2]:
            print(f"❌ Trovata parentesi extra a riga {i+1} - Rimuovo")
            lines[i] = '        '  # Sostituisci con spazio vuoto

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(lines)

print("✅ Correzione parentesi applicata")

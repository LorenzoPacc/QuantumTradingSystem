import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

print("🔧 Modifica logica di acquisto...")

# Trova la sezione da modificare
for i, line in enumerate(lines):
    if 'if should_trade:' in line:
        print(f"✅ Trovato 'if should_trade:' a riga {i+1}")
        
        # Modifica: Se should_trade è True OPPURE confidence è alta
        lines[i] = '        # Modified: Accept high confidence even if should_trade=False\n' + \
                   '        if should_trade or confidence >= 45.0:  # 45% min for auto-buy\n'
        
        print(f"✅ Modificato riga {i+1}: Ora accetta confidence >=45%")
        break

# Scrivi il file modificato
with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(lines)

print("🎉 Logica di acquisto modificata!")
print("   Ora accetta: should_trade=True OPPURE confidence >=45%")

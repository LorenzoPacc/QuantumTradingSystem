with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

print("🔧 Sistemazione indentazione finale...")

# Trova l'inizio del blocco Fear Bonus
fear_start = -1
for i, line in enumerate(lines):
    if '# 🚀 FEAR BONUS SIMPLE' in line:
        fear_start = i
        break

if fear_start != -1:
    print(f"✅ Trovato Fear Bonus a linea {fear_start+1}")
    
    # Le prossime linee devono avere indentazione corretta
    # Dovrebbero essere 8 spazi (dentro check_buy che è dentro la classe)
    expected_indent = '        '  # 8 spazi
    
    # Correggi le prossime 10 linee
    for i in range(fear_start, fear_start + 15):
        if i < len(lines):
            line = lines[i]
            if line.strip():  # Se non è vuota
                # Deve iniziare con 8 spazi
                if not line.startswith(expected_indent) and line.strip():
                    # Rimuovi spazi esistenti e aggiungi 8 spazi
                    lines[i] = expected_indent + line.lstrip()
                    print(f"   Linea {i+1} corretta")
            # Se è una linea vuota, lasciala com'è

# Scrivi il file corretto
with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(lines)

print("✅ Indentazione sistemata")

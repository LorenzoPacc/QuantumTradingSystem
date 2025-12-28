import re

print("🔧 Correggo indentazione completa funzione check_buy...")

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Trova la funzione check_buy
start = content.find('    def check_buy(self, symbol):')
if start == -1:
    # Prova senza indentazione
    start = content.find('def check_buy(self, symbol):')

if start == -1:
    print("❌ Funzione check_buy non trovata")
    exit()

print(f"✅ Trovata funzione check_buy a posizione {start}")

# Trova la fine della funzione (prima def check_sell successiva)
end = content.find('def check_sell', start)
if end == -1:
    print("❌ Fine funzione non trovata")
    exit()

# Estrai la funzione
func = content[start:end]
print(f"📏 Lunghezza funzione: {len(func)} caratteri")

# La funzione dovrebbe iniziare con 8 spazi (doppia indentazione)
# Perché è dentro una classe
expected_indent = '    '  # 4 spazi per essere dentro def check_buy
current_first_line = func.split('\n')[0]

if not current_first_line.startswith('    def check_buy'):
    print(f"⚠️  Prima linea: '{current_first_line}'")
    print("   Aggiungo 4 spazi di indentazione a tutta la funzione...")
    
    # Aggiungi 4 spazi a ogni linea della funzione
    lines = func.split('\n')
    indented_lines = []
    for line in lines:
        if line.strip():  # Se non è linea vuota
            indented_lines.append('    ' + line)
        else:
            indented_lines.append(line)
    
    func = '\n'.join(indented_lines)
    print("✅ Indentazione aggiunta")
else:
    print("✅ Funzione già indentata correttamente")

# Sostituisci nel contenuto
new_content = content[:start] + func + content[end:]

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.write(new_content)

print("🎉 Indentazione corretta applicata!")
print("Ora la funzione dovrebbe essere dentro la classe correttamente")

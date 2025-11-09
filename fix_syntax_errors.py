import re

print("🔧 Fixing syntax errors in quantum_ultimate_fixed.py...")

# Leggi il file
with open('quantum_ultimate_fixed.py', 'r') as f:
    content = f.read()

# Fix 1: Rimuovi escape sequences errate
content = content.replace('\\$', '$')
content = content.replace('\\n\\n', '\n\n')
content = content.replace('\\n', '\n')

# Fix 2: Trova e correggi la riga problematica
# Cerca pattern tipo: \n\ndef execute_trading_cycle
content = re.sub(r'\\n\\ndef\s+execute_trading_cycle', '\n\n    def execute_trading_cycle', content)

# Salva il file corretto
with open('quantum_ultimate_fixed.py', 'w') as f:
    f.write(content)

print("✅ File corretto!")

# Verifica
with open('quantum_ultimate_fixed.py', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'def execute_trading_cycle' in line:
            print(f"✅ execute_trading_cycle trovato alla riga {i+1}")
            break


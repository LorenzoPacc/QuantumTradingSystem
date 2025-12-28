import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

print("🔄 Correzione ULTIMATIVA indentazione...")

new_lines = []
in_check_buy = False
check_buy_start = -1

for i, line in enumerate(lines):
    if i == 632:  # Linea 633 (0-based index)
        # Questa deve essere: "    def check_buy(self, symbol):"
        if 'def check_buy' in line:
            # Correggi l'indentazione
            new_lines.append('    def check_buy(self, symbol):\n')
            check_buy_start = i
            in_check_buy = True
        else:
            new_lines.append(line)
    elif i > 632 and in_check_buy:
        # Le linee dentro check_buy devono avere 8 spazi
        if line.strip() == '':
            new_lines.append(line)
        elif line.strip().startswith('def check_sell'):
            # Fine della funzione check_buy
            in_check_buy = False
            new_lines.append(line)
        else:
            # Aggiungi 8 spazi se non li ha già
            if not line.startswith('        '):
                new_lines.append('        ' + line.lstrip())
            else:
                new_lines.append(line)
    else:
        new_lines.append(line)

# Scrivi il file corretto
with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(new_lines)

print("✅ File riscritto con indentazione corretta!")

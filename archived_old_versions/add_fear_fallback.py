#!/usr/bin/env python3

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Trova def check_buy_signal
for i, line in enumerate(lines):
    if 'def check_buy_signal' in line:
        # Trova la prima riga di codice dopo la def
        j = i + 1
        while j < len(lines) and (lines[j].strip() == '' or lines[j].strip().startswith('"""') or lines[j].strip().startswith('#')):
            j += 1
        
        # Inserisci fallback
        indent = '        '  # 8 spazi
        fallback = f'{indent}if fear_index is None:\n{indent}    fear_index = self.get_fear_greed_index()\n'
        lines.insert(j, fallback)
        break

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(lines)

print("✅ Aggiunto fallback per fear_index in check_buy_signal")

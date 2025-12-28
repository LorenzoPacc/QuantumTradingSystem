#!/usr/bin/env python3
"""
Fix per passare fear_index al check_buy_signal
"""

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Trova dove viene chiamato check_buy_signal e aggiungi fear_index come parametro
# Pattern da cercare: self.check_buy_signal(symbol, ...)

import re

# Cerca tutte le chiamate a check_buy_signal
pattern = r'self\.check_buy_signal\(([^)]+)\)'

def add_fear_param(match):
    params = match.group(1)
    # Se fear_index non è già nei parametri
    if 'fear_index' not in params and 'fear_greed' not in params:
        return f'self.check_buy_signal({params}, fear_index)'
    return match.group(0)

content = re.sub(pattern, add_fear_param, content)

# Salva
with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.write(content)

print("✅ Aggiunto fear_index alle chiamate check_buy_signal")

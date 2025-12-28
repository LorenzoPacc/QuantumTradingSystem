#!/usr/bin/env python3
"""
Aggiunge fear_index all'inizio di check_buy
"""

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Trova def check_buy
for i, line in enumerate(lines):
    if 'def check_buy(self, symbol):' in line:
        print(f"✅ Trovato check_buy alla riga {i+1}")
        
        # Trova la prima riga di codice (dopo la def)
        # Dovrebbe essere la prima riga con if len(self.state["positions"])
        j = i + 1
        
        # Inserisci subito dopo la def, prima di qualsiasi altro codice
        indent = '        '
        fear_line = f'{indent}fear_index = getattr(self, "fear_index", self.get_fear_greed_index())\n'
        
        lines.insert(j, fear_line)
        print(f"✅ Aggiunto fear_index alla riga {j+1}")
        break

# Salva
with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(lines)

print("\n🎯 Fix completato! fear_index ora definito in check_buy")

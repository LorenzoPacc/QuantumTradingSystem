#!/usr/bin/env python3
"""
Sposta la definizione di fear_greed prima del regime report
"""

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Trova la riga con fear_index = self.get_fear_greed_index()
fear_greed_line = None
fear_greed_idx = None

for i, line in enumerate(lines):
    if 'fear_index = self.get_fear_greed_index()' in line:
        fear_greed_line = line
        fear_greed_idx = i
        print(f"✅ Trovato fear_index alla riga {i+1}")
        break

if fear_greed_idx is None:
    print("❌ Non trovato fear_index definition")
    exit(1)

# Trova il try block del regime report (prima di fear_greed_idx)
try_block_start = None
for i in range(fear_greed_idx - 1, max(0, fear_greed_idx - 50), -1):
    if 'try:' in lines[i] and 'regime' in ''.join(lines[i:i+10]).lower():
        try_block_start = i
        print(f"✅ Trovato try block alla riga {i+1}")
        break

if try_block_start is None:
    print("⚠️  Try block non trovato, cerco comunque di spostare fear_greed")
    # Fallback: sposta fear_greed 30 righe prima
    try_block_start = fear_greed_idx - 30

# Sposta fear_index prima del try block
# Rimuovi dalla posizione originale
fear_line_to_move = lines.pop(fear_greed_idx)

# Inserisci prima del try block
lines.insert(try_block_start, fear_line_to_move)

# Aggiungi anche fear_greed = fear_index subito dopo
lines.insert(try_block_start + 1, '        fear_greed = fear_index  # Alias per compatibilità\n')

# Salva
with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(lines)

print("\n🎯 Fix applicato!")
print(f"✅ fear_index spostato dalla riga {fear_greed_idx+1} alla riga {try_block_start+1}")
print("✅ Aggiunto alias fear_greed = fear_index")

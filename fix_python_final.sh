#!/bin/bash
echo "🔧 FIX PYTHON FINALE..."

cp quantum_v33_ultimate_final.py quantum_backup_python.py

python3 << 'PYEND'
with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Split in righe
lines = content.split('\n')

# 1. Fix riga 679 (indice 678)
if '...' in lines[678]:
    lines[678] = "        should_trade, confidence, score_info = self.fixes.fix_confidence_threshold("
    lines.insert(679, "            symbol=symbol,")
    lines.insert(680, "            fg=fear_index,")
    lines.insert(681, "            rsi=rsi,")
    lines.insert(682, "            price_change=price_change_24h,")
    lines.insert(683, "            min_confidence=45.0")
    lines.insert(684, "        )")

# 2. Trova e mantieni SOLO il primo blocco FEAR BONUS
new_lines = []
i = 0
fear_bonus_count = 0

while i < len(lines):
    line = lines[i]
    
    # Detecta inizio FEAR BONUS
    if '# 🚀 FEAR BONUS' in line:
        fear_bonus_count += 1
        
        if fear_bonus_count == 1:
            # Mantieni primo blocco (8 righe)
            for j in range(8):
                if i+j < len(lines):
                    new_lines.append(lines[i+j])
            i += 8
        else:
            # Salta blocchi duplicati
            # Cerca fine blocco (fino a print con 📊 o elif/if non indentato)
            while i < len(lines):
                if ('print(f"📊' in lines[i] or 
                    (lines[i].strip().startswith('if ') and not lines[i].startswith('            '))):
                    break
                i += 1
    else:
        new_lines.append(line)
        i += 1

# Scrivi
with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.write('\n'.join(new_lines))

print("✅ Fix applicato!")
PYEND

echo ""
echo "🔍 Verifica 675-700..."
sed -n '675,700p' quantum_v33_ultimate_final.py

echo ""
echo "🧪 Test..."
python3 -m py_compile quantum_v33_ultimate_final.py

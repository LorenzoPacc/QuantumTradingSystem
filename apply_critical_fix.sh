#!/bin/bash
echo "🔧 APPLICAZIONE FIX DEFINITIVO..."

# Backup sicurezza
cp quantum_v33_ultimate_final.py quantum_v33_before_fix.py

# FIX COMPLETO
python3 << 'PYTHON'
with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# 1. FIX RIGA 679 - Aggiungi parametri corretti
for i in range(len(lines)):
    if i == 678 and '...' in lines[i]:  # riga 679 (indice 678)
        lines[i] = """        should_trade, confidence, score_info = self.fixes.fix_confidence_threshold(
            symbol=symbol,
            fg=fear_index,
            rsi=rsi,
            price_change=price_change_24h,
            min_confidence=45.0
        )
"""

# 2. RIMUOVI DUPLICATI FEAR BONUS (righe 682-710)
# Trova la prima occorrenza e rimuovi le successive
new_lines = []
fear_bonus_found = False
skip_until = -1

for i, line in enumerate(lines):
    if i < skip_until:
        continue
    
    # Trova inizio blocco FEAR BONUS
    if '# 🚀 FEAR BONUS FIXED' in line and not fear_bonus_found:
        fear_bonus_found = True
        new_lines.append(line)
        # Aggiungi le prossime 7 righe (il blocco completo)
        for j in range(1, 8):
            if i+j < len(lines):
                new_lines.append(lines[i+j])
        skip_until = i + 8
    elif '# 🚀 FEAR BONUS FIXED' in line and fear_bonus_found:
        # Salta questo blocco duplicato (8 righe)
        skip_until = i + 8
        continue
    elif i >= skip_until:
        new_lines.append(line)

# 3. FIX RIGA 738 - Rimuovi riga orfana `fg=fear_index,`
final_lines = []
for i, line in enumerate(new_lines):
    # Salta la riga orfana che inizia con spazi e "fg=fear_index,"
    if line.strip().startswith('fg=fear_index,'):
        continue
    final_lines.append(line)

# Scrivi file corretto
with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(final_lines)

print("✅ Fix applicato!")
PYTHON

# Test sintassi
echo ""
echo "🔍 TEST SINTASSI..."
python3 -m py_compile quantum_v33_ultimate_final.py

if [ $? -eq 0 ]; then
    echo "✅ SINTASSI OK!"
    echo ""
    echo "📊 VERIFICA RIGHE 675-720:"
    sed -n '675,720p' quantum_v33_ultimate_final.py
else
    echo "❌ Errore ancora presente"
    echo "🔙 Ripristino backup..."
    cp quantum_v33_before_fix.py quantum_v33_ultimate_final.py
fi

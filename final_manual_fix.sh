#!/bin/bash
echo "🔧 FIX MANUALE DEFINITIVO..."

cp quantum_v33_ultimate_final.py quantum_backup_manual_final.py

# Sostituisci righe 686-696 con il blocco corretto
python3 << 'PYEND'
with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Sostituisci righe 685-695 (indici 684-694)
# Rimuovi tutto da riga 686 (# 🚀 FEAR BONUS) fino a riga con )
new_lines = lines[:685]  # Tutto prima di FEAR BONUS

# Aggiungi blocco FEAR BONUS corretto
new_lines.append("        # 🚀 FEAR BONUS FIXED\n")
new_lines.append("        if fear_index < 30:  # EXTREME FEAR\n")
new_lines.append("            confidence = confidence * 1.25\n")
new_lines.append("            print(f\"🚀 FEAR BONUS APPLIED: +25% (F&G: {fear_index})\")\n")
new_lines.append("        elif fear_index < 45:  # FEAR\n")
new_lines.append("            confidence = confidence * 1.15\n")
new_lines.append("            print(f\"📈 FEAR BONUS APPLIED: +15% (F&G: {fear_index})\")\n")

# Trova dove ripartire (dopo la ) orfana)
start_again = None
for i in range(685, min(700, len(lines))):
    if 'if should_trade:' in lines[i]:
        start_again = i
        break

if start_again:
    new_lines.extend(lines[start_again:])
    print(f"✅ Ripartito dalla riga {start_again+1}")
else:
    print("❌ Non trovato 'if should_trade:'")
    exit(1)

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Fix applicato!")
PYEND

echo ""
echo "🔍 Verifica 680-700..."
sed -n '680,700p' quantum_v33_ultimate_final.py

echo ""
echo "🧪 Test sintassi..."
python3 -m py_compile quantum_v33_ultimate_final.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉🎉🎉 FINALMENTE FATTO! 🎉🎉🎉"
    echo ""
    echo "✅ quantum_v33_ultimate_final.py è pronto!"
else
    echo ""
    echo "❌ Errore:"
    python3 -m py_compile quantum_v33_ultimate_final.py 2>&1
fi

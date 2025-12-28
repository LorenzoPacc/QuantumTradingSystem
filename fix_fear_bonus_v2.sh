#!/bin/bash

FILE="quantum_v33_ultimate_final.py"

echo "🔧 FIX FEAR BONUS v2 IN CORSO..."

# 1️⃣ Rimuove eventuali fear bonus rotti
sed -i '/# 🚀 FEAR BONUS SIMPLE/,+10d' "$FILE"

# 2️⃣ Chiude la parentesi nel fix_confidence_threshold se manca
sed -i 's/self.fixes.fix_confidence_threshold(/self.fixes.fix_confidence_threshold(/' "$FILE"

# Controlla se la riga successiva contiene ')'
LINE_NUM=$(grep -n "fix_confidence_threshold(" "$FILE" | cut -d: -f1 | head -1)
NEXT_LINE=$((LINE_NUM+1))
LINE_CONTENT=$(sed -n "${NEXT_LINE}p" "$FILE")

if ! echo "$LINE_CONTENT" | grep -q ")"; then
    echo "➡️ Aggiungo parentesi mancante..."
    sed -i "${LINE_NUM}s/$/ )/" "$FILE"
fi

# 3️⃣ Inserisce Fear Bonus corretto dopo la chiusura
sed -i "/fix_confidence_threshold(/a\
        # 🚀 FEAR BONUS SIMPLE\n\
        if fear_index < 30:\n\
            confidence = confidence * 1.25\n\
            print(f\"🚀 FEAR BONUS APPLIED: +25% (F&G: {fear_index})\")\n\
        elif fear_index < 45:\n\
            confidence = confidence * 1.15\n\
            print(f\"📈 FEAR BONUS APPLIED: +15% (F&G: {fear_index})\")\n" "$FILE"

echo "🔍 CONTROLLO SINTASSI..."
if python3 -m py_compile "$FILE"; then
    echo "🎉 SINTASSI OK — FIX COMPLETO!"
else
    echo "❌ C'È ANCORA UN ERRORE — MOSTRA 20 RIGHE VICINE"
    sed -n "$((LINE_NUM-5)),$((LINE_NUM+20))p" "$FILE"
fi


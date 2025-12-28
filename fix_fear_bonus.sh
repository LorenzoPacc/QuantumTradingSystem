#!/bin/bash

FILE="quantum_v33_ultimate_final.py"

echo "🔧 FIX FEAR BONUS IN CORSO..."

# Rimuove il blocco rotto (quello con la parentesi aperta)
sed -i '/# 🚀 FEAR BONUS SIMPLE/,+5d' "$FILE"

# Inserisce il blocco corretto subito dopo la riga con fix_confidence_threshold
sed -i '/fix_confidence_threshold(/a\
\
        # 🚀 FEAR BONUS SIMPLE\n\
        if fear_index < 30:  # EXTREME FEAR\n\
            confidence = confidence * 1.25\n\
            print(f"🚀 FEAR BONUS APPLIED: +25% (F&G: {fear_index})")\n\
        elif fear_index < 45:  # FEAR\n\
            confidence = confidence * 1.15\n\
            print(f"📈 FEAR BONUS APPLIED: +15% (F&G: {fear_index})")\n\
' "$FILE"

echo "✅ FIX COMPLETATO!"

echo "🔍 CONTROLLO SINTASSI..."
python3 -m py_compile "$FILE" && echo "🎉 SINTASSI OK — BOT PRONTO!" || echo "❌ C'È ANCORA UN ERRORE"

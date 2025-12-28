#!/bin/bash

echo "🔧 FIX FINALE FEAR BONUS..."

FILE="quantum_v33_ultimate_final.py"

# 1. Rimuove il blocco rotto attuale
sed -i '/# 🚀 FEAR BONUS SIMPLE/,+5d' "$FILE"

# 2. Chiude correttamente la riga con "(" aperta
sed -i 's/fix_confidence_threshold(.*/fix_confidence_threshold(...)/' "$FILE"

# 3. Inserisce Fear Bonus corretto
sed -i '/fix_confidence_threshold(...)/a \
        # 🚀 FEAR BONUS FIXED\n\
        if fear_index < 30:  # EXTREME FEAR\n\
            confidence = confidence * 1.25\n\
            print(f"🚀 FEAR BONUS APPLIED: +25% (F&G: {fear_index})")\n\
        elif fear_index < 45:  # FEAR\n\
            confidence = confidence * 1.15\n\
            print(f"📈 FEAR BONUS APPLIED: +15% (F&G: {fear_index})")\n\
' "$FILE"

echo "🔍 Test sintassi..."
python3 -m py_compile "$FILE" && echo "🎉 FIX OK!" || echo "❌ Errore ancora presente"

#!/bin/bash
echo "🔧 AGGIUNGI IF MANCANTE..."

cp quantum_v33_ultimate_final.py quantum_backup_missing_if.py

# Inserisci "if fear_index < 30:  # EXTREME FEAR" dopo riga 685
sed -i '685a\        if fear_index < 30:  # EXTREME FEAR' quantum_v33_ultimate_final.py

echo "✅ IF aggiunto!"
echo ""
echo "🔍 Verifica 683-695..."
sed -n '683,695p' quantum_v33_ultimate_final.py

echo ""
echo "🧪 Test..."
python3 -m py_compile quantum_v33_ultimate_final.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 FUNZIONA!"
    echo ""
    echo "🚀 Avvia: python3 quantum_v33_ultimate_final.py"
else
    echo ""
    echo "❌ Errore:"
    python3 quantum_v33_ultimate_final.py 2>&1 | head -5
fi

#!/bin/bash
echo "🔨 FIX DRASTICO..."

cp quantum_v33_ultimate_final.py quantum_backup_drastic.py

# Rimuovi TUTTE le righe da 695 a 733 (tutti i duplicati)
sed -i '695,733d' quantum_v33_ultimate_final.py

echo "✅ Righe 695-733 eliminate!"
echo ""
echo "🔍 Verifica 680-700..."
sed -n '680,700p' quantum_v33_ultimate_final.py

echo ""
echo "🧪 Test sintassi..."
python3 -m py_compile quantum_v33_ultimate_final.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 FINALMENTE! 🎉"
    echo ""
    echo "📊 Struttura finale FEAR BONUS (righe 686-693):"
    sed -n '686,693p' quantum_v33_ultimate_final.py
else
    echo ""
    echo "❌ Errore:"
    python3 -m py_compile quantum_v33_ultimate_final.py 2>&1
    echo ""
    echo "📋 Mostra righe 690-710:"
    sed -n '690,710p' quantum_v33_ultimate_final.py
fi

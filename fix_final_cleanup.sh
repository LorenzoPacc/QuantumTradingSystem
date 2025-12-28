#!/bin/bash
echo "🔧 CLEANUP FINALE..."

cp quantum_v33_ultimate_final.py quantum_backup_cleanup.py

# Rimuovi righe 729-731 (duplicato + orfani)
sed -i '729,731d' quantum_v33_ultimate_final.py

echo "✅ Cleanup completato!"
echo ""
echo "🔍 Verifica 720-740..."
sed -n '720,740p' quantum_v33_ultimate_final.py

echo ""
echo "🧪 Test sintassi..."
python3 -m py_compile quantum_v33_ultimate_final.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉🎉🎉 SUCCESSO COMPLETO! 🎉🎉🎉"
    echo ""
    echo "✅ File quantum_v33_ultimate_final.py è pronto!"
    echo ""
    echo "🚀 Puoi avviare il bot con:"
    echo "   python3 quantum_v33_ultimate_final.py"
else
    echo ""
    echo "❌ Errore:"
    python3 -m py_compile quantum_v33_ultimate_final.py 2>&1
fi

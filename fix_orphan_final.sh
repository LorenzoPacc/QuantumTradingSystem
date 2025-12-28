#!/bin/bash
echo "🔧 RIMOZIONE RIGHE ORFANE..."

cp quantum_v33_ultimate_final.py quantum_backup_final.py

# Rimuovi righe 738-742 (gli argomenti orfani)
sed -i '738,742d' quantum_v33_ultimate_final.py

echo "✅ Righe 738-742 rimosse!"
echo ""
echo "🔍 Verifica 730-745..."
sed -n '730,745p' quantum_v33_ultimate_final.py

echo ""
echo "🧪 Test sintassi..."
python3 -m py_compile quantum_v33_ultimate_final.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESSO TOTALE!"
    echo ""
    echo "📊 Riepilogo fix applicati:"
    echo "✅ Riga 679: fix_confidence_threshold con parametri corretti"
    echo "✅ Righe 682-689: FEAR BONUS (duplicati rimossi)"
    echo "✅ Righe 738-742: Argomenti orfani rimossi"
else
    echo ""
    echo "❌ Errore rimanente:"
    python3 -m py_compile quantum_v33_ultimate_final.py 2>&1
fi

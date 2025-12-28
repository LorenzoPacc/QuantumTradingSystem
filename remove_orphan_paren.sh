#!/bin/bash
echo "🔧 RIMUOVI ) ORFANA..."

cp quantum_v33_ultimate_final.py quantum_backup_paren.py

# La riga 691 ha "elif fear_index < 45:  # FEAR" senza corpo
# La riga 692 ha ")" orfana
# Aggiungi corpo elif e rimuovi )

# Opzione 1: Completa elif
sed -i '691a\            confidence = confidence * 1.15\n            print(f"📈 FEAR BONUS APPLIED: +15% (F&G: {fear_index})")' quantum_v33_ultimate_final.py

# Opzione 2: Rimuovi la ) orfana (ora sarà riga 694)
sed -i '694d' quantum_v33_ultimate_final.py

echo "✅ Fix applicato!"
echo ""
echo "🔍 Verifica 686-700..."
sed -n '686,700p' quantum_v33_ultimate_final.py

echo ""
echo "🧪 Test..."
python3 -m py_compile quantum_v33_ultimate_final.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 FUNZIONA!"
else
    echo ""
    echo "❌ Errore:"
    python3 -m py_compile quantum_v33_ultimate_final.py 2>&1
fi

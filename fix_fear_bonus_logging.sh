#!/bin/bash
echo "🔧 FIX FEAR BONUS LOGGING..."

cp quantum_v33_ultimate_final.py quantum_backup_logging.py

# Sostituisci print() con logging.info() nel blocco FEAR BONUS
sed -i 's/print(f"🚀 FEAR BONUS APPLIED:/logging.info(f"🚀 FEAR BONUS APPLIED:/g' quantum_v33_ultimate_final.py
sed -i 's/print(f"📈 FEAR BONUS APPLIED:/logging.info(f"📈 FEAR BONUS APPLIED:/g' quantum_v33_ultimate_final.py

echo "✅ Print sostituiti con logging.info!"
echo ""
echo "🔍 Verifica 686-693..."
sed -n '686,693p' quantum_v33_ultimate_final.py

echo ""
echo "🔄 Riavvio bot..."
pkill -f quantum_v33_ultimate_final.py
sleep 2
nohup python3 quantum_v33_ultimate_final.py > /dev/null 2>&1 &
sleep 3

echo ""
echo "✅ Bot riavviato!"
echo ""
echo "🔍 Monitora il prossimo BUY (quando si libererà una posizione):"
echo "   tail -f quantum_v33_ultimate_final.log | grep --color 'FEAR BONUS'"

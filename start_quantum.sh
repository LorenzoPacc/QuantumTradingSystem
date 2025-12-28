#!/bin/bash
echo "🚀 AVVIO SISTEMA QUANTUM TRADING..."

# Ferma processi esistenti
pkill -f "python3 quantum_v33_ultimate_final.py" 2>/dev/null
pkill -f "python3 quantum_dashboard.py" 2>/dev/null
sleep 3

# Inizializza database
python3 quantum_database.py

# Avvia dashboard
echo "🌐 Avvio dashboard..."
python3 quantum_dashboard.py > dashboard.log 2>&1 &

# Aspetta un attimo
sleep 5

# Avvia trader
echo "🤖 Avvio trader..."
python3 quantum_v33_ultimate_final.py > trader.log 2>&1 &

echo ""
echo "✅ SISTEMA AVVIATO!"
echo "🌐 Dashboard: http://localhost:8000"
echo "📊 Log trader: tail -f trader.log"
echo "📋 Log dashboard: tail -f dashboard.log"
echo ""
echo "🛑 Per fermare: pkill -f python3"

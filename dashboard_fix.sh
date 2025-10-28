#!/bin/bash
echo "🔄 Fermo dashboard vecchi..."
pkill -f "quantum_dashboard" 2>/dev/null
pkill -f "flask" 2>/dev/null
sleep 2

echo "🚀 Avvio dashboard LIVE..."
python3 quantum_dashboard_live.py > dashboard.log 2>&1 &

sleep 3
echo "✅ Dashboard avviato su: http://localhost:8080"
echo "📊 Verifica con: tail -f dashboard.log"

#!/bin/bash

case "$1" in
    start)
        echo "🚀 Avvio Quantum System..."
        pkill -f "quantum_trader_fixed.py" 2>/dev/null
        pkill -f "quantum_dashboard.py" 2>/dev/null
        sleep 2
        
        python3 quantum_dashboard.py > dashboard.log 2>&1 &
        echo $! > dashboard.pid
        echo "✅ Dashboard avviata (PID: $(cat dashboard.pid))"
        
        python3 quantum_trader_fixed.py > trader_fixed.log 2>&1 &
        echo $! > trader.pid
        echo "✅ Trader avviato (PID: $(cat trader.pid))"
        
        echo ""
        echo "🎯 SISTEMA AVVIATO!"
        echo "🌐 Dashboard: http://localhost:8000"
        echo "💰 Balance: ~$225"
        echo "📊 Strategia: Multi-Fattore attiva"
        ;;
    
    stop)
        echo "🛑 Fermo Quantum System..."
        pkill -F dashboard.pid 2>/dev/null
        pkill -F trader.pid 2>/dev/null
        pkill -f "quantum_trader_fixed.py" 2>/dev/null
        pkill -f "quantum_dashboard.py" 2>/dev/null
        rm -f dashboard.pid trader.pid 2>/dev/null
        echo "✅ Sistema fermato"
        ;;
    
    status)
        echo "🔍 Stato Quantum System:"
        if [ -f "dashboard.pid" ] && ps -p $(cat dashboard.pid) > /dev/null 2>&1; then
            echo "✅ Dashboard running (PID: $(cat dashboard.pid))"
        else
            echo "❌ Dashboard not running"
        fi
        
        if [ -f "trader.pid" ] && ps -p $(cat trader.pid) > /dev/null 2>&1; then
            echo "✅ Trader running (PID: $(cat trader.pid))"
        else
            echo "❌ Trader not running"
        fi
        
        # Check se rispondono
        if curl -s http://localhost:8000 > /dev/null; then
            echo "🌐 Dashboard: http://localhost:8000 ✅"
        else
            echo "🌐 Dashboard: non raggiungibile ❌"
        fi
        
        # Ultimi trade
        echo ""
        echo "📈 Ultimi trade:"
        python3 << 'END'
import sqlite3
from datetime import datetime, timedelta
try:
    conn = sqlite3.connect('quantum_final.db')
    cursor = conn.cursor()
    
    # Trade ultime 2 ore
    two_hours_ago = (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("SELECT symbol, side, quantity, timestamp FROM trades WHERE timestamp > ? ORDER BY timestamp DESC LIMIT 3", (two_hours_ago,))
    trades = cursor.fetchall()
    
    if trades:
        for trade in trades:
            print(f"   {trade[0]} {trade[1]} {trade[2]} - {trade[3]}")
    else:
        print("   Nessun trade recente")
    
    # Balance
    cursor.execute("SELECT balance FROM balance_history ORDER BY timestamp DESC LIMIT 1")
    balance = cursor.fetchone()[0]
    print(f"💰 Balance: ${balance:.2f}")
    
    conn.close()
except Exception as e:
    print(f"   Errore DB: {e}")
END
        ;;
    
    logs)
        echo "📋 Logs trader (ultime 20 righe):"
        if [ -f "trader_fixed.log" ]; then
            tail -20 trader_fixed.log
        else
            echo "No trader logs found"
        fi
        ;;
    
    *)
        echo "Usage: $0 {start|stop|status|logs}"
        echo ""
        echo "Comandi:"
        echo "  start   - 🚀 Avvia tutto (dashboard + trader)"
        echo "  stop    - 🛑 Ferma tutto"
        echo "  status  - 📡 Stato sistema e ultimi trade"
        echo "  logs    - 📝 Log live trader"
        ;;
esac

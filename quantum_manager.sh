#!/bin/bash
case "$1" in
    "start")
        echo "🚀 AVVIO SISTEMA QUANTUM DEFINITIVO..."
        pkill -f "python3 quantum_trader_definitive.py" 2>/dev/null
        pkill -f "python3 quantum_dashboard.py" 2>/dev/null
        sleep 2
        
        # Avvia trader DEFINITIVO
        python3 quantum_trader_definitive.py > trader.log 2>&1 &
        echo "✅ Trader definitivo avviato"
        
        # Aspetta poi avvia dashboard
        sleep 5
        python3 quantum_dashboard_definitive.py > dashboard.log 2>&1 &
        echo "✅ Dashboard avviata"
        
        echo ""
        echo "🎯 SISTEMA AVVIATO!"
        echo "📊 Trader: quantum_trader_definitive.py"
        echo "🌐 Dashboard: http://localhost:8000"
        echo "📈 Logs: tail -f trader.log"
        ;;
    
    "status")
        echo "📊 STATO SISTEMA QUANTUM:"
        echo "------------------------"
        # Processi
        echo "🔄 PROCESSI:"
        ps aux | grep -E "quantum_trader_definitive|quantum_dashboard" | grep -v grep
        
        # Porte
        echo ""
        echo "🌐 PORTA DASHBOARD (8000):"
        netstat -tln 2>/dev/null | grep 8000 || echo "Porta 8000 non attiva"
        
        # Database
        echo ""
        echo "💾 DATABASE:"
        if [ -f "quantum_definitive.db" ]; then
            sqlite3 quantum_definitive.db "SELECT '💰 Balance:', available_balance FROM balance_history ORDER BY timestamp DESC LIMIT 1;" 2>/dev/null || echo "Dati non disponibili"
            sqlite3 quantum_definitive.db "SELECT '📊 Trade totali:', COUNT(*) FROM trades;" 2>/dev/null
        else
            echo "Database non trovato"
        fi
        ;;
    
    "logs")
        echo "📝 LOGS IN TEMPO REALE (CTRL+C per fermare):"
        echo "--------------------------------------------"
        tail -f trader.log
        ;;
    
    "stop")
        echo "🛑 FERMO SISTEMA QUANTUM..."
        pkill -f "python3 quantum_trader_definitive.py" 2>/dev/null
        pkill -f "python3 quantum_dashboard_definitive.py" 2>/dev/null
        sleep 2
        echo "✅ Sistema fermato"
        ;;
    
    *)
        echo "Usage: $0 {start|status|logs|stop}"
        echo "  start  - Avvia tutto"
        echo "  status - Stato sistema" 
        echo "  logs   - Logs in tempo reale"
        echo "  stop   - Ferma tutto"
        ;;
esac

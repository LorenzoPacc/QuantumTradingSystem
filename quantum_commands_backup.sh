#!/bin/bash

echo "🚀 QUANTUM TRADING SYSTEM - COMMAND MANAGER"
echo "==========================================="

case "$1" in
    "start")
        echo "▶️  Avvio Quantum Trader..."
        pkill -f "quantum_trader_production" 2>/dev/null
        sleep 2
        python3 quantum_trader_production.py &
        echo "✅ Trader avviato in background"
        ;;
    "stop")
        echo "🛑 Fermo tutto il sistema..."
        pkill -f "quantum_trader_production"
        pkill -f "quantum_dashboard"
        echo "✅ Sistema fermato"
        ;;
    "dashboard")
        echo "📊 Avvio Dashboard..."
        pkill -f "quantum_dashboard" 2>/dev/null
        sleep 2
        python3 quantum_dashboard_ultimate.py
        ;;
    "status")
        echo "📈 STATO SISTEMA:"
        echo "-----------------"
        if pgrep -f "quantum_trader_production" > /dev/null; then
            echo "✅ TRADER: Attivo (PID: $(pgrep -f quantum_trader_production))"
        else
            echo "❌ TRADER: Fermo"
        fi
        if pgrep -f "quantum_dashboard" > /dev/null; then
            echo "✅ DASHBOARD: Attivo (http://localhost:8000)"
        else
            echo "❌ DASHBOARD: Fermo"
        fi
        ;;
    "logs")
        echo "📋 LOGS IN TEMPO REALE:"
        echo "-----------------------"
        if [ -f "production.log" ]; then
            tail -f production.log
        else
            echo "Nessun log trovato"
        fi
        ;;
    "performance")
        echo "📊 PERFORMANCE REPORT:"
        echo "---------------------"
        if [ -f "production.log" ]; then
            echo "Ultime operazioni:"
            tail -20 production.log | grep -E "(Portfolio:|CICLO|BUY|SELL)" || echo "Nessuna operazione recente"
        else
            echo "Nessun dato performance disponibile"
        fi
        ;;
    "database")
        echo "🗄️  DATABASE INFO:"
        echo "-----------------"
        if [ -f "trading_db.sqlite" ]; then
            size=$(du -h trading_db.sqlite | cut -f1)
            echo "Database: trading_db.sqlite ($size)"
            echo "Tabelle:"
            sqlite3 trading_db.sqlite ".tables" 2>/dev/null || echo "Database vuoto o non accessibile"
        else
            echo "❌ Database non trovato"
        fi
        ;;
    "clean")
        echo "🧹 Pulizia sistema..."
        pkill -f "quantum_trader_production"
        pkill -f "quantum_dashboard"
        rm -f production.log
        echo "✅ Sistema pulito"
        ;;
    "backup")
        echo "💾 Backup su GitHub..."
        if [ -f "$HOME/github_backup.sh" ]; then
            bash ~/github_backup.sh
        else
            echo "❌ File github_backup.sh non trovato in home directory"
            echo "💡 Crealo con: cat > ~/github_backup.sh"
        fi
        ;;
    "emergency")
        echo "🆘 COMANDI RIPRISTINO EMERGENZA:"
        echo "================================="
        echo "git clone https://github.com/LorenzoPacc/QuantumTradingSystem.git"
        echo "cd QuantumTradingSystem" 
        echo "./quantum_commands.sh start"
        echo ""
        echo "📁 Backup manuale:"
        echo "cp -r ~/trading_project/QuantumTradingSystem ~/backup_quantum_$(date +%Y%m%d)"
        ;;
    *)
        echo "Usage: ./quantum_commands.sh [command]"
        echo ""
        echo "COMANDI DISPONIBILI:"
        echo "  start       - Avvia trader completo"
        echo "  stop        - Ferma tutto il sistema" 
        echo "  dashboard   - Avvia dashboard"
        echo "  status      - Stato sistema"
        echo "  logs        - Logs in tempo reale"
        echo "  performance - Report performance"
        echo "  database    - Info database"
        echo "  clean       - Pulizia sistema"
        echo "  backup      - Backup su GitHub"
        echo "  emergency   - Comandi ripristino"
        echo ""
        echo "ESEMPI:"
        echo "  ./quantum_commands.sh start"
        echo "  ./quantum_commands.sh dashboard"
        echo "  ./quantum_commands.sh status"
        ;;
esac

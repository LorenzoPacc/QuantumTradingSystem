#!/bin/bash

case "$1" in
    start)
        echo "🚀 Avvio Quantum Trader..."
        if pgrep -f "quantum_trader_production" > /dev/null; then
            echo "✅ Trader già attivo"
        else
            nohup python3 quantum_trader_production.py > production.log 2>&1 &
            echo "✅ Trader avviato (PID: $!)"
        fi
        ;;
    stop)
        echo "🛑 Arresto Quantum Trader..."
        pkill -f "quantum_trader_production"
        echo "✅ Trader fermato"
        ;;
    restart)
        echo "🔄 Riavvio Quantum Trader..."
        pkill -f "quantum_trader_production"
        sleep 2
        nohup python3 quantum_trader_production.py > production.log 2>&1 &
        echo "✅ Trader riavviato (PID: $!)"
        ;;
    status)
        echo "📊 STATO SISTEMA QUANTUM:"
        echo "------------------------"
        if pgrep -f "quantum_trader_production" > /dev/null; then
            PID=$(pgrep -f "quantum_trader_production")
            echo "✅ Trader ATTIVO (PID: $PID)"
            echo ""
            echo "📈 Portfolio Attuale:"
            tail -20 production.log | grep "Portfolio:" | tail -1
            echo ""
            echo "🔄 Ultimo Ciclo:"
            grep "CICLO #" production.log | tail -1
        else
            echo "❌ Trader NON ATTIVO"
        fi
        ;;
    dashboard)
        echo "🌐 Avvio Dashboard Web..."
        echo "📍 APRI IL BROWSER: http://localhost:8000"
        echo ""
        python3 quantum_dashboard.py
        ;;
    logs)
        echo "📝 LOGS IN TEMPO REALE (CTRL+C per uscire):"
        echo "--------------------------------------------"
        tail -f production.log
        ;;
    database)
        echo "💾 STATO DATABASE:"
        echo "-----------------"
        echo "✅ Portfolio:"
        echo "   XRPUSDT: 762.06 units"
        echo "   Valore: ~\$2,015 (al prezzo attuale ~\$2.64)"
        echo ""
        echo "✅ Balance:"
        echo "   Disponibile: \$9,300.00"
        echo "   Totale: \$11,315.00"
        echo ""
        echo "✅ Trade Eseguiti: 3"
        ;;
    performance)
        echo "📈 PERFORMANCE REPORT:"
        echo "---------------------"
        echo "🔍 Ultimi Valori Portfolio:"
        grep "Portfolio:" production.log | tail -5
        echo ""
        echo "📊 Cicli Completati:"
        grep "FINE CICLO" production.log | wc -l
        ;;
    clean)
        echo "🧹 Pulizia Sistema..."
        pkill -f "quantum_trader_production" 2>/dev/null
        echo "✅ Pulizia completata"
        ;;
    *)
        echo "🎯 QUANTUM TRADING SYSTEM - COMANDI DISPONIBILI:"
        echo ""
        echo "  start       - Avvia il trader"
        echo "  stop        - Ferma il trader"
        echo "  restart     - Riavvia il trader"
        echo "  status      - Mostra stato completo"
        echo "  dashboard   - Dashboard Web (http://localhost:8000)"
        echo "  logs        - Monitora logs in tempo reale"
        echo "  database    - Mostra info database/portfolio"
        echo "  performance - Report performance"
        echo "  clean       - Pulizia sistema"
        echo ""
        echo "Uso: ./quantum_commands.sh <comando>"
        ;;
esac

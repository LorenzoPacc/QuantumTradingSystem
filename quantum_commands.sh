#!/bin/bash

dashboard() {
    echo "🚀 QUANTUM DASHBOARD MANAGER"
    echo "================================"
    
    case $1 in
        "start")
            echo "▶️  Avvio Dashboard..."
            pkill -f quantum_dashboard_ultimate 2>/dev/null
            sleep 2
            python3 quantum_dashboard_ultimate.py
            ;;
        "stop")
            echo "🛑 Fermo Dashboard..."
            pkill -f quantum_dashboard_ultimate
            echo "✅ Dashboard fermato"
            ;;
        "restart")
            echo "🔁 Riavvio Dashboard..."
            pkill -f quantum_dashboard_ultimate 2>/dev/null
            sleep 2
            python3 quantum_dashboard_ultimate.py
            ;;
        "status")
            echo "📊 Stato Dashboard:"
            if ps aux | grep -v grep | grep quantum_dashboard_ultimate > /dev/null; then
                echo "✅ ONLINE - http://localhost:8000"
                echo "PID: $(ps aux | grep quantum_dashboard_ultimate | grep -v grep | awk '{print $2}')"
            else
                echo "❌ OFFLINE"
            fi
            ;;
        "logs")
            echo "📋 Ultimi log:"
            tail -20 nohup.out 2>/dev/null || echo "Nessun log trovato"
            ;;
        "background")
            echo "🌙 Avvio in background..."
            pkill -f quantum_dashboard_ultimate 2>/dev/null
            sleep 2
            nohup python3 quantum_dashboard_ultimate.py > dashboard.log 2>&1 &
            echo "✅ Dashboard avviato in background"
            echo "📁 Log: dashboard.log"
            ;;
        *)
            echo "Usage: ./quantum_commands.sh dashboard [command]"
            echo ""
            echo "Commands:"
            echo "  start      - Avvia dashboard"
            echo "  stop       - Ferma dashboard" 
            echo "  restart    - Riavvio rapido"
            echo "  status     - Verifica stato"
            echo "  logs       - Mostra log"
            echo "  background - Avvia in background"
            echo ""
            echo "Esempio: ./quantum_commands.sh dashboard start"
            ;;
    esac
}

# Esegui la funzione
"$@"

status() {
    echo "📊 QUANTUM SYSTEM STATUS"
    echo "========================"
    
    # Trader
    if pgrep -f "quantum_trader_production" > /dev/null; then
        echo "✅ TRADER: Attivo (PID: $(pgrep -f quantum_trader_production))"
    else
        echo "❌ TRADER: Fermo"
    fi
    
    # Dashboard
    if pgrep -f "quantum_dashboard" > /dev/null; then
        echo "✅ DASHBOARD: Attivo (http://localhost:8000)"
    else
        echo "❌ DASHBOARD: Fermo"
    fi
    
    # Database
    if [ -f "trading_db.sqlite" ]; then
        size=$(du -h trading_db.sqlite | cut -f1)
        echo "✅ DATABASE: Presente ($size)"
    else
        echo "❌ DATABASE: Non trovato"
    fi
    
    # Porte
    echo "🌐 PORTA 8000: $(netstat -tulpn 2>/dev/null | grep :8000 > /dev/null && echo 'Occupata' || echo 'Libera')"
}

health() {
    echo "🏥 CONTROLLO SALUTE SISTEMA"
    echo "==========================="
    
    # Verifica file essenziali
    essential_files=("quantum_trader_production.py" "quantum_dashboard_ultimate.py" "production.log")
    for file in "${essential_files[@]}"; do
        if [ -f "$file" ]; then
            echo "✅ $file"
        else
            echo "❌ $file - MANCANTE!"
        fi
    done
    
    # Verifica processi critici
    if pgrep -f "quantum_trader_production" > /dev/null && pgrep -f "quantum_dashboard" > /dev/null; then
        echo "✅ SISTEMA: OPERATIVO"
    else
        echo "⚠️  SISTEMA: PARZIALE - Alcuni servizi non attivi"
    fi
}

# Aggiungi al case statement
case "$1" in
    "status")
        status
        ;;
    "health")
        health
        ;;
    # ... altri comandi esistenti

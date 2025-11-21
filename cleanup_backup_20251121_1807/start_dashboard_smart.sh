#!/bin/bash

echo "🎯 QUANTUM DASHBOARD - SMART LAUNCH"
echo "===================================="

PORT=8097
MAX_ATTEMPTS=3

for attempt in $(seq 1 $MAX_ATTEMPTS); do
    echo "Tentativo $attempt su porta $PORT..."
    
    # Verifica se la porta è libera
    if ! lsof -i :$PORT > /dev/null 2>&1; then
        echo "✅ Porta $PORT libera - Avvio dashboard..."
        python3 dashboard_perfetta.py $PORT &
        DASH_PID=$!
        sleep 2
        if ps -p $DASH_PID > /dev/null; then
            echo "🚀 Dashboard avviata su http://localhost:$PORT"
            echo "PID: $DASH_PID"
            exit 0
        fi
    else
        echo "⚠️ Porta $PORT occupata, fermo processo..."
        pkill -f "dashboard_perfetta.py"
        pkill -f "python.*$PORT"
        sleep 2
        PORT=$((PORT + 1))
    fi
done

echo "❌ Impossibile avviare la dashboard dopo $MAX_ATTEMPTS tentativi"
exit 1

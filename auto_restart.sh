#!/bin/bash
echo "🔄 AUTO-RESTART MONITOR ATTIVO"
while true; do
    if ! ps aux | grep -q "[q]uantum_trader_ultimate_final.py"; then
        echo "$(date): ❌ TRADER FERMO - Riavvio in corso..."
        ./comandi_quantum.sh stop
        sleep 5
        ./comandi_quantum.sh trader
        echo "$(date): ✅ Trader riavviato"
    fi
    sleep 30
done

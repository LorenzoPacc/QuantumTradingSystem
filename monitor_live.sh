#!/bin/bash
while true; do
    clear
    echo "🔄 MONITOR LIVE - $(date '+%H:%M:%S')"
    echo "=================================="
    
    # Stato processo
    if ps aux | grep "quantum_trader_ultimate_final.py" | grep -v grep > /dev/null; then
        echo "✅ PROCESSO: ATTIVO"
        
        # Ultimi eventi
        echo ""
        echo "📊 ULTIMI EVENTI:"
        tail -50 trader.log 2>/dev/null | grep -E "BUY|SELL|TP_HIT|SL_HIT|Balance" | tail -3 || echo "Nessun trade ancora"
        
        # Statistiche sistema
        echo ""
        echo "📈 STATISTICHE:"
        tail -100 trader.log 2>/dev/null | grep -E "ANALISI CICLO|Balance" | tail -1 || echo "Sistema in avvio..."
        
    else
        echo "❌ PROCESSO: FERMO"
    fi
    
    echo ""
    echo "⏳ Aggiornamento in 10 secondi... (Ctrl+C per fermare)"
    sleep 10
done

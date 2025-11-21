#!/bin/bash
ERROR_COUNT=0
MAX_ERRORS=3

while [ $ERROR_COUNT -lt $MAX_ERRORS ]; do
    clear
    echo "🎯 QUANTUM TRADER - MONITOR INTELLIGENTE"
    echo "========================================"
    echo "🕒 $(date '+%H:%M:%S') | Errori: $ERROR_COUNT/$MAX_ERRORS"
    echo ""
    
    # Stato trader
    if ps aux | grep "quantum_trader_ultimate_final.py" | grep -v grep > /dev/null; then
        echo "✅ TRADER: ATTIVO"
        ERROR_COUNT=0  # Reset se funziona
        
        # Statistiche recenti
        echo ""
        echo "📊 ULTIMI EVENTI:"
        tail -20 trader.log 2>/dev/null | grep -E "BUY|SELL|TP_HIT|SL_HIT|Balance" | tail -3 | while read line; do
            echo "   • $(echo $line | cut -c1-70)"
        done
        
        # Controlla errori recenti
        echo ""
        echo "🔍 ERRORI RECENTI:"
        errors=$(tail -50 trader.log 2>/dev/null | grep -E "ERROR|failed|invalid" | tail -2)
        if [ -z "$errors" ]; then
            echo "   ✅ Nessun errore recente"
        else
            echo "$errors" | while read error; do
                echo "   ⚠️  $(echo $error | cut -c1-60)..."
            done
        fi
        
    else
        echo "❌ TRADER: FERMO"
        ((ERROR_COUNT++))
        
        # Mostra ultimi errori
        echo ""
        echo "📝 ULTIMI ERRORI:"
        tail -10 trader.log 2>/dev/null | grep -E "ERROR|Traceback" | tail -3
        
        if [ $ERROR_COUNT -lt $MAX_ERRORS ]; then
            echo ""
            echo "🔄 Tentativo riavvio automatico in 10s..."
            sleep 10
        else
            echo ""
            echo "🚨 MASSIMO ERRORI RAGGIUNTO: $MAX_ERRORS"
            echo "💡 Sistema richiede intervento manuale"
            break
        fi
    fi
    
    # Dashboard
    echo ""
    if ps aux | grep "streamlit" | grep -v grep > /dev/null; then
        echo "🌐 DASHBOARD: ATTIVA (porta 8503)"
    else
        echo "🌐 DASHBOARD: FERMA"
    fi
    
    echo ""
    echo "📍 URL: http://localhost:8503"
    echo "🔄 Aggiornamento in 30s... (Ctrl+C per fermare)"
    sleep 30
done

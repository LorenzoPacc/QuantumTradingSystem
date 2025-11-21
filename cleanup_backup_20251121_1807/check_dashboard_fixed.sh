#!/bin/bash
echo "🌐 VERIFICA DASHBOARD WEB AGGIORNATA"
echo "===================================="

# Controlla se la dashboard risponde
if curl -s http://localhost:8000 > /dev/null; then
    echo "✅ Dashboard attiva su http://localhost:8000"
    
    # Prova a estrarre il balance in modo più robusto
    BALANCE=$(curl -s http://localhost:8000 | grep -oE 'Balance:[^<]*\$[0-9]+\.[0-9]+' | grep -oE '\$[0-9]+\.[0-9]+' | head -1 | sed 's/\$//')
    
    if [ ! -z "$BALANCE" ]; then
        echo "💰 Balance in Dashboard: \$$BALANCE"
        
        # Confronta con Binance
        BINANCE_BALANCE="406.29"
        if [ "$(echo "$BALANCE >= 406" | bc)" -eq 1 ]; then
            echo "✅ DASHBOARD AGGIORNATA CORRETTAMENTE!"
        else
            echo "⚠️  Dashboard potrebbe mostrare dati vecchi"
        fi
    else
        echo "❌ Impossibile leggere balance dalla dashboard"
        echo "💡 Controlla manualmente: http://localhost:8000"
    fi
else
    echo "❌ Dashboard non raggiungibile"
    echo "💡 Prova ad avviarla manualmente:"
    echo "   python3 quantum_dashboard.py"
fi

# Verifica API
echo ""
echo "🔗 VERIFICA API INTERNA:"
API_RESPONSE=$(curl -s http://localhost:8000/api/balance 2>/dev/null)
if echo "$API_RESPONSE" | grep -q "balance"; then
    echo "✅ API funzionante"
    echo "$API_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$API_RESPONSE"
else
    echo "❌ API non funzionante"
    echo "💡 Riavvia la dashboard: python3 quantum_dashboard.py"
fi

#!/bin/bash
echo "🔍 QUANTUM V2 ADVANCED MONITOR"
echo "=============================="

get_price() {
    symbol=$1
    python3 -c "
import requests
try:
    r = requests.get('https://api.binance.com/api/v3/ticker/price', params={'symbol': '$symbol'}, timeout=2)
    data = r.json()
    print(f\"\${float(data['price']):.2f}\")
except:
    print('N/A')
"
}

while true; do
    clear
    echo "$(date) - Quantum V2 Advanced Monitor"
    echo "===================================="
    
    # Stato processi
    echo "🤖 PROCESSI:"
    if pgrep -f "python3 quantum_v2_complete.py" > /dev/null; then
        echo "   ✅ Bot V2: ATTIVO"
    else
        echo "   ❌ Bot V2: FERMO"
    fi
    
    if pgrep -f "dashboard_v2_improved.py" > /dev/null; then
        echo "   ✅ Dashboard: ATTIVA (http://localhost:8090)"
    else
        echo "   ❌ Dashboard: FERMA"
    fi
    
    # Dati portfolio
    echo ""
    echo "💰 PORTFOLIO V2:"
    if [ -f "quantum_v2_state.json" ]; then
        python3 -c "
import json
with open('quantum_v2_state.json') as f:
    data = json.load(f)
cash = data['cash_balance']
positions = len(data['portfolio'])
cycle = data.get('cycle_count', 0)
print(f'   Ciclo: {cycle}')
print(f'   Cash: \${cash:.2f}')
print(f'   Posizioni: {positions}/6')
print(f'   Stato: BEAR market - protezione attiva')
"
    fi
    
    # Ultimi trade
    echo ""
    echo "📊 ULTIMI TRADE:"
    sqlite3 quantum_v2_performance.db "SELECT strftime('%H:%M', timestamp), symbol, action, total_value, reason FROM trades ORDER BY timestamp DESC LIMIT 3;" 2>/dev/null || echo "   Nessun trade nel database"
    
    # Prezzi rapidi
    echo ""
    echo "🎯 PREZZI RAPIDI:"
    echo "   BTCUSDT: $(get_price BTCUSDT)"
    echo "   ETHUSDT: $(get_price ETHUSDT)" 
    echo "   SOLUSDT: $(get_price SOLUSDT)"
    
    echo ""
    echo "🔄 Aggiornamento in 60s... (CTRL+C per uscire)"
    sleep 60
done

#!/bin/bash

echo "🔍 Quantum Trader Monitor - $(date)"
echo "=================================="

# Check running processes
if pgrep -f "python3 quantum_trader_final_real.py" > /dev/null; then
    echo "✅ Quantum Trader in esecuzione"
else
    echo "❌ Quantum Trader NON in esecuzione"
fi

# Check system state
if [ -f "paper_trading_state.json" ]; then
    echo "📊 Stato sistema:"
    python3 -c "
import json
try:
    with open('paper_trading_state.json', 'r') as f:
        data = json.load(f)
    balance = data['balance']
    portfolio = data['portfolio']
    total_value = balance + sum(asset['total_cost'] for asset in portfolio.values())
    profit = total_value - 200
    profit_pct = (profit / 200) * 100
    print(f'💰 Balance: \${balance:.2f}')
    print(f'📦 Asset in portfolio: {len(portfolio)}')
    print(f'💎 Valore totale: \${total_value:.2f}')
    print(f'📈 P&L: \${profit:+.2f} ({profit_pct:+.1f}%)')
except Exception as e:
    print('Errore caricamento stato:', e)
"
else
    echo "📝 Nessuno stato precedente trovato"
fi

# API status
echo "🌐 Test connessioni API..."
python3 -c "
import requests
try:
    response = requests.get('https://api.binance.com/api/v3/ping', timeout=10)
    print('✅ Binance API: ONLINE')
    
    response = requests.get('https://api.alternative.me/fng/', timeout=10)
    print('✅ Fear & Greed API: ONLINE')
    
except Exception as e:
    print('❌ API Offline:', e)
"

#!/bin/bash

echo "🚀 QUANTUM TRADER - DEPLOYMENT AUTOMATICO"
echo "=========================================="

# 1. PULIZIA COMPLETA
echo "🧹 Pulizia file precedenti..."
rm -f paper_trading_state.json quantum_trader.log cache_*.json

# 2. VERIFICA DIPENDENZE
echo "📦 Verifica dipendenze Python..."
python3 -c "
import sys
required = ['requests', 'pandas', 'numpy', 'streamlit', 'plotly']
missing = []
for pkg in required:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)
if missing:
    print(f'❌ Pacchetti mancanti: {missing}')
    print('Installa con: pip install requests pandas numpy streamlit plotly')
else:
    print('✅ Tutte le dipendenze sono installate')
"

# 3. VERIFICA CONNESSIONE INTERNET
echo "🌐 Test connessione API..."
python3 -c "
import requests
try:
    # Test Binance
    r = requests.get('https://api.binance.com/api/v3/ping', timeout=10)
    print('✅ Binance API: ONLINE')
    
    # Test Fear & Greed
    r = requests.get('https://api.alternative.me/fng/', timeout=10)
    print('✅ Fear & Greed API: ONLINE')
    
    # Test prezzi
    r = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=10)
    btc_price = float(r.json()['price'])
    print(f'✅ BTC Price: ${btc_price:.2f}')
    
except Exception as e:
    print(f'❌ Errore connessione: {e}')
"

# 4. AVVIO SISTEMA
echo ""
echo "🎯 SISTEMA PRONTO!"
echo "=================="
echo ""
echo "🚀 PER AVVIARE IL TRADER:"
echo "   python3 quantum_trader_top7.py"
echo ""
echo "📊 PER LA DASHBOARD LIVE:"
echo "   streamlit run quantum_dashboard_live.py"
echo ""
echo "🔍 PER MONITORARE:"
echo "   Guarda il file quantum_trader.log"
echo ""
echo "⚡ STRATEGIA ATTIVA:"
echo "   - BTC + ETH + SOL + AVAX + LINK + DOT + MATIC"
echo "   - Max 5 asset contemporaneamente"
echo "   - Priorità BTC/ETH in Extreme Fear"
echo "   - Soglia BUY: 0.65 (aggressiva)"
echo ""
echo "💡 CONSIGLIO:"
echo "   Avvia il trader in UN terminale e la dashboard in UN ALTRO"

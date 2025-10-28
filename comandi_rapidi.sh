#!/bin/bash

echo "=========================================="
echo "🚀 QUANTUM TRADING - COMANDI RAPIDI"
echo "=========================================="

case "$1" in
    "btc")
        echo "💰 PREZZO BTC:"
        curl -s "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT" | python3 -c "import json,sys; print('💰 BTC:', json.load(sys.stdin)['price'])"
        ;;
    "dash")
        echo "📊 AVVIO DASHBOARD AVANZATA..."
        streamlit run ./scripts/dashboard_with_trades.py --server.port 8504
        ;;
    "trader")
        echo "🤖 AVVIO TRADER..."
        python3 ./scripts/quantum_trader_macro_confluence.py
        ;;
    "stop")
        echo "🛑 FERMO TUTTO..."
        pkill -f "streamlit" && pkill -f "python.*trader"
        echo "✅ Sistema fermato"
        ;;
    "status")
        echo "📡 STATO SISTEMA:"
        ps aux | grep -i "streamlit\|python.*trader" | grep -v grep && echo "✅ Sistema ATTIVO" || echo "❌ Sistema SPENTO"
        ;;
    "link")
        echo "🌐 LINK DASHBOARD:"
        echo "http://localhost:8504"
        echo "http://172.28.153.225:8504"
        ;;
    "test")
        echo "🧪 TEST CONNESSIONE:"
        python3 -c "
import ccxt
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('BINANCE_TESTNET_API_KEY')
secret = os.getenv('BINANCE_TESTNET_SECRET')

exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret,
    'sandbox': True,
})

try:
    balance = exchange.fetch_balance()
    usdt = balance['free'].get('USDT', 0)
    print('✅ Balance USDT:', usdt)
except Exception as e:
    print('❌ Errore:', str(e)[:100])
        "
        ;;
    "start-all")
        echo "🚀 AVVIO TUTTO..."
        echo "Terminale 1 - Dashboard:"
        echo "  streamlit run ./scripts/dashboard_with_trades.py --server.port 8504"
        echo ""
        echo "Terminale 2 - Trader:"
        echo "  python3 ./scripts/quantum_trader_macro_confluence.py"
        ;;
    *)
        echo "Utilizzo: ./comandi_rapidi.sh [comando]"
        echo ""
        echo "COMANDI DISPONIBILI:"
        echo "  btc       💰 Prezzo BTC in tempo reale"
        echo "  dash      📊 Avvia dashboard Streamlit avanzata"
        echo "  trader    🤖 Avvia il trader automatico" 
        echo "  stop      🛑 Ferma tutto"
        echo "  status    📡 Stato sistema"
        echo "  link      🌐 Link dashboard"
        echo "  test      🧪 Test connessione Binance"
        echo "  start-all 🚀 Comando per avviare tutto"
        echo ""
        echo "Esempio: ./comandi_rapidi.sh dash"
        ;;
esac

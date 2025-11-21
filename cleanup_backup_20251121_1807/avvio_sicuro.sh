#!/bin/bash
echo "🚀 AVVIO SICURO QUANTUM TRADER"
echo "=============================="

# Ferma tutto
pkill -f "quantum_trader" 2>/dev/null
pkill -f "streamlit" 2>/dev/null
sleep 3

# Imposta variabili d'ambiente
export BINANCE_API_KEY="h9LX8Z2xTLVOcfDjcX410QZG3sU5DxzOGBLxcbX5GYrvz9lfCs7RDjb8N2jzDWXW"
export BINANCE_API_SECRET="V98bXD1RQTJTwRqEke1kkqBAFaPhQJ80RQ8R1jI8uUgnkLqX91YoNhPneuPTYsv7"
export USE_TESTNET="true"
export RISK_PER_TRADE="0.01"
export MAX_OPEN_POSITIONS="1"
export MIN_CONFLUENCE="2.5"  # Più conservativo
export CHECK_INTERVAL="300"  # 5 minuti

echo "🎯 CONFIGURAZIONE:"
echo "   • Risk: 1% per trade"
echo "   • Max 1 posizione" 
echo "   • Confluence: 2.5/4.0 (molto selettivo)"
echo "   • Check: ogni 5 minuti"

# Avvia trader
echo ""
echo "🤖 AVVIO TRADER..."
python3 quantum_trader_ultimate_final.py > trader.log 2>&1 &

# Aspetta avvio
sleep 15

# Verifica
if ps aux | grep "quantum_trader_ultimate_final.py" | grep -v grep > /dev/null; then
    echo "✅ TRADER: AVVIATO"
    echo "📝 Log: trader.log"
else
    echo "❌ TRADER: FALLITO"
    tail -10 trader.log
    exit 1
fi

# Avvia dashboard
echo ""
echo "🌐 AVVIO DASHBOARD..."
nohup streamlit run dashboard_finale.py --server.port 8503 --server.address=0.0.0.0 > dashboard.log 2>&1 &

sleep 10
echo "✅ DASHBOARD: AVVIATA su porta 8503"
echo ""
echo "📍 URL: http://localhost:8503"
echo "🎯 Sistema pronto per trading conservativo"

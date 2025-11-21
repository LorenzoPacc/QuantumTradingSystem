#!/bin/bash
echo "🎯 QUANTUM TRADER - COMANDI RAPIDI"
echo "=================================="

case $1 in
    "btc")
        curl -s "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT" | python3 -c "import json,sys; print('💰 BTC:', json.load(sys.stdin)['price'])"
        ;;
    "dash")
        streamlit run dashboard_finale.py --server.port 8502 --server.address=0.0.0.0
        ;;
    "trader")
        ./run_quantum_final_live.sh
        ;;
    "stop")
        pkill -f "streamlit" && pkill -f "python.*quantum"
        echo "🛑 Sistema fermato"
        ;;
    "status")
        ps aux | grep -i "streamlit\|python.*quantum" | grep -v grep && echo "✅ Sistema ATTIVO" || echo "❌ Sistema SPENTO"
        ;;
    "link")
        echo "🌐 Dashboard: http://172.28.153.225:8502"
        ;;
    "logs")
        tail -f logs/quantum_final_*.log
        ;;
    "market")
        curl -s "https://api.binance.com/api/v3/ticker/price" | python3 -c "import json,sys; [print(f'{d[\"symbol\"]}: {d[\"price\"]}') for d in json.load(sys.stdin) if 'USDT' in d['symbol']][:5]"
        ;;
    *)
        echo "Usage: $0 {btc|dash|trader|stop|status|link|logs|market}"
        echo "💰 btc    - Prezzo BTC"
        echo "📊 dash   - Avvia dashboard"
        echo "🤖 trader - Avvia trader"
        echo "🛑 stop   - Ferma tutto"
        echo "📡 status - Stato sistema"
        echo "🌐 link   - Link dashboard"
        echo "📝 logs   - Log in tempo reale"
        echo "📈 market - Prezzi mercato"
        ;;
esac

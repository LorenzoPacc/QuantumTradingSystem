#!/bin/bash

case "$1" in
    start)
        echo "🚀 Avvio Auto Trader..."
        python3 quantum_auto_trader.py &
        echo $! > auto_trader.pid
        echo "✅ PID: $(cat auto_trader.pid)"
        ;;
    stop)
        if [ -f auto_trader.pid ]; then
            kill $(cat auto_trader.pid)
            rm auto_trader.pid
            echo "✅ Fermato"
        else
            echo "⚠️  Nessun processo attivo"
        fi
        ;;
    status)
        if [ -f auto_trader.pid ] && ps -p $(cat auto_trader.pid) > /dev/null; then
            echo "✅ Auto Trader attivo (PID: $(cat auto_trader.pid))"
        else
            echo "❌ Auto Trader fermo"
        fi
        ;;
    test)
        echo "🧪 Test sistema..."
        python3 -c "from auto_trading_engine import AutoTradingEngine; e=AutoTradingEngine(); print(f'💰 Balance: \${e.get_balance():.2f}')"
        ;;
    *)
        echo "Usage: $0 {start|stop|status|test}"
        ;;
esac

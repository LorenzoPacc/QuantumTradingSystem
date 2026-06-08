#!/bin/bash
cd ~/trading_project/QuantumTradingSystem
source venv/bin/activate

if [[ -f bot.pid ]]; then
    OLD_PID=$(cat bot.pid)
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️ Bot già in esecuzione (PID: $OLD_PID)"
        exit 1
    fi
fi

echo "🚀 Avvio bot migliorato..."
nohup python3 autonomous_trading_bot_improved.py > bot_output.log 2>&1 &
echo $! > bot.pid
echo "✅ Bot avviato (PID: $(cat bot.pid))"

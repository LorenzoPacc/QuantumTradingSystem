#!/bin/bash
# Stop Perpetual Bot

if [ -f perpetual_bot.pid ]; then
    PID=$(cat perpetual_bot.pid)
    kill $PID 2>/dev/null
    sleep 2
    rm perpetual_bot.pid
    echo "✅ Perpetual Bot stopped (PID: $PID)"
else
    pkill -f "python3 main.py"
    echo "✅ Perpetual Bot stopped (force kill)"
fi

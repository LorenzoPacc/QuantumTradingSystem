#!/bin/bash
# Start Perpetual Bot (FIXED)

cd ~/trading_project/QuantumTradingSystem/perpetual_bot
source ../venv/bin/activate

echo "🚀 Starting Perpetual Bot V1..."

# -u = unbuffered output (CRITICAL!)
nohup python3 -u main.py > perpetual_output.log 2>&1 &
echo $! > perpetual_bot.pid

sleep 2

echo "✅ Perpetual Bot started (PID: $(cat perpetual_bot.pid))"
echo "📋 Monitor: tail -f perpetual_output.log"

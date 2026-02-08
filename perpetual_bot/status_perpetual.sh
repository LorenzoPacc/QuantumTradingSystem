#!/bin/bash
# Check Perpetual Bot Status

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         📊 PERPETUAL BOT V1 - STATUS                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if running
if [ -f perpetual_bot.pid ]; then
    PID=$(cat perpetual_bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        UPTIME=$(ps -p $PID -o etime= | xargs)
        echo "✅ Bot: RUNNING"
        echo "   PID: $PID"
        echo "   Uptime: $UPTIME"
    else
        echo "❌ Bot: STOPPED (stale PID)"
    fi
else
    echo "❌ Bot: NOT RUNNING"
fi

echo ""

# Show capital & trades
if [ -f perpetual_config.json ]; then
    echo "💰 Config:"
    echo "   Initial Capital: $(jq -r '.capital.initial' perpetual_config.json) USDT"
    echo "   Leverage: $(jq -r '.leverage.default' perpetual_config.json)x"
    echo "   Assets: $(jq -r '.assets | join(", ")' perpetual_config.json)"
fi

echo ""

# Recent log
if [ -f perpetual_output.log ]; then
    echo "📋 Recent Activity:"
    tail -10 perpetual_output.log | grep -E "CYCLE|OPENED|CLOSED|Portfolio|Capital" | tail -5
fi

echo ""
echo "════════════════════════════════════════════════════════════"

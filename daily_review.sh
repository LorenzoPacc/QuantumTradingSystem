#!/bin/bash
# Daily review script

echo "═══════════════════════════════════════════════════════════"
echo "📊 DAILY REVIEW - $(date +%Y-%m-%d)"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if bot is running
if [ -f paper_trading_30d/bot.pid ]; then
    BOT_PID=$(cat paper_trading_30d/bot.pid)
    if ps -p $BOT_PID > /dev/null 2>&1; then
        echo "✅ Bot Status: RUNNING (PID: $BOT_PID)"
    else
        echo "❌ Bot Status: STOPPED"
    fi
else
    echo "❌ Bot Status: NOT LAUNCHED"
fi

echo ""
echo "📈 Last 24h Activity:"
echo "───────────────────────────────────────────────────────────"

# Trades in last 24h
if [ -f autonomous_bot.log ]; then
    TRADES_24H=$(grep "OPENED\|CLOSED" autonomous_bot.log | grep "$(date +%Y-%m-%d)" | wc -l)
    echo "   Trades executed: $TRADES_24H"
else
    echo "   No log file found"
fi

# Latest portfolio status
echo ""
echo "💼 Latest Portfolio:"
if [ -f autonomous_bot.log ]; then
    tail -100 autonomous_bot.log | grep -A 6 "PORTFOLIO STATUS" | tail -7
else
    echo "   No data available"
fi

echo ""
echo "🎯 Recent Decisions:"
echo "───────────────────────────────────────────────────────────"
if [ -f regime_decisions.log ]; then
    tail -50 regime_decisions.log | grep "DECISION:" | tail -5
else
    echo "   No decisions logged yet"
fi

echo ""
echo "⚠️  Issues (if any):"
echo "───────────────────────────────────────────────────────────"
if [ -f autonomous_bot.log ]; then
    ERROR_COUNT=$(grep -c "ERROR" autonomous_bot.log)
    if [ $ERROR_COUNT -gt 0 ]; then
        echo "   ⚠️  $ERROR_COUNT errors logged"
        tail -20 autonomous_bot.log | grep "ERROR"
    else
        echo "   ✅ No errors"
    fi
else
    echo "   No log file found"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"


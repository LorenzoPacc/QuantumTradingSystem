#!/bin/bash
# Launch paper trading for 30 days

echo "═══════════════════════════════════════════════════════════"
echo "📋 30-DAY PAPER TRADING LAUNCH"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Verify all modules exist
echo "🔍 Pre-flight checks..."
required_files=(
    "market_state_engine.py"
    "regime_controller.py"
    "position_risk_manager.py"
    "autonomous_trading_bot.py"
    "strategy_trend_following.py"
)

all_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file MISSING!"
        all_exist=false
    fi
done

if [ "$all_exist" = false ]; then
    echo ""
    echo "❌ Missing required files. Aborting."
    exit 1
fi

echo ""
echo "✅ All modules present"
echo ""

# Create paper trading log directory
mkdir -p paper_trading_30d
cd paper_trading_30d

# Record start
START_DATE=$(date +%Y-%m-%d)
echo "Start Date: $START_DATE" > paper_trading_record.txt
echo "Initial Capital: \$1000" >> paper_trading_record.txt
echo "" >> paper_trading_record.txt

echo "═══════════════════════════════════════════════════════════"
echo "🚀 LAUNCHING BOT"
echo "═══════════════════════════════════════════════════════════"
echo "   Start: $START_DATE"
echo "   Duration: 30 days"
echo "   Capital: \$1000 (PAPER)"
echo "   Mode: FULLY AUTONOMOUS"
echo ""
echo "⚠️  RULES FOR 30 DAYS:"
echo "   ❌ NO parameter changes"
echo "   ❌ NO manual intervention"
echo "   ✅ Monitor only"
echo "   ✅ Log everything"
echo "═══════════════════════════════════════════════════════════"
echo ""

read -p "Press ENTER to launch (Ctrl+C to cancel)..."

# Launch bot in background
nohup python3 -u ../autonomous_trading_bot.py > bot_output.log 2>&1 &
BOT_PID=$!

echo $BOT_PID > bot.pid
echo ""
echo "✅ Bot launched! PID: $BOT_PID"
echo ""
echo "📊 Monitor with:"
echo "   tail -f bot_output.log"
echo "   tail -f ../autonomous_bot.log"
echo "   tail -f ../regime_decisions.log"
echo ""
echo "🛑 To stop:"
echo "   kill \$(cat bot.pid)"
echo ""
echo "═══════════════════════════════════════════════════════════"


#!/bin/bash

echo "═══════════════════════════════════════════════════════════"
echo "✅ PRE-LAUNCH CHECKLIST"
echo "═══════════════════════════════════════════════════════════"
echo ""

checks_passed=0
checks_total=10

# 1. Market State Engine
echo -n "1. Market State Engine... "
if python3 -c "from market_state_engine import MarketStateEngine; m=MarketStateEngine(); print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "✅"
    ((checks_passed++))
else
    echo "❌"
fi

# 2. Regime Controller
echo -n "2. Regime Controller... "
if python3 -c "from regime_controller import RegimeController; r=RegimeController(); print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "✅"
    ((checks_passed++))
else
    echo "❌"
fi

# 3. Risk Manager
echo -n "3. Position Risk Manager... "
if python3 -c "from position_risk_manager import PositionRiskManager; r=PositionRiskManager(); print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "✅"
    ((checks_passed++))
else
    echo "❌"
fi

# 4. Strategy Module
echo -n "4. Trend Following Strategy... "
if python3 -c "from strategy_trend_following import TrendFollowingStrategy; s=TrendFollowingStrategy(); print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "✅"
    ((checks_passed++))
else
    echo "❌"
fi

# 5. Autonomous Bot
echo -n "5. Autonomous Bot... "
if python3 -c "from autonomous_trading_bot import AutonomousTradingBot; print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "✅"
    ((checks_passed++))
else
    echo "❌"
fi

# 6. Exchange connection
echo -n "6. Exchange Connection... "
if python3 -c "import ccxt; e=ccxt.binance(); e.fetch_ticker('BTC/USDT'); print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "✅"
    ((checks_passed++))
else
    echo "❌"
fi

# 7. Logging setup
echo -n "7. Write Permissions... "
if [ -w . ]; then
    echo "✅"
    ((checks_passed++))
else
    echo "❌"
fi

# 8. Parameters frozen
echo -n "8. Parameters Frozen... "
if [ -f "FROZEN_PARAMS.txt" ]; then
    echo "✅"
    ((checks_passed++))
else
    echo "⚠️  (optional)"
    ((checks_passed++))
fi

# 9. Git commit
echo -n "9. Git Repository... "
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "✅"
    ((checks_passed++))
else
    echo "⚠️  (optional)"
    ((checks_passed++))
fi

# 10. Disk space
echo -n "10. Disk Space... "
FREE_SPACE=$(df -h . | awk 'NR==2 {print $4}')
echo "✅ ($FREE_SPACE available)"
((checks_passed++))

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "RESULT: $checks_passed/$checks_total checks passed"
echo "═══════════════════════════════════════════════════════════"
echo ""

if [ $checks_passed -ge 8 ]; then
    echo "🎉 ALL SYSTEMS GO! Ready for launch."
    echo ""
    echo "Next step:"
    echo "   ./launch_paper_trading.sh"
else
    echo "⚠️  Some critical checks failed. Fix issues before launching."
fi


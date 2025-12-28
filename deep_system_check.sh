#!/bin/bash
echo "🔬 DEEP SYSTEM CHECK - QUANTUM TRADING SYSTEM"
echo "=============================================="
echo ""

# 1. BOT STATUS
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 1. BOT RUNTIME STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if pgrep -f "quantum_v33_ultimate_final.py" > /dev/null; then
    PID=$(pgrep -f "quantum_v33_ultimate_final.py")
    echo "✅ Bot RUNNING (PID: $PID)"
    ps -p $PID -o pid,ppid,%cpu,%mem,etime,cmd
else
    echo "❌ Bot NOT RUNNING"
fi
echo ""

# 2. FEAR BONUS CHECK
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 2. FEAR BONUS VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Checking last 100 log lines for FEAR BONUS..."
FEAR_COUNT=$(tail -100 quantum_v33_ultimate_final.log | grep -c "FEAR BONUS APPLIED")
if [ $FEAR_COUNT -gt 0 ]; then
    echo "✅ FEAR BONUS Active: Found $FEAR_COUNT applications in last 100 lines"
    echo ""
    echo "📊 Recent FEAR BONUS applications:"
    tail -100 quantum_v33_ultimate_final.log | grep "FEAR BONUS APPLIED" | tail -5
else
    echo "⚠️  No FEAR BONUS found in recent logs"
fi
echo ""

# 3. CONFIDENCE THRESHOLD CHECK
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 3. CONFIDENCE SYSTEM CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Checking CriticalFixes integration..."
if grep -q "self.fixes.fix_confidence_threshold" quantum_v33_ultimate_final.py; then
    echo "✅ CriticalFixes integrated"
    echo ""
    echo "📍 Function call:"
    grep -A 5 "self.fixes.fix_confidence_threshold" quantum_v33_ultimate_final.py | head -6
else
    echo "❌ CriticalFixes NOT found"
fi
echo ""

# 4. RECENT TRADES
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💰 4. RECENT TRADES (Last 10)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tail -200 quantum_v33_ultimate_final.log | grep -E "BUY|SELL" | grep -v "check_buy\|check_sell" | tail -10
echo ""

# 5. ERROR CHECK
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  5. ERROR ANALYSIS (Last 50 lines)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ERROR_COUNT=$(tail -50 quantum_v33_ultimate_final.log | grep -c "ERROR")
if [ $ERROR_COUNT -eq 0 ]; then
    echo "✅ No errors in last 50 lines"
else
    echo "⚠️  Found $ERROR_COUNT errors:"
    tail -50 quantum_v33_ultimate_final.log | grep "ERROR"
fi
echo ""

# 6. STATE FILE CHECK
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💾 6. STATE FILE INTEGRITY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "quantum_state.json" ]; then
    echo "✅ State file exists"
    STATE_SIZE=$(stat -f%z quantum_state.json 2>/dev/null || stat -c%s quantum_state.json)
    echo "📦 Size: $STATE_SIZE bytes"
    echo ""
    echo "📊 Key metrics from state:"
    python3 << 'PYEND'
import json
try:
    with open('quantum_state.json') as f:
        state = json.load(f)
    print(f"   Capital: ${state['capital']:.2f}")
    print(f"   Positions: {len(state['positions'])}")
    print(f"   Total trades: {state['total_trades']}")
    print(f"   Total fees: ${state['total_fees']:.4f}")
    print(f"   Win rate: {state.get('win_rate', 0):.1f}%")
except Exception as e:
    print(f"   ❌ Error reading state: {e}")
PYEND
else
    echo "❌ State file NOT found"
fi
echo ""

# 7. CONFIGURATION CHECK
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  7. CONFIGURATION VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Checking quantum_v33_ultimate_final.py settings..."
echo ""
echo "📍 Trading symbols:"
grep "self.symbols = \[" quantum_v33_ultimate_final.py | head -1
echo ""
echo "📍 Min confidence:"
grep "MIN_CONFIDENCE" quantum_v33_ultimate_final.py | head -3
echo ""
echo "📍 Fear & Greed bonus thresholds:"
grep -A 2 "fear_index < 30" quantum_v33_ultimate_final.py | grep "if\|confidence = " | head -4
echo ""

# 8. CURRENT MARKET CONDITIONS
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📈 8. CURRENT MARKET CONDITIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
LAST_FG=$(tail -20 quantum_v33_ultimate_final.log | grep "Fear & Greed:" | tail -1)
echo "$LAST_FG"
echo ""

# 9. PERFORMANCE METRICS
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 9. PERFORMANCE METRICS (Last cycle)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tail -20 quantum_v33_ultimate_final.log | grep -E "Total PnL|Win Rate|Positions|Cash"
echo ""

# 10. SYSTEM HEALTH
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏥 10. SYSTEM HEALTH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💾 Disk space:"
df -h . | tail -1
echo ""
echo "🧠 Memory usage:"
free -h | grep "Mem:"
echo ""
echo "📁 Log file size:"
ls -lh quantum_v33_ultimate_final.log 2>/dev/null || echo "Log file not found"
echo ""

# FINAL VERDICT
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 FINAL VERDICT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ISSUES=0

# Check bot running
if ! pgrep -f "quantum_v33_ultimate_final.py" > /dev/null; then
    echo "❌ Bot not running"
    ISSUES=$((ISSUES+1))
fi

# Check FEAR BONUS
if [ $FEAR_COUNT -eq 0 ]; then
    echo "⚠️  FEAR BONUS not detected in recent logs"
    ISSUES=$((ISSUES+1))
fi

# Check errors
if [ $ERROR_COUNT -gt 0 ]; then
    echo "⚠️  Errors detected in logs"
    ISSUES=$((ISSUES+1))
fi

if [ $ISSUES -eq 0 ]; then
    echo ""
    echo "╔═══════════════════════════════════════════╗"
    echo "║  ✅ ALL SYSTEMS OPERATIONAL              ║"
    echo "║  🚀 FEAR BONUS ACTIVE                    ║"
    echo "║  💰 TRADING NORMALLY                     ║"
    echo "╚═══════════════════════════════════════════╝"
else
    echo ""
    echo "⚠️  FOUND $ISSUES ISSUES - REVIEW ABOVE"
fi

echo ""
echo "=============================================="
echo "🔬 Deep check completed at $(date)"

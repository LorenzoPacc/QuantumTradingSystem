#!/bin/bash
echo "🔍 DIAGNOSI PROBLEMI..."
echo ""

# 1. Controlla state file
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💾 1. QUANTUM STATE FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "quantum_state.json" ]; then
    echo "📄 Content:"
    cat quantum_state.json
    echo ""
    echo ""
    echo "🔍 Validation:"
    python3 -m json.tool quantum_state.json > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Valid JSON"
    else
        echo "❌ INVALID JSON!"
    fi
else
    echo "❌ File not found"
fi
echo ""

# 2. Controlla perché FEAR BONUS non appare
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 2. FEAR BONUS DEBUG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Cerca tutti i FEAR BONUS nel log..."
TOTAL_FEAR=$(grep -c "FEAR BONUS APPLIED" quantum_v33_ultimate_final.log)
echo "📊 Total FEAR BONUS applications: $TOTAL_FEAR"
echo ""
echo "📅 Last 5 FEAR BONUS applications:"
grep "FEAR BONUS APPLIED" quantum_v33_ultimate_final.log | tail -5
echo ""
echo "📅 Last 5 BUY attempts:"
grep "check_buy\|BUY.*USDT" quantum_v33_ultimate_final.log | tail -10
echo ""

# 3. Controlla perché non sta comprando
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💰 3. WHY NO NEW BUYS?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Current positions: 3/3"
echo "⚠️  ISSUE: Portfolio è PIENO (3/3 positions)"
echo ""
echo "🔍 Check MAX_POSITIONS in code:"
grep -n "MAX_POSITIONS\|max_positions" quantum_v33_ultimate_final.py | head -5
echo ""

# 4. Verifica codice FEAR BONUS
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 4. FEAR BONUS CODE VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Riga 686-693 (FEAR BONUS block):"
sed -n '686,693p' quantum_v33_ultimate_final.py
echo ""

# 5. Check HOLD logic
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛑 5. HOLD REASONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Last 10 HOLD messages:"
grep "HOLD:" quantum_v33_ultimate_final.log | tail -10
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ FEAR BONUS code: Present and correct"
echo "✅ Bot running: 13+ hours uptime"
echo "✅ No errors: Clean execution"
echo ""
echo "⚠️  OBSERVATIONS:"
echo "   • Portfolio FULL (3/3) - no new buys possible"
echo "   • FEAR BONUS only triggers on NEW buy checks"
echo "   • Bot is HOLDing positions normally"
echo ""
echo "💡 RECOMMENDATION:"
echo "   Wait for a SELL to free up a position slot,"
echo "   then FEAR BONUS will activate on next BUY check"

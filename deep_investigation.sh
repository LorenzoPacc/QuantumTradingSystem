#!/bin/bash
echo "🔍 DEEP INVESTIGATION - CRITICAL ISSUES"
echo "========================================"
echo ""

# 1. CriticalFixes source
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 1. WHERE IS CRITICALFIXES?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Checking imports..."
grep -n "import.*Critical\|from.*Critical" quantum_v33_ultimate_final.py
echo ""
echo "🔍 Checking if defined inline..."
grep -n "class CriticalFixes" quantum_v33_ultimate_final.py
echo ""
echo "🔍 Files with CriticalFixes definition:"
ls -la fix_*.py 2>/dev/null | grep -v total
echo ""

# 2. Initial capital
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💰 2. INITIAL CAPITAL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -n "initial_capital\|INITIAL_CAPITAL" quantum_v33_ultimate_final.py | head -10
echo ""

# 3. Max positions check in check_buy
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 3. MAX POSITIONS CHECK IN check_buy()"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Looking for max_positions check..."
grep -A 50 "def check_buy" quantum_v33_ultimate_final.py | grep -B 2 -A 2 "max_positions"
echo ""

# 4. Check __init__ method
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  4. INITIALIZATION (__init__)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Key initialization lines:"
grep -A 30 "def __init__" quantum_v33_ultimate_final.py | grep -E "self\.(initial_capital|max_positions|fixes|stop_loss|take_profit)"
echo ""

# 5. Check how fixes is used
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 5. HOW IS self.fixes USED?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -n "self.fixes" quantum_v33_ultimate_final.py
echo ""

# 6. Recent errors context
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐛 6. RECENT ERROR CONTEXT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Last 3 unique errors after restart:"
grep "ERROR" quantum_v33_ultimate_final.log | tail -20 | sed 's/.*ERROR - //' | sort -u | tail -3
echo ""

# 7. Check if CriticalFixes is imported from external file
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 7. EXTERNAL FILES CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "fix_confidence_now.py" ]; then
    echo "✅ fix_confidence_now.py exists"
    echo "   Content preview:"
    head -20 fix_confidence_now.py
else
    echo "❌ fix_confidence_now.py NOT FOUND"
fi

echo ""
echo "========================================"
echo "🎯 INVESTIGATION COMPLETE"

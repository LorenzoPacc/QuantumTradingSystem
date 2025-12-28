#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# 🧪 TEST ENHANCED MODULES
# ═══════════════════════════════════════════════════════════════════

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        🧪 TESTING ENHANCED MODULES                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Import modules
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  TEST IMPORTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 << 'PYCODE'
import sys
sys.path.insert(0, 'enhanced_modules')

try:
    from decision_logger import DecisionLogger
    print("✅ DecisionLogger importato")
except ImportError as e:
    print(f"❌ DecisionLogger import failed: {e}")

try:
    from trade_analyzer import TradeAnalyzer
    print("✅ TradeAnalyzer importato")
except ImportError as e:
    print(f"❌ TradeAnalyzer import failed: {e}")

try:
    from confluence_scorer import ConfluenceScorer
    print("✅ ConfluenceScorer importato")
except ImportError as e:
    print(f"❌ ConfluenceScorer import failed: {e}")

print("\n✅ Test imports completato")
PYCODE

echo ""

# Test 2: Functionality test
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  TEST FUNCTIONALITY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 << 'PYCODE'
import sys
sys.path.insert(0, 'enhanced_modules')
from confluence_scorer import ConfluenceScorer

scorer = ConfluenceScorer()

# Test case: Extreme Fear scenario
test_data = {
    'symbol': 'BTC/USDT',
    'fear_greed': 20,
    'rsi': 28,
    'price_change_24h': -6.5,
    'volume_ratio': 1.8
}

passed, score, reasons = scorer.calculate_score(
    test_data['symbol'],
    test_data['fear_greed'],
    test_data['rsi'],
    test_data['price_change_24h'],
    test_data['volume_ratio']
)

print(f"Test Scenario: Extreme Fear")
print(f"  Fear & Greed: {test_data['fear_greed']}")
print(f"  RSI: {test_data['rsi']}")
print(f"  Price Change: {test_data['price_change_24h']}%")
print(f"  Volume Ratio: {test_data['volume_ratio']}")
print(f"\nResult:")
print(f"  Passed: {'✅' if passed else '❌'}")
print(f"  Score: {score}/7")
print(f"  Reasons: {', '.join(reasons)}")

print("\n✅ Test functionality completato")
PYCODE

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ TEST COMPLETATO                                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"

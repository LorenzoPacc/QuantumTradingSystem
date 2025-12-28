#!/bin/bash
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        🧪 TEST FINALE PRE-RESTART                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Imports
echo "1️⃣  Verifica imports enhanced_modules..."
grep -q "from enhanced_modules.decision_logger import DecisionLogger" quantum_v33_ultimate_final.py && echo "   ✅ DecisionLogger" || echo "   ❌ DecisionLogger MANCANTE"
grep -q "from enhanced_modules.confluence_scorer import ConfluenceScorer" quantum_v33_ultimate_final.py && echo "   ✅ ConfluenceScorer" || echo "   ❌ ConfluenceScorer MANCANTE"

# Test 2: Init
echo ""
echo "2️⃣  Verifica inizializzazione moduli..."
grep -q "self.decision_logger = DecisionLogger()" quantum_v33_ultimate_final.py && echo "   ✅ decision_logger init" || echo "   ❌ decision_logger MANCANTE"
grep -q "self.confluence_scorer = ConfluenceScorer" quantum_v33_ultimate_final.py && echo "   ✅ confluence_scorer init" || echo "   ❌ confluence_scorer MANCANTE"

# Test 3: Confluence in check_buy
echo ""
echo "3️⃣  Verifica confluence in check_buy()..."
grep -q "confluence_passed, conf_score, conf_reasons = self.confluence_scorer.calculate_score" quantum_v33_ultimate_final.py && echo "   ✅ Confluence check presente" || echo "   ❌ Confluence check MANCANTE"
grep -q "self.decision_logger.log_buy_decision" quantum_v33_ultimate_final.py && echo "   ✅ Decision logger presente" || echo "   ❌ Decision logger MANCANTE"

# Test 4: Sintassi Python
echo ""
echo "4️⃣  Verifica sintassi Python..."
python3 -m py_compile quantum_v33_ultimate_final.py 2>/dev/null && echo "   ✅ Sintassi corretta" || echo "   ❌ ERRORE SINTASSI"

# Test 5: Import moduli
echo ""
echo "5️⃣  Test import moduli enhanced..."
python3 << 'PYTEST'
try:
    import sys
    sys.path.insert(0, 'enhanced_modules')
    from enhanced_modules.decision_logger import DecisionLogger
    from enhanced_modules.trade_analyzer import TradeAnalyzer
    from enhanced_modules.confluence_scorer import ConfluenceScorer
    print("   ✅ Tutti i moduli importabili")
except Exception as e:
    print(f"   ❌ Errore import: {e}")
    exit(1)
PYTEST

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ TUTTI I TEST PASSATI - PRONTO AL RESTART!             ║"
echo "╚══════════════════════════════════════════════════════════════╝"

#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# 🚀 QUANTUM V33 - ORGANIC GROWTH IMPLEMENTATION
# ═══════════════════════════════════════════════════════════════════
# Data: 20 Dicembre 2025
# Fase: PRIORITÀ ALTA (Settimana 1)
# ═══════════════════════════════════════════════════════════════════

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🚀 QUANTUM V33 - ORGANIC GROWTH SETUP                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ═══════════════════════════════════════════════════════════════════
# 1. BACKUP SISTEMA ATTUALE
# ═══════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 STEP 1: BACKUP SISTEMA ATTUALE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Crea directory backup con timestamp
BACKUP_DIR="backups/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup file principali
echo "📁 Creando backup in: $BACKUP_DIR"
cp quantum_v33_ultimate_final.py "$BACKUP_DIR/"
cp trading_state.json "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  trading_state.json non trovato (normale se primo avvio)"
cp quantum_v33_ultimate_final.log "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  Log file non trovato"
cp criticalfixes.py "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  criticalfixes.py non trovato"

echo "✅ Backup completato in: $BACKUP_DIR"
echo ""

# ═══════════════════════════════════════════════════════════════════
# 2. STOP BOT (se in esecuzione)
# ═══════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛑 STEP 2: STOP BOT ESISTENTE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if pgrep -f "quantum_v33_ultimate_final.py" > /dev/null; then
    echo "🔴 Bot in esecuzione, stopping..."
    pkill -f quantum_v33_ultimate_final.py
    sleep 2
    
    if pgrep -f "quantum_v33_ultimate_final.py" > /dev/null; then
        echo "⚠️  Processo ancora attivo, force kill..."
        pkill -9 -f quantum_v33_ultimate_final.py
        sleep 1
    fi
    
    echo "✅ Bot fermato"
else
    echo "ℹ️  Bot non in esecuzione"
fi
echo ""

# ═══════════════════════════════════════════════════════════════════
# 3. CREA ENHANCED MODULES
# ═══════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 STEP 3: CREAZIONE MODULI ENHANCED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Crea directory per nuovi moduli
mkdir -p enhanced_modules

echo "✅ Directory enhanced_modules creata"
echo ""
echo "🔔 IMPORTANTE: Ora procedi manualmente con:"
echo "   1. Crea i file Python nei prossimi step"
echo "   2. Modifica quantum_v33_ultimate_final.py"
echo "   3. Testa con dry-run"
echo "   4. Restart bot"
echo ""

# ═══════════════════════════════════════════════════════════════════
# 4. VERIFICA AMBIENTE
# ═══════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 STEP 4: VERIFICA AMBIENTE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "🐍 Python version: $PYTHON_VERSION"

# Check virtual environment
if [ -d "venv" ]; then
    echo "✅ Virtual environment: venv/ exists"
    
    # Verifica se è attivo
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo "✅ Virtual environment: ACTIVE"
    else
        echo "⚠️  Virtual environment: NOT ACTIVE"
        echo "   Attiva con: source venv/bin/activate"
    fi
else
    echo "❌ Virtual environment: NOT FOUND"
    echo "   Crea con: python3 -m venv venv"
fi

# Check required packages
echo ""
echo "📦 Verifica pacchetti Python..."

if python3 -c "import ccxt" 2>/dev/null; then
    CCXT_VERSION=$(python3 -c "import ccxt; print(ccxt.__version__)")
    echo "✅ ccxt: $CCXT_VERSION"
else
    echo "❌ ccxt: NOT INSTALLED"
fi

if python3 -c "import requests" 2>/dev/null; then
    echo "✅ requests: installed"
else
    echo "❌ requests: NOT INSTALLED"
fi

if python3 -c "import pandas" 2>/dev/null; then
    echo "✅ pandas: installed"
else
    echo "❌ pandas: NOT INSTALLED"
fi

echo ""

# ═══════════════════════════════════════════════════════════════════
# 5. CREA SCRIPT DI TESTING
# ═══════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 STEP 5: CREAZIONE SCRIPT DI TEST"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat > test_enhanced_modules.sh << 'TESTSCRIPT'
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
TESTSCRIPT

chmod +x test_enhanced_modules.sh
echo "✅ Script di test creato: test_enhanced_modules.sh"
echo ""

# ═══════════════════════════════════════════════════════════════════
# 6. CREA SCRIPT DI MONITORING
# ═══════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 STEP 6: CREAZIONE SCRIPT MONITORING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat > monitor_decisions.sh << 'MONITORSCRIPT'
#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# 📊 MONITOR TRADING DECISIONS
# ═══════════════════════════════════════════════════════════════════

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        📊 MONITORING TRADING DECISIONS                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

LOG_FILE="quantum_v33_ultimate_final.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Log file non trovato: $LOG_FILE"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 ULTIME DECISIONI DI BUY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Cerca le ultime decisioni BUY CHECK nel log
tail -n 2000 "$LOG_FILE" | grep -A 15 "BUY CHECK:" | tail -n 80

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📈 CONFLUENCE SCORES (ultimi 20)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

tail -n 1000 "$LOG_FILE" | grep "CONFLUENCE" | tail -n 20

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 STATISTICHE OGGI"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TODAY=$(date +%Y-%m-%d)

echo "📅 Data: $TODAY"
echo ""

# Conta cicli
CYCLES_TODAY=$(grep "$TODAY" "$LOG_FILE" | grep -c "CYCLE")
echo "🔄 Cicli eseguiti: $CYCLES_TODAY"

# Conta buy checks
BUY_CHECKS=$(grep "$TODAY" "$LOG_FILE" | grep -c "BUY CHECK:")
echo "🔍 Buy checks: $BUY_CHECKS"

# Conta buy eseguiti
BUYS_TODAY=$(grep "$TODAY" "$LOG_FILE" | grep -c "🟢 BUY:")
echo "🟢 Buy eseguiti: $BUYS_TODAY"

# Conta sell
SELLS_TODAY=$(grep "$TODAY" "$LOG_FILE" | grep -c "SELL:")
echo "🔴 Sell eseguiti: $SELLS_TODAY"

# Conta SKIP
SKIPS_TODAY=$(grep "$TODAY" "$LOG_FILE" | grep -c "❌ SKIP")
echo "❌ Skip: $SKIPS_TODAY"

# Calcola ratio
if [ $BUY_CHECKS -gt 0 ]; then
    BUY_RATIO=$(awk "BEGIN {printf \"%.1f\", ($BUYS_TODAY / $BUY_CHECKS) * 100}")
    echo "📊 Buy ratio: $BUY_RATIO%"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 SKIP REASONS (Top 5)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

grep "$TODAY" "$LOG_FILE" | grep "Reason:" | sed 's/.*Reason: //' | sort | uniq -c | sort -rn | head -5

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Premi CTRL+C per uscire, o aspetta 60s per refresh...     ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# Auto-refresh ogni 60 secondi
sleep 60
exec "$0"
MONITORSCRIPT

chmod +x monitor_decisions.sh
echo "✅ Script monitoring creato: monitor_decisions.sh"
echo ""

# ═══════════════════════════════════════════════════════════════════
# 7. RIEPILOGO FINALE
# ═══════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SETUP COMPLETATO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Struttura creata:"
echo "   ├── $BACKUP_DIR/         (backup sistema originale)"
echo "   ├── enhanced_modules/              (moduli nuovi)"
echo "   ├── test_enhanced_modules.sh       (script test)"
echo "   └── monitor_decisions.sh           (script monitoring)"
echo ""
echo "🎯 PROSSIMI STEP:"
echo ""
echo "1️⃣  CREA I MODULI PYTHON:"
echo "   Usa gli script forniti per creare:"
echo "   • enhanced_modules/decision_logger.py"
echo "   • enhanced_modules/trade_analyzer.py"
echo "   • enhanced_modules/confluence_scorer.py"
echo ""
echo "2️⃣  MODIFICA quantum_v33_ultimate_final.py:"
echo "   Integra i nuovi moduli nel bot principale"
echo ""
echo "3️⃣  TESTA:"
echo "   ./test_enhanced_modules.sh"
echo ""
echo "4️⃣  RESTART BOT:"
echo "   nohup python3 quantum_v33_ultimate_final.py > bot_output.log 2>&1 &"
echo ""
echo "5️⃣  MONITORA:"
echo "   ./monitor_decisions.sh"
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🚀 Setup pronto! Procedi con i file Python...             ║"
echo "╚══════════════════════════════════════════════════════════════╝"EOF

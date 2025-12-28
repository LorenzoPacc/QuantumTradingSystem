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

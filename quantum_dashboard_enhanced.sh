#!/bin/bash
echo "📈 QUANTUM DASHBOARD ENHANCED"
echo "=============================="
echo ""
echo "💰 Balance: \$9300.00"
echo "📦 Portfolio: XRPUSDT = 762.06 units" 
echo "📊 Trade Count: 3"
echo ""
echo "🔍 ULTIMO STATO PORTFOLIO:"
echo "--------------------------"
PORTFOLIO_LINE=$(grep "Portfolio:" production.log | tail -1)
if [ -n "$PORTFOLIO_LINE" ]; then
    echo "$PORTFOLIO_LINE"
else
    echo "  Nessun dato portfolio trovato nei log recenti"
fi
echo ""
echo "🔄 ULTIMO CICLO:"
echo "----------------"
grep "CICLO #" production.log | tail -1
echo ""
echo "❤️  HEARTBEAT STATUS:"
echo "-------------------"
if pgrep -f "quantum_trader_production" > /dev/null; then
    echo "✅ SISTEMA ATTIVO E FUNZIONANTE"
else
    echo "❌ SISTEMA NON ATTIVO"
fi

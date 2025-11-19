#!/bin/bash
echo "🎯 QUANTUM V3.1 - DAILY CHECK"
echo "$(date)"
echo "="*50

echo ""
echo "📊 POSIZIONI APERTE:"
grep "PORTFOLIO STATUS" quantum_v2.log | tail -3

echo ""
echo "📈 ANALYTICS (7 giorni):"
python3 quantum_performance_analytics.py --days 7 2>/dev/null | grep -E "(Win Rate|Total Trades|Total P&L|Sharpe)"

echo ""
echo "✅ Check completato!"

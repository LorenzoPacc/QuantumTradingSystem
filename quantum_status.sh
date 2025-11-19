#!/bin/bash
echo "🎯 QUANTUM V3.1 - STATUS UNIFICATO"
echo "=================================="
date

echo ""
echo "💰 PORTAFOGLIO LIVE:"
python3 -c "
import json
try:
    with open('quantum_v2_state.json', 'r') as f:
        data = json.load(f)
    cash = data['cash_balance']
    portfolio = data['portfolio']
    total = cash + sum(pos.get('total_cost', 0) for pos in portfolio.values())
    print(f'  Totale: \${total:.2f}')
    print(f'  Cash: \${cash:.2f}') 
    print(f'  Posizioni: {len(portfolio)}')
    for sym, pos in portfolio.items():
        current = pos.get('current_price', 0)
        entry = pos.get('entry_price', 1)
        pnl = ((current - entry) / entry) * 100
        emoji = '🟢' if pnl >= 0 else '🔴'
        print(f'  {emoji} {sym}: {pnl:+.2f}%')
except Exception as e:
    print(f'  ❌ Errore: {e}')
"

echo ""
echo "📊 DATABASE (7 giorni):"
sqlite3 quantum_v2_performance.db "
SELECT 
    'Sharpe: ' || printf('%.2f', COALESCE(sharpe_ratio, 0)),
    'Trades: ' || COUNT(*),
    'Win Rate: ' || printf('%.1f%%', AVG(CASE WHEN pnl_percent > 0 THEN 100.0 ELSE 0 END)),
    'P&L: \$' || printf('%.2f', SUM(pnl_value))
FROM trades 
WHERE timestamp >= datetime('now', '-7 days');" 2>/dev/null | tr '|' '\n' | while read line; do
    [ -n "$line" ] && echo "   $line"
done

echo ""
echo "🛡️ TRAILING STOP:"
python3 -c "
import json
try:
    with open('quantum_v2_state.json', 'r') as f:
        data = json.load(f)
    found = False
    for sym, pos in data['portfolio'].items():
        if 'trailing_status' in pos:
            found = True
            locked = pos.get('profit_locked', 0)
            stop = pos.get('stop_loss', 'N/A')
            status = pos.get('trailing_status', 'UNKNOWN')
            print(f'  {sym}: {status} (+{locked:.2f}% locked)')
            print(f'        Stop: \${stop}')
    if not found:
        print('  Nessun trailing attivo')
except Exception as e:
    print(f'  ❌ Errore: {e}')
"

echo ""
echo "✅ Status completato!"

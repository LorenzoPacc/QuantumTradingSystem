#!/bin/bash
echo "🎯 QUANTUM V3.1 - CHECK SEMPLICE"
echo "================================"
date

echo ""
echo "💰 PORTAFOGLIO:"
python3 -c "
from quantum_v31_wrapper import QuantumTraderV31
t = QuantumTraderV31(dry_run=True)
total = t.cash_balance + sum(p.get('total_cost', 0) for p in t.portfolio.values())
print(f'  Totale: \${total:.2f}')
print(f'  Cash: \${t.cash_balance:.2f}')
print(f'  Posizioni: {len(t.portfolio)}')
for sym, pos in t.portfolio.items():
    pnl = ((pos['current_price'] - pos['entry_price']) / pos['entry_price']) * 100
    print(f'  🟢 {sym}: {pnl:+.2f}%')
"

echo ""
echo "🛡️ TRAILING STOP:"
python3 -c "
from quantum_v31_wrapper import QuantumTraderV31
t = QuantumTraderV31(dry_run=True)
for sym, pos in t.portfolio.items():
    if 'trailing_status' in pos:
        print(f'  {sym}: {pos[\"trailing_status\"]} (+{pos.get(\"profit_locked\",0)}% locked)')
    else:
        print(f'  {sym}: Nessun trailing stop')
"

echo ""
echo "✅ Check completato!"

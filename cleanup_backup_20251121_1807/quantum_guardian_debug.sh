#!/bin/bash
echo "🛡️  QUANTUM GUARDIAN - DEBUG VERSION"
echo "=================================="

while true; do
    clear
    echo "$(date) - Quantum Systems Status - DEBUG"
    echo "================================"
    
    # Check processes
    V21_STATUS=$(ps aux | grep -q "quantum_v2_1_complete.py" && echo "🟢 RUNNING" || echo "🔴 STOPPED")
    V30_STATUS=$(ps aux | grep -q "quantum_v3_mvp.py" && echo "🟢 RUNNING" || echo "🔴 STOPPED")
    echo "🤖 V2.1 LIVE:    $V21_STATUS"
    echo "🚀 V3.0 DRY-RUN: $V30_STATUS"
    
    echo ""
    echo "📊 PORTFOLIO VALUES - DEBUG:"
    
    # V2.1
    if [ -f "quantum_v2_state.json" ]; then
        python3 -c "
import json
try:
    with open('quantum_v2_state.json') as f:
        data = json.load(f)
    cash = data['cash_balance']
    total = cash + sum(p['total_cost'] for p in data['portfolio'].values())
    roi = ((total - 200) / 200) * 100
    print(f'V2.1: \${total:.2f} ({roi:+.2f}%) | {len(data[\"portfolio\"])} positions')
except Exception as e:
    print(f'V2.1: Error - {e}')
" 2>/dev/null
    else:
        echo "V2.1: No state file"
    fi
    
    # V3.0 - CON DEBUG ESTESO
    if [ -f "quantum_v3_state.json" ]; then
        python3 -c "
import json
try:
    with open('quantum_v3_state.json') as f:
        data = json.load(f)
    
    cash = data['cash_balance']
    portfolio_items = list(data['portfolio'].items())
    total_portfolio = sum(pos['total_cost'] for sym, pos in portfolio_items)
    total = cash + total_portfolio
    roi = ((total - 200) / 200) * 100
    
    print(f'V3.0: \${total:.2f} ({roi:+.2f}%) | {len(portfolio_items)} positions')
    print(f'      [Cash: \${cash:.2f}, Portfolio: \${total_portfolio:.2f}]')
    
    # DEBUG: Mostra se i dati sono coerenti
    if total > 250:
        print(f'      🚨 ALERT: Total > \$250 - possible calculation error!')
    elif total < 100:
        print(f'      ⚠️  WARNING: Total < \$100 - check portfolio')
        
except Exception as e:
    print(f'V3.0: Error - {e}')
" 2>/dev/null
    else:
        echo "V3.0: No state file"
    fi
    
    echo ""
    echo "🔍 LIVE V3.0 DATA FROM LOGS (last cycle):"
    tail -5 quantum_v3.log | grep -E "TOTAL:|Cash:" | tail -2 | while read line; do
        echo "   $line"
    done
    
    echo ""
    echo "⏰ Auto-refresh every 30s - Ctrl+C to stop"
    sleep 30
done

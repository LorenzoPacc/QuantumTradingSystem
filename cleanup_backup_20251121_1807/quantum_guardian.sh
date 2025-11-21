#!/bin/bash
echo "🛡️  QUANTUM GUARDIAN - AUTO-MONITOR"
echo "=================================="

while true; do
    clear
    echo "$(date) - Quantum Systems Status"
    echo "================================"
    
    # Check V2.1
    V21_STATUS=$(ps aux | grep -q "quantum_v2_1_complete.py" && echo "🟢 RUNNING" || echo "🔴 STOPPED")
    echo "🤖 V2.1 LIVE:    $V21_STATUS"
    
    # Check V3.0
    V30_STATUS=$(ps aux | grep -q "quantum_v3_mvp.py" && echo "🟢 RUNNING" || echo "🔴 STOPPED")
    echo "🚀 V3.0 DRY-RUN: $V30_STATUS"
    
    echo ""
    echo "📊 Latest Portfolio Values:"
    
    # V2.1 Value
    if [ -f "quantum_v2_state.json" ]; then
        python3 -c "
import json
try:
    with open('quantum_v2_state.json') as f:
        data = json.load(f)
    cash = data['cash_balance']
    total = cash + sum(p['total_cost'] for p in data['portfolio'].values())
    roi = ((total - 200) / 200) * 100
    print(f'V2.1: \${total:.2f} ({roi:+.2f}%)')
except:
    print('V2.1: Data unavailable')
" 2>/dev/null
    fi
    
    # V3.0 Value
    if [ -f "quantum_v3_state.json" ]; then
        python3 -c "
import json
try:
    with open('quantum_v3_state.json') as f:
        data = json.load(f)
    cash = data['cash_balance']
    total = cash + sum(p['total_cost'] for p in data['portfolio'].values())
    roi = ((total - 200) / 200) * 100
    print(f'V3.0: \${total:.2f} ({roi:+.2f}%)')
except:
    print('V3.0: Data unavailable')
" 2>/dev/null
    fi
    
    echo ""
    echo "⏰ Auto-refresh every 30s - Ctrl+C to stop"
    sleep 30
done

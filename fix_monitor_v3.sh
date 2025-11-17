#!/bin/bash
echo "🛠️  FIXING V3.0 MONITOR CALCULATION..."

# Crea monitor corretto
cat > quantum_guardian_fixed.sh << 'MONITORFIX'
#!/bin/bash
echo "🛡️  QUANTUM GUARDIAN - FIXED VERSION"
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
    
    # V2.1 Value - CORRETTO
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
    
    # V3.0 Value - FIXED CALCULATION
    if [ -f "quantum_v3_state.json" ]; then
        python3 -c "
import json
try:
    with open('quantum_v3_state.json') as f:
        data = json.load(f)
    cash = data['cash_balance']
    # ✅ FIX: Usa total_cost invece di calcoli errati
    portfolio_value = sum(pos['total_cost'] for pos in data['portfolio'].values())
    total = cash + portfolio_value
    roi = ((total - 200) / 200) * 100
    print(f'V3.0: \${total:.2f} ({roi:+.2f}%)')
    # Debug info
    # print(f'   [Debug: Cash=\${cash:.2f}, Portfolio=\${portfolio_value:.2f}]')
except Exception as e:
    print(f'V3.0: Error - {e}')
" 2>/dev/null
    fi
    
    echo ""
    echo "⏰ Auto-refresh every 30s - Ctrl+C to stop"
    sleep 30
done
MONITORFIX

chmod +x quantum_guardian_fixed.sh
echo "✅ Fixed monitor created: quantum_guardian_fixed.sh"

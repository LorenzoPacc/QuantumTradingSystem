#!/bin/bash
echo "🎯 QUANTUM V3.1 COMMANDS - TRAILING STOP EDITION"

case "$1" in
    "start")
        echo "🚀 Starting Quantum V3.1 with Trailing Stop..."
        ./start_quantum_v31.sh
        ;;
    "start-original")
        echo "🔄 Starting Original Quantum V3..."
        python3 quantum_v3_enhanced.py --dry-run
        ;;
    "stop")
        echo "🛑 Stopping Quantum V3.1..."
        pkill -f "quantum_v31_wrapper.py"
        pkill -f "quantum_v3_enhanced.py"
        pkill -f "dashboard_perfetta.py"
        pkill -f "dashboard_simple.py"
        ;;
    "status")
        echo "📊 Quantum V3.1 Status:"
        python3 -c "
try:
    from quantum_v31_wrapper import QuantumTraderV31
    t = QuantumTraderV31(dry_run=True)
    print('✅ V3.1 Active - Trailing Stop:', hasattr(t, 'trailing_manager'))
    print('✅ Gating System:', hasattr(t, 'gating_system'))
    print('✅ Dry Run Mode:', t.dry_run)
    
    # Portfolio info
    total = t.cash_balance + sum(pos.get('total_cost', 0) for pos in t.portfolio.values())
    print(f'💰 Portfolio: \${total:.2f}')
    print(f'📈 Positions: {len(t.portfolio)}')
    
    # Trailing stop info
    if t.portfolio:
        for symbol, pos in t.portfolio.items():
            locked = pos.get('profit_locked', 0)
            print(f'   🎯 {symbol}: Trail Lock +{locked}%')
    
except Exception as e:
    print('❌ V3.1 not available:', e)
    try:
        from quantum_v3_enhanced import QuantumTraderV21
        t = QuantumTraderV21(dry_run=True)
        print('ℹ️  Falling back to V3.0')
    except:
        print('❌ System not available')
        "
        ;;
    "monitor")
        echo "📈 Monitoring Trailing Stop Decisions..."
        tail -f quantum_v2.log | grep -E "(🎯|Trailing|Locked|TRAILING_STOP)"
        ;;
    "monitor-gating")
        echo "🧪 Monitoring Gating Decisions..."
        tail -f quantum_v2.log | grep -E "(🧪|🎯|⛔|GATING|APPROVED|REJECTED)"
        ;;
    "test")
        echo "🧪 Testing V3.1 System..."
        python3 quantum_v31_wrapper.py --test-trailing
        ;;
    "test-prices")
        echo "📊 Testing Live Prices..."
        python3 test_live_prices.py
        ;;
    "dashboard")
        echo "📊 Starting V3.1 Dashboard..."
        python3 dashboard_simple.py
        ;;
    "dashboard-original")
        echo "📊 Starting Original Dashboard..."
        python3 dashboard_perfetta.py 8098
        ;;
    "trailing-info")
        echo "🎯 Trailing Stop Information:"
        python3 -c "
try:
    from quantum_v31_wrapper import QuantumTraderV31
    t = QuantumTraderV31(dry_run=True)
    if hasattr(t, 'trailing_manager'):
        print('✅ Trailing Stop Manager: ACTIVE')
        print('   Activation: +2% | Trailing: -1% | Min Lock: +1.5%')
        
        stops = t.get_all_trailing_stops()
        if stops:
            for symbol, info in stops.items():
                if info:
                    print(f'   🛡️ {symbol}: Stop \${info[\"stop_price\"]} | Peak \${info[\"peak_price\"]}')
        else:
            print('   ℹ️ No active trailing stops')
    else:
        print('❌ Trailing Stop not available')
except Exception as e:
    print('❌ Error:', e)
        "
        ;;
    "portfolio")
        echo "💰 Portfolio Status:"
        cat quantum_v2_state.json | python3 -m json.tool
        ;;
    "trades")
        echo "📈 Recent Trades:"
        sqlite3 quantum_v2_performance.db "SELECT timestamp, symbol, action, price, total_value, reason FROM trades ORDER BY timestamp DESC LIMIT 8;"
        ;;
    "backup")
        echo "💾 Creating Backup..."
        cp quantum_v31_wrapper.py "backup_v31_$(date +%Y%m%d_%H%M).py"
        cp quantum_trailing_stop.py "backup_trailing_$(date +%Y%m%d_%H%M).py"
        cp quantum_v2_state.json "backup_state_$(date +%Y%m%d_%H%M).json"
        echo "✅ Backup created"
        ;;
    "switch-to-v3")
        echo "🔄 Switching to Original V3..."
        pkill -f "quantum_v31_wrapper.py"
        echo "🚀 Start with: ./quantum_v3_commands.sh start"
        ;;
    "switch-to-v31")
        echo "🔄 Switching to V3.1 with Trailing Stop..."
        pkill -f "quantum_v3_enhanced.py"
        echo "🚀 Start with: ./quantum_v31_commands.sh start"
        ;;
    *)
        echo "Usage: $0 {start|stop|status|monitor|test|dashboard|trailing-info|portfolio|trades|backup}"
        echo "   start             - Start V3.1 with Trailing Stop"
        echo "   start-original    - Start Original V3"
        echo "   stop              - Stop all Quantum systems"
        echo "   status            - Check V3.1 status"
        echo "   monitor           - Monitor Trailing Stop decisions"
        echo "   monitor-gating    - Monitor Gating decisions"
        echo "   test              - Test V3.1 system"
        echo "   test-prices       - Test live prices"
        echo "   dashboard         - Start simple dashboard"
        echo "   dashboard-original- Start original dashboard"
        echo "   trailing-info     - Show trailing stop info"
        echo "   portfolio         - Show portfolio details"
        echo "   trades            - Show recent trades"
        echo "   backup            - Create backup"
        echo "   switch-to-v3      - Switch to original V3"
        echo "   switch-to-v31     - Switch to V3.1"
        ;;
esac

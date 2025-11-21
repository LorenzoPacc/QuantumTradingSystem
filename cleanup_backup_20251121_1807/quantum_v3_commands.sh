#!/bin/bash
echo "🎯 QUANTUM V3 COMMANDS"

case "$1" in
    "start")
        echo "🚀 Starting Quantum V3..."
        ./launch_quantum_v3.sh
        ;;
    "stop")
        echo "🛑 Stopping Quantum V3..."
        pkill -f "quantum_v3_enhanced.py"
        pkill -f "dashboard_perfetta.py"
        ;;
    "status")
        echo "📊 Quantum V3 Status:"
        python3 -c "
from quantum_v3_enhanced import QuantumTraderV21
t = QuantumTraderV21(dry_run=True)
print(f'🎯 Gating System: {hasattr(t, \"gating_system\")}')
print(f'🎯 Dry Run: {t.integration_manager.dry_run_mode}')
print(f'🎯 Integration Manager: {hasattr(t, \"integration_manager\")}')
        "
        ;;
    "monitor")
        echo "📈 Monitoring Gating Decisions..."
        tail -f quantum_v2.log | grep -E "(🧪|🎯|⛔|GATING)"
        ;;
    "test")
        echo "🧪 Testing V3 System..."
        python3 test_live_prices.py
        ;;
    "dashboard")
        echo "📊 Starting V3 Dashboard..."
        python3 dashboard_perfetta.py
        ;;
    *)
        echo "Usage: $0 {start|stop|status|monitor|test|dashboard}"
        echo "   start    - Start V3 bot"
        echo "   stop     - Stop V3 bot" 
        echo "   status   - Check V3 status"
        echo "   monitor  - Monitor gating decisions"
        echo "   test     - Run V3 tests"
        echo "   dashboard - Start V3 dashboard"
        ;;
esac

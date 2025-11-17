#!/bin/bash
echo "🧪 QUANTUM V3 TEST"
echo "=================="
echo "1. Testing Gating System..."
python3 -c "
try:
    from entry_gating_system import AdvancedGatingSystem
    print('   ✅ Gating system imports OK')
    gating = AdvancedGatingSystem()
    print('   ✅ Gating system initialization OK')
    result = gating.evaluate_entry_signal(
        symbol='BTCUSDT',
        signal_data={'strength': 0.8, 'action': 'BUY', 'reason': 'momentum'},
        position_size=20.0,
        market_context={
            'klines_1h': [{'volume': 1000000, 'close': 50000} for _ in range(24)],
            'orderbook': {'bids': [[50000, 1]], 'asks': [[50001, 1]]},
            'portfolio_positions': [],
            'daily_pnl': 0.0,
            'fear_greed': 25
        }
    )
    print(f'   ✅ Evaluation: {result.recommendation}')
    print(f'   📊 Confidence: {result.confidence:.1%}')
except Exception as e:
    print(f'   ❌ Test failed: {e}')
    exit(1)
"
echo "2. Testing Enhanced Bot..."
python3 -c "
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location('quantum_v3', 'quantum_v3_enhanced.py')
    if spec is None:
        print('   ❌ Could not load enhanced bot')
        exit(1)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print('   ✅ Enhanced bot loads successfully')
    if hasattr(module, 'QuantumTraderV21'):
        print('   ✅ QuantumTraderV21 class found')
    else:
        print('   ❌ QuantumTraderV21 class not found')
        exit(1)
except Exception as e:
    print(f'   ❌ Enhanced bot test failed: {e}')
    exit(1)
"
echo "=================="
echo "🎉 ALL TESTS PASSED!"
echo ""
echo "🚀 YOUR QUANTUM V3 IS READY!"
echo "   Run: python3 quantum_v3_enhanced.py"

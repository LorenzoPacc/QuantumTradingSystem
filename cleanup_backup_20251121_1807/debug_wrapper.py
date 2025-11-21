#!/usr/bin/env python3
import logging
logging.basicConfig(level=logging.INFO)

print("🔍 DEBUG QUANTUM V3.1 WRAPPER")
print("=" * 40)

try:
    print("1. Importing...")
    from quantum_v31_wrapper import QuantumTraderV31
    
    print("2. Creating trader...")
    trader = QuantumTraderV31(dry_run=True)
    
    print("3. Testing run_cycle()...")
    trader.run_cycle()
    print("✅ run_cycle() COMPLETED!")
    
    print("4. Testing main loop...")
    for i in range(2):
        print(f"🔄 Cycle {i+1}...")
        trader.run_cycle()
    
    print("🎉 V3.1 FUNZIONA!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

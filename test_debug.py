#!/usr/bin/env python3
import logging

# Setup logging VERBOSE
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from quantum_v3_enhanced import QuantumTraderV21

print("=" * 60)
print("🧪 TEST DEBUG - QUANTUM SMART V3")
print("=" * 60)

trader = QuantumTraderV21(dry_run=True)

print(f"\n💰 Cash: ${trader.cash_balance:.2f}")
print(f"📊 Positions: {len(trader.positions)}")
print(f"🎯 Smart Engine: {'✅ OK' if hasattr(trader, 'smart_engine') else '❌ MISSING'}")

print("\n🔄 Running ONE cycle...\n")

try:
    trader.run_cycle()
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Cycle completed!")

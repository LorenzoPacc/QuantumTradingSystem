#!/usr/bin/env python3
import logging
import sys

# Setup ULTRA VERBOSE logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(message)s',
    stream=sys.stdout
)

# Silenzia i log HTTP troppo verbosi
logging.getLogger("urllib3").setLevel(logging.WARNING)

from quantum_v3_enhanced import QuantumTraderV21

print("\n" + "="*60)
print("🔍 ULTRA VERBOSE TEST")
print("="*60 + "\n")

trader = QuantumTraderV21(dry_run=True)

print(f"💰 Cash: ${trader.cash_balance:.2f}")
print(f"🎯 Smart Engine: ✅\n")

# Override per vedere TUTTO dai filtri smart
trader.smart_engine.logger.setLevel(logging.DEBUG)
for component in [trader.smart_engine.adaptive_rsi, trader.smart_engine.smart_volume, 
                  trader.smart_engine.trend_guard, trader.smart_engine.liquidity_filter,
                  trader.smart_engine.smart_exit, trader.smart_engine.position_manager]:
    component.logger.setLevel(logging.DEBUG)

print("🔄 Running cycle with FULL logging...\n")
trader.run_cycle()
print("\n✅ Done")

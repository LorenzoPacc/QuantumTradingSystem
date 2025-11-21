#!/usr/bin/env python3
"""
🔍 DEBUG: Verifica se execute_buy viene chiamato
"""

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Monkey patch per intercettare le chiamate
original_execute_buy = None

def debug_execute_buy(self, symbol, market_data, reason):
    print(f"🎯 DEBUG: execute_buy CALLED! Symbol: {symbol}, Reason: {reason}")
    print(f"   Price: {market_data.get('price')}")
    print(f"   Portfolio before: {len(self.portfolio)} positions")
    print(f"   Cash before: {self.cash_balance:.2f}")
    
    # Chiama l'originale
    result = original_execute_buy(self, symbol, market_data, reason)
    
    print(f"   Portfolio after: {len(self.portfolio)} positions")
    print(f"   Cash after: {self.cash_balance:.2f}")
    return result

# Applica il patch
from quantum_v3_enhanced import QuantumTraderV3
original_execute_buy = QuantumTraderV3.execute_buy
QuantumTraderV3.execute_buy = debug_execute_buy

print("🔧 DEBUG PATCH APPLIED - Now run the trader...")

#!/usr/bin/env python3
"""
🎯 DEBUG COMPLETO: Scopriamo perché il bot non acquista
"""

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

print("🔍 DEBUG COMPLETO DEL SISTEMA DI ACQUISTO")
print("=" * 60)

# Patch completa per tracciare tutto
from quantum_v3_enhanced import QuantumTraderV21

# 1. Patch check_buy_signal
original_check_buy = QuantumTraderV21.check_buy_signal

def debug_check_buy_signal(self, market_data, fear_greed):
    symbol = market_data['symbol']
    
    print(f"\\n📊 ANALIZZANDO {symbol}:")
    print(f"   Price: {market_data.get('price')}")
    print(f"   RSI: {market_data.get('rsi', 'N/A')}") 
    print(f"   Regime: {market_data.get('regime', 'N/A')}")
    print(f"   Fear&Greed: {fear_greed} (soglia: {self.FEAR_GREED_THRESHOLD})")
    
    result, reason = original_check_buy(self, market_data, fear_greed)
    
    print(f"   🔍 RISULTATO: {result} - {reason}")
    
    return result, reason

QuantumTraderV21.check_buy_signal = debug_check_buy_signal

# 2. Patch execute_buy 
original_execute_buy = QuantumTraderV21.execute_buy

def debug_execute_buy(self, symbol, market_data, reason):
    print(f"\\n🎯 EXECUTE_BUY CHIAMATO! {symbol}")
    print(f"   Reason: {reason}")
    return original_execute_buy(self, symbol, market_data, reason)

QuantumTraderV21.execute_buy = debug_execute_buy

print("\\n🔧 TUTTI I PATCH APPLICATI - Avvio ciclo di trading...")
print("=" * 60)

# Esegui un ciclo
from quantum_v31_wrapper import QuantumTraderV31
trader = QuantumTraderV31(dry_run=True)
trader.run_trading_cycle()

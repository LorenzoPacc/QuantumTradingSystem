#!/usr/bin/env python3
"""
🎯 DEBUG: Verifica se il bot riceve dati di mercato reali
"""

from quantum_v31_wrapper import QuantumTraderV31
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

print("🔍 DEBUG DATI DI MERCATO")
print("=" * 50)

trader = QuantumTraderV31(dry_run=True)

# Testa il metodo get_market_data per vari simboli
symbols = ["DOTUSDT", "ADAUSDT", "XRPUSDT", "MATICUSDT"]

print("\\n📊 DATI DI MERCATO REALI:")
for symbol in symbols:
    print(f"\\n🔍 {symbol}:")
    try:
        market_data = trader.get_market_data(symbol)
        if market_data:
            print(f"   ✅ Dati ottenuti:")
            print(f"      Price: {market_data.get('price', 'N/A')}")
            print(f"      RSI: {market_data.get('rsi', 'N/A')}")
            print(f"      Regime: {market_data.get('regime', 'N/A')}")
            print(f"      Volume: {market_data.get('volume', 'N/A')}")
            
            # Testa se genera segnale di acquisto
            can_buy, reason = trader.check_buy_signal(market_data, fear_greed=11)
            print(f"      Segnale acquisto: {can_buy} - {reason}")
        else:
            print(f"   ❌ Nessun dato di mercato")
    except Exception as e:
        print(f"   ❌ Errore: {e}")

print("\\n🎯 VERIFICA INTEGRAZIONE V3:")
# Il wrapper v31 dovrebbe usare il sistema V3 internamente
print(f"   Tipo trader interno: {type(trader)}")
print(f"   Ha quantum_trader: {hasattr(trader, 'quantum_trader')}")

# Verifica se il wrapper sta usando V3 o è autonomo
if hasattr(trader, 'gating_system'):
    print(f"   ✅ Usa gating_system V3")
else:
    print(f"   ❌ NON usa gating_system V3")

#!/usr/bin/env python3
"""
🔍 Analizza la struttura del wrapper v31
"""

from quantum_v31_wrapper import QuantumTraderV31
import inspect

trader = QuantumTraderV31(dry_run=True)

print("📁 STRUTTURA QuantumTraderV31:")
print("=" * 50)

# Lista tutti i metodi
methods = [method for method in dir(trader) if not method.startswith('_')]
print("\\n🔧 METODI DISPONIBILI:")
for method in sorted(methods):
    print(f"   - {method}")

# Verifica se esiste un metodo principale
print(f"\\n📊 ATTRIBUTI PRINCIPALI:")
print(f"   quantum_trader: {hasattr(trader, 'quantum_trader')}")
if hasattr(trader, 'quantum_trader'):
    print(f"   Tipo: {type(trader.quantum_trader)}")

# Cerca il metodo che esegue il trading
print(f"\\n🎯 CERCO METODO DI TRADING:")
for method in methods:
    if 'run' in method.lower() or 'trad' in method.lower() or 'cycle' in method.lower():
        print(f"   TROVATO: {method}")
        
# Verifica il metodo __call__ o simile
print(f"\\n🔍 METODI SPECIALI:")
special_methods = [method for method in dir(trader) if method.startswith('__') and 'call' in method]
for method in special_methods:
    print(f"   - {method}")

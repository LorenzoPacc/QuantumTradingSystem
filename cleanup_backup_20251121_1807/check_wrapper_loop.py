#!/usr/bin/env python3
"""
🔍 Verifica struttura del wrapper
"""

import inspect

print("🔍 ANALISI QUANTUM_V31_WRAPPER")
print("=" * 50)

try:
    from quantum_v31_wrapper import QuantumTraderV31
    
    # Lista tutti i metodi
    methods = [m for m in dir(QuantumTraderV31) if not m.startswith('_')]
    
    print(f"📋 METODI TROVATI ({len(methods)}):")
    for method in sorted(methods):
        print(f"   • {method}")
    
    # Verifica metodi critici
    print("\n🎯 METODI CRITICI:")
    critical = ['run', 'main_loop', 'run_cycle', 'start']
    for method in critical:
        has_it = hasattr(QuantumTraderV31, method)
        status = "✅" if has_it else "❌"
        print(f"   {status} {method}()")
    
    # Verifica se ha __main__
    print("\n🔍 ENTRY POINT:")
    import quantum_v31_wrapper as wrapper_module
    
    # Cerca il blocco if __name__ == '__main__'
    import os
    with open('quantum_v31_wrapper.py', 'r') as f:
        content = f.read()
        
    has_main = '__main__' in content
    has_run_call = '.run()' in content or 'trader.start()' in content
    
    print(f"   {'✅' if has_main else '❌'} Blocco if __name__ == '__main__'")
    print(f"   {'✅' if has_run_call else '❌'} Chiamata .run() o .start()")
    
    if not has_run_call:
        print("\n❌ PROBLEMA TROVATO: Il wrapper non chiama il loop!")
        print("   Il bot si inizializza ma non parte mai.")
    
except Exception as e:
    print(f"❌ Errore: {e}")
    import traceback
    traceback.print_exc()

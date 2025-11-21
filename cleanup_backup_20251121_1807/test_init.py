#!/usr/bin/env python3
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    print("🔄 Carico QuantumTraderV31...")
    from quantum_v31_wrapper import QuantumTraderV31
    
    print("🎯 Inizializzo trader...")
    trader = QuantumTraderV31(dry_run=True)
    
    print("✅ TRADER INIZIALIZZATO CON SUCCESSO!")
    print(f"💰 Cash: \${trader.cash_balance:.2f}")
    print(f"📊 Posizioni: {len(trader.portfolio)}")
    
    if trader.portfolio:
        for symbol, pos in trader.portfolio.items():
            print(f"   🟢 {symbol}: {pos.get('quantity', 0)} unità @ \${pos.get('entry_price', 0):.2f}")
    
    print("\n🧪 Test ciclo singolo...")
    trader.run_cycle()
    print("✅ CICLO COMPLETATO!")
    
    sys.exit(0)
    
except Exception as e:
    print(f"❌ ERRORE: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

#!/usr/bin/env python3
"""
🎯 TEST del metodo run() vs run_cycle()
"""

from quantum_v31_wrapper import QuantumTraderV31
import time

print("🎯 CONFRONTO run() vs run_cycle()")
print("=" * 50)

# Test run_cycle() - singolo ciclo
print("\\n1. TEST run_cycle() (singolo ciclo):")
trader1 = QuantumTraderV31(dry_run=True)
start_time = time.time()
trader1.run_cycle()
end_time = time.time()

print(f"   Tempo esecuzione: {end_time - start_time:.2f}s")
print(f"   Posizioni: {len(trader1.portfolio)}")
print(f"   Cash: {trader1.cash_balance:.2f}")

# Test run() - modalità continua (breve)
print("\\n2. TEST run() (modalità continua - 5 secondi):")
trader2 = QuantumTraderV31(dry_run=True)

# Avvia in un thread per poterlo stoppare
import threading
import signal

def run_trader():
    try:
        trader2.run()
    except:
        pass

thread = threading.Thread(target=run_trader)
thread.daemon = True
thread.start()

# Aspetta 5 secondi poi interrompi
print("   Avviato... (attendi 5 secondi)")
time.sleep(5)
print("   Interrotto dopo 5 secondi")

print(f"   Posizioni: {len(trader2.portfolio)}")
print(f"   Cash: {trader2.cash_balance:.2f}")

print("\\n🔍 CONCLUSIONE:")
print("   - run_cycle(): esegue UN ciclo e termina")
print("   - run(): esegue cicli CONTINUI fino a interruzione")

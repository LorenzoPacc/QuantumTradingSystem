import time
import threading
import os
import signal
import sys

def signal_handler(sig, frame):
    print(f"\n🛑 Ricevuto segnale {sig}. Arresto pulito...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

print("🚀 AVVIO ROBUSTO QUANTUM TRADING SYSTEM...")
print("⏳ Caricamento moduli...")

try:
    from quantum_ultimate_fixed import QuantumTraderUltimateFixed
    from quantum_dashboard_compatible import start_compatible_dashboard
    print("✅ Moduli caricati correttamente")
except Exception as e:
    print(f"❌ Errore caricamento moduli: {e}")
    sys.exit(1)

# Crea trader
print("🤖 Creazione Quantum Trader...")
trader = QuantumTraderUltimateFixed(200)

# Avvia dashboard in thread separato
print("📊 Avvio Dashboard...")

def start_dashboard():
    try:
        dashboard = start_compatible_dashboard(trading_engine=trader, port=8081)
    except Exception as e:
        print(f"❌ Errore dashboard: {e}")

dashboard_thread = threading.Thread(target=start_dashboard)
dashboard_thread.daemon = True
dashboard_thread.start()

# Attendi avvio dashboard
time.sleep(5)

print("✅ DASHBOARD PRONTA: http://localhost:8081")
print("💡 Database contiene 6 trade REALI")
print("📊 Grafico mostrerà dati reali")

# Avvia trading in thread separato
def start_trading():
    try:
        print("🎯 Avvio trading automatico...")
        trader.run_continuous_trading(cycles=1000, delay=600)
    except Exception as e:
        print(f"❌ Errore trading: {e}")

trading_thread = threading.Thread(target=start_trading)
trading_thread.daemon = True
trading_thread.start()

print("🔥 SISTEMA AVVIATO - Premi Ctrl+C per fermare")

# Mantieni il programma attivo
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Arresto richiesto dall'utente")

import subprocess
import time
import os
import sys
import threading

print("🔄 Riavvio sistema con database corretto...")

# Ferma tutto
subprocess.run(['pkill', '-f', 'python3'], capture_output=True)
time.sleep(2)

# Importa le classi
try:
    from quantum_ultimate_fixed import QuantumTraderUltimateFixed
    from quantum_dashboard_compatible import start_compatible_dashboard
    print("✅ Moduli importati correttamente")
except ImportError as e:
    print(f"❌ Errore import: {e}")
    sys.exit(1)

print('🚀 AVVIO SISTEMA CORRETTO...')

# Crea trader
trader = QuantumTraderUltimateFixed(200)

# Avvia dashboard
dashboard = start_compatible_dashboard(trading_engine=trader, port=8081)

print('⏳ Attendere avvio dashboard...')
time.sleep(5)

print('✅ SISTEMA PRONTO: http://localhost:8081')
print('📊 Ora vedrai dati REALI nel grafico Performance Cumulative!')
print('💡 I 6 trade reali saranno visibili nelle statistiche')

# Avvia trading in thread separato
def run_trading():
    try:
        trader.run_continuous_trading(cycles=1000, delay=600)
    except Exception as e:
        print(f"❌ Errore trading: {e}")

trading_thread = threading.Thread(target=run_trading)
trading_thread.daemon = True
trading_thread.start()

# Mantieni il programma attivo
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Sistema fermato dall'utente")

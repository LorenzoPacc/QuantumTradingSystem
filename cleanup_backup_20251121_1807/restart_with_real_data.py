import sqlite3
import time
import subprocess
from datetime import datetime

# Ferma il sistema corrente
subprocess.run(['pkill', '-f', 'python3'], capture_output=True)
time.sleep(2)

# Pulisci il database per iniziare con dati freschi
conn = sqlite3.connect('trading_performance.db')
cursor = conn.cursor()
cursor.execute('DELETE FROM trade_performance')
conn.commit()
conn.close()
print("🗑️ Database pulito per dati reali")

# Importa le classi aggiornate
from quantum_ultimate_fixed import QuantumTraderUltimateFixed, TradeLogger
from quantum_dashboard_compatible import start_compatible_dashboard

print('🚀 AVVIO SISTEMA CON REGISTRAZIONE TRADE REALI...')

# Crea trader con logging
trader = QuantumTraderUltimateFixed(200)

# Avvia dashboard
dashboard = start_compatible_dashboard(trading_engine=trader, port=8081)

print('⏳ Attendere primo ciclo di trading...')
time.sleep(10)

print('✅ SISTEMA PRONTO: http://localhost:8081')
print('📊 I trade REALI verranno ora registrati automaticamente!')

# Avvia trading
trader.run_continuous_trading(cycles=1000, delay=600)

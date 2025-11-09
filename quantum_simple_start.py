import time
import threading
from quantum_ai_trader_ultimate import QuantumAITraderUltimate

# Versione semplificata che funziona sempre
def simple_dashboard_integration():
    print("🚀 AVVIO SEMPLIFICATO QUANTUM TRADER...")
    
    # Crea trader
    trader = QuantumAITraderUltimate(200)
    
    # Importa e avvia dashboard DOPO aver creato il trader
    from quantum_dashboard_perfected import start_quantum_dashboard_perfected
    
    print("📊 Avvio dashboard...")
    dashboard = start_quantum_dashboard_perfected(trading_engine=trader, port=8080)
    
    # Aspetta che la dashboard sia pronta
    time.sleep(3)
    
    print("✅ Sistema pronto!")
    print("🌐 Dashboard: http://localhost:8080")
    print("🤖 Trader: attivo")
    
    # Avvia trading
    try:
        trader.run_ultimate_trading(cycles=1000, delay=600)
    except KeyboardInterrupt:
        print("🛑 Sistema fermato dall'utente")

if __name__ == "__main__":
    simple_dashboard_integration()

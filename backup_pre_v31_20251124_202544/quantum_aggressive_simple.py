import time
import logging
from quantum_ai_trader_ultimate import QuantumAITraderUltimate
from quantum_dashboard_perfected import start_quantum_dashboard_perfected

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def make_trader_aggressive():
    print("🚀 QUANTUM TRADER AGGRESSIVO - EXTREME FEAR MODE")
    print("🎯 Fear & Greed = 20 → STRATEGIA CONTRARIAN ATTIVATA")
    
    trader = QuantumAITraderUltimate(200)
    
    # 🎯 PARAMETRI SUPER AGGRESSIVI PER EXTREME FEAR
    params = trader.learning_engine.optimal_params
    params['confluence_threshold'] = 0.55    # Soglia abbassata (era 0.65)
    params['position_size_base'] = 0.15      # Size aumentata (era 0.10)
    params['fear_boost'] = 1.8               # Boost massivo (era 1.4)
    params['max_position_size'] = 45         # Posizioni più grandi (era 30)
    
    print("✅ PARAMETRI AGGRESSIVI APPLICATI:")
    print(f"   📉 Soglia acquisto: {params['confluence_threshold']} (era 0.65)")
    print(f"   💰 Size posizione: {params['position_size_base']:.0%} (era 10%)")
    print(f"   😨 Fear boost: {params['fear_boost']}x (era 1.4x)")
    print(f"   📊 Max position: ${params['max_position_size']} (era $30)")
    
    return trader

if __name__ == "__main__":
    try:
        # Crea e configura trader aggressivo
        trader = make_trader_aggressive()
        
        # Avvia dashboard
        print("📊 Avvio dashboard...")
        dashboard = start_quantum_dashboard_perfected(trading_engine=trader, port=8081)
        
        # Aspetta inizializzazione
        time.sleep(3)
        
        print("✅ SISTEMA AGGRESSIVO PRONTO!")
        print("🌐 DASHBOARD: http://localhost:8081")
        print("🤖 TRADER: Modalità Extreme Fear Attivata")
        print("💸 ASPETTATI ACQUISTI IMMEDIATI NEL PROSSIMO CICLO!")
        print("⏰ Cicli ogni 10 minuti - Premi Ctrl+C per fermare")
        
        # Avvia trading
        trader.run_ultimate_trading(cycles=1000, delay=600)
        
    except KeyboardInterrupt:
        print("\n🛑 Sistema fermato dall'utente")
    except Exception as e:
        print(f"❌ Errore: {e}")
        logging.exception("Errore dettagliato:")

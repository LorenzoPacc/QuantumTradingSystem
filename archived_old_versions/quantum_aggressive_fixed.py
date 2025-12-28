import time
import logging
from decimal import Decimal
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

# 🔧 PATCH PER IL BUG DECIMAL
def apply_decimal_fix():
    """Applica fix per errore Decimal vs float"""
    import quantum_ai_trader_ultimate as qatu
    
    # Override del metodo problematico
    original_calculate_position_size = None
    
    def safe_calculate_position_size(self, symbol, score, fgi, params):
        try:
            available_cash = float(self.portfolio_manager.cash_balance)
            
            if available_cash < 10:
                return 0.0
            
            base_size = available_cash * params['position_size_base']
            score_multiplier = 0.5 + score
            
            if fgi < 25:
                fear_multiplier = params['fear_boost']
            elif fgi < 40:
                fear_multiplier = 1.2
            elif fgi > 70:
                fear_multiplier = params['greed_reduction']
            else:
                fear_multiplier = 1.0
            
            final_size = base_size * score_multiplier * fear_multiplier
            final_size = min(params['max_position_size'], final_size)
            final_size = max(10.0, final_size)
            
            current_exposure = self.portfolio_manager.get_current_exposure()
            if current_exposure >= params['max_portfolio_exposure']:
                return 0.0
            
            return float(final_size)  # 🔧 CONVERTI SEMPRE A FLOAT
            
        except Exception as e:
            logging.error(f"Errore calcolo position size: {e}")
            return 0.0
    
    # Applica la patch
    qatu.QuantumAITraderUltimate._calculate_optimized_position_size = safe_calculate_position_size
    print("🔧 Patch Decimal applicata con successo")

if __name__ == "__main__":
    try:
        # Applica fix prima di tutto
        apply_decimal_fix()
        
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

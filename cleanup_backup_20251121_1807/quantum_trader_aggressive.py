from quantum_ai_trader_ultimate import QuantumAITraderUltimate
from quantum_dashboard_perfected import start_quantum_dashboard_perfected
import time

class QuantumTraderAggressive(QuantumAITraderUltimate):
    """VERSIONE PIÙ AGGRESSIVA - COMPRA IN EXTREME FEAR!"""
    
    def _calculate_confluence_score(self, symbol: str) -> Dict:
        """SCORE PIÙ AGGRESSIVO IN EXTREME FEAR"""
        try:
            price_data = self.market_data.get_ohlcv_data(symbol, '4h', 20)
            if price_data is None:
                return {'final_score': 0.5}
            
            closes = price_data['close'].values
            volumes = price_data['volume'].values
            
            if len(closes) < 10:
                return {'final_score': 0.5}
            
            momentum = ((closes[-1] - closes[-5]) / closes[-5]) * 100
            volume_ratio = volumes[-1] / np.mean(volumes[-5:])
            
            # 🎯 BASE SCORE PIÙ ALTO IN EXTREME FEAR
            base_score = 0.6  # Era 0.5
            
            if momentum > 1:  # Era 2
                base_score += 0.25  # Era 0.2
            elif momentum < -1:  # Era -2  
                base_score -= 0.15  # Era 0.2
            
            if volume_ratio > 1.1:  # Era 1.2
                base_score += 0.15  # Era 0.1
            
            fgi = self.market_data.get_fear_greed_index()
            
            # 🎯 BOOST MASSIVO IN EXTREME FEAR
            if fgi < 25:    # Extreme Fear
                base_score *= 1.6   # Era 1.2 - MOLTO più aggressivo!
            elif fgi < 40:  # Fear
                base_score *= 1.3   # Era 1.2
            elif fgi > 70:  # Greed
                base_score *= 0.7   # Era 0.8
            else:           # Neutral
                base_score *= 1.0
            
            return {
                'final_score': max(0.1, min(0.95, base_score)),
                'fear_greed_index': fgi
            }
            
        except Exception as e:
            logging.error(f"Errore calcolo score {symbol}: {e}")
            return {'final_score': 0.6}  # Fallback più alto

def start_aggressive_trader():
    print("🚀 AVVIO QUANTUM TRADER AGGRESSIVO...")
    print("🎯 STRATEGIA: Extreme Fear Contrarian Boosted!")
    
    # Crea trader aggressivo
    trader = QuantumTraderAggressive(200)
    
    # Avvia dashboard sulla porta CORRETTA (8081)
    from quantum_dashboard_perfected import start_quantum_dashboard_perfected
    dashboard = start_quantum_dashboard_perfected(trading_engine=trader, port=8081)
    
    time.sleep(3)
    
    print("✅ Sistema aggressivo pronto!")
    print("🌐 Dashboard: http://localhost:8081")
    print("🤖 Trader: Modalità Extreme Fear Attivata")
    print("💡 Con F&G=20, il trader sarà MOLTO più aggressivo!")
    
    # Avvia trading
    try:
        trader.run_ultimate_trading(cycles=1000, delay=600)
    except KeyboardInterrupt:
        print("🛑 Sistema fermato")

if __name__ == "__main__":
    start_aggressive_trader()

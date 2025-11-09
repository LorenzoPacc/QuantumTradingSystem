from quantum_ultimate_fixed import QuantumTraderUltimateFixed
import random  # Aggiungi questo import

# Aggiungi metodi mancanti alla classe MockMarketData
def add_market_methods():
    original_class = QuantumTraderUltimateFixed
    
    # Estendi MockMarketData
    class FixedMarketData:
        def get_real_price(self, symbol):
            prices = {
                'BTCUSDT': 100000 + random.randint(-5000, 5000),
                'ETHUSDT': 3300 + random.randint(-200, 200),
                'SOLUSDT': 150 + random.randint(-10, 10),
                'AVAXUSDT': 16 + random.uniform(-2, 2),
                'LINKUSDT': 15 + random.uniform(-1, 1),
                'DOTUSDT': 3.1 + random.uniform(-0.2, 0.2)
            }
            return prices.get(symbol, 100)
        
        def get_fear_greed_index(self):
            return 22  # Extreme Fear
            
        def get_btc_dominance(self):
            return 57.5 + random.uniform(-1, 1)
    
    # Sostituisci market_data
    trader = QuantumTraderUltimateFixed(200)
    trader.market_data = FixedMarketData()
    
    print("✅ MARKET DATA FIXED!")
    print(f"🎯 Fear & Greed: {trader.market_data.get_fear_greed_index()}")
    print(f"📊 BTC Dominance: {trader.market_data.get_btc_dominance():.1f}%")

if __name__ == "__main__":
    add_market_methods()

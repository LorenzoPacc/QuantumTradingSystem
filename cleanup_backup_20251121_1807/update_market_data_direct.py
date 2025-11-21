import random

# Leggi il file
with open('quantum_ultimate_fixed.py', 'r') as f:
    content = f.read()

# Cerca la classe MockMarketData e sostituiscila completamente
old_code = '''class MockMarketData:
    def get_real_price(self, symbol):
        prices = {
            'BTCUSDT': 101600 + random.randint(-1000, 1000),
            'ETHUSDT': 3380 + random.randint(-50, 50),
            'SOLUSDT': 157 + random.randint(-5, 5),
            'AVAXUSDT': 17.2 + random.uniform(-1, 1),
            'LINKUSDT': 15.3 + random.uniform(-0.5, 0.5),
            'DOTUSDT': 3.17 + random.uniform(-0.1, 0.1)
        }
        return prices.get(symbol, 100)'''

new_code = '''class MockMarketData:
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
        return 57.5 + random.uniform(-1, 1)'''

# Sostituisci
if old_code in content:
    content = content.replace(old_code, new_code)
    print("✅ MARKET DATA AGGIORNATO NEL TRADER!")
else:
    print("❌ Non ho trovato il codice da sostituire")
    print("🔍 Cerco MockMarketData...")
    if 'class MockMarketData' in content:
        print("✅ MockMarketData trovato, ma struttura diversa")

# Scrivi il file aggiornato
with open('quantum_ultimate_fixed.py', 'w') as f:
    f.write(content)

print("📝 File aggiornato")

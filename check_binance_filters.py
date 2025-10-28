import requests
import json

symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

print("🎯 FILTRI MINIMI BINANCE TESTNET")
print("================================")

for symbol in symbols:
    url = f"https://testnet.binance.vision/api/v3/exchangeInfo?symbol={symbol}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        symbol_info = data['symbols'][0]
        
        print(f"\n📊 {symbol}:")
        
        # Trova filtro NOTIONAL (minimo ordine)
        for filtro in symbol_info['filters']:
            if filtro['filterType'] == 'NOTIONAL':
                min_notional = float(filtro['minNotional'])
                print(f"   💰 Minimo ordine: ${min_notional:.2f}")
            
            if filtro['filterType'] == 'LOT_SIZE':
                min_qty = float(filtro['minQty'])
                print(f"   📦 Quantità minima: {min_qty}")
                
        # Prezzo attuale
        price_url = f"https://testnet.binance.vision/api/v3/ticker/price?symbol={symbol}"
        price_data = requests.get(price_url).json()
        current_price = float(price_data['price'])
        print(f"   💵 Prezzo attuale: ${current_price:.2f}")
        
        # Calcola quantità minima
        min_qty_value = min_notional / current_price
        print(f"   🎯 Quantità minima per ${min_notional}: {min_qty_value:.6f}")

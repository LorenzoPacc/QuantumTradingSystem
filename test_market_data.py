#!/usr/bin/env python3
import requests
import pandas as pd

print("📊 TEST DATI MERCATO (senza API keys)")
print("="*50)

symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

for symbol in symbols:
    try:
        url = f"https://api.binance.com/api/v3/ticker/price"
        response = requests.get(url, params={"symbol": symbol}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {symbol}: ${float(data['price']):,.2f}")
        else:
            print(f"❌ {symbol}: Errore {response.status_code}")
            
    except Exception as e:
        print(f"❌ {symbol}: {e}")

print("="*50)
print("Se vedi i prezzi, la connessione a Binance funziona!")

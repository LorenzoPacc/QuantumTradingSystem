#!/bin/bash
echo "💰 CALCOLO VALORE REALE PORTFOLIO TESTNET"
echo "=========================================="

python3 << 'END'
import requests
import hmac
import hashlib
import time

api_key = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
api_secret = "yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"

# Ottieni balance completo
timestamp = int(time.time() * 1000)
query_string = f"timestamp={timestamp}"
signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

url = f"https://testnet.binance.vision/api/v3/account?{query_string}&signature={signature}"
headers = {"X-MBX-APIKEY": api_key}

response = requests.get(url, headers=headers)
data = response.json()

# Prezzi reali da API
def get_price(symbol):
    try:
        price_url = f"https://testnet.binance.vision/api/v3/ticker/price?symbol={symbol}"
        price_data = requests.get(price_url).json()
        return float(price_data['price'])
    except:
        return 0

# Assets principali con prezzi reali
main_assets = {
    'BTC': get_price('BTCUSDT'),
    'ETH': get_price('ETHUSDT'), 
    'SOL': get_price('SOLUSDT'),
    'BNB': get_price('BNBUSDT'),
    'USDT': 1, 'USDC': 1, 'TUSD': 1, 'DAI': 1, 'FDUSD': 1, 'BUSD': 1
}

total_value = 0
print("🎯 ASSETS PRINCIPALI CON VALORE:\n")

for balance in data['balances']:
    asset = balance['asset']
    free = float(balance['free'])
    locked = float(balance['locked'])
    total = free + locked
    
    if total > 0 and asset in main_assets:
        price = main_assets[asset]
        value = total * price
        total_value += value
        
        if value > 10:  # Mostra solo assets con valore > $10
            print(f"  💎 {asset}:")
            print(f"     Quantità: {total}")
            print(f"     Prezzo: ${price:,.2f}")
            print(f"     Valore: ${value:,.2f}")
            if locked > 0:
                print(f"     🔒 Bloccati: {locked}")

# Stablecoins totali
stablecoins = ['USDT', 'USDC', 'TUSD', 'DAI', 'FDUSD', 'BUSD']
stable_total = sum(float(b['free']) + float(b['locked']) for b in data['balances'] if b['asset'] in stablecoins)

print(f"\n💵 STABLECOINS TOTALI: ${stable_total:,.2f}")
print(f"🚀 VALORE TOTALE PORTFOLIO: ${total_value:,.2f}")

# Confronto con $10k iniziali
if stable_total < 10000:
    missing = 10000 - stable_total
    print(f"\n🔍 ANALISI:")
    print(f"   Stablecoins attuali: ${stable_total:,.2f}")
    print(f"   Stablecoins iniziali: $10,000.00") 
    print(f"   DIFFERENZA: -${missing:,.2f}")
    print(f"   💡 Probabilmente convertiti in ETH/SOL positions")
END

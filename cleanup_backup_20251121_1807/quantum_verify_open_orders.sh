#!/bin/bash
echo "🔍 VERIFICA ORDINI APERTI SU BINANCE TESTNET"
echo "=============================================="

python3 << 'END'
import requests
import hmac
import hashlib
import time

api_key = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
api_secret = "yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"

timestamp = int(time.time() * 1000)
query_string = f"timestamp={timestamp}"
signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

url = f"https://testnet.binance.vision/api/v3/openOrders?{query_string}&signature={signature}"
headers = {"X-MBX-APIKEY": api_key}

response = requests.get(url, headers=headers)
orders = response.json()

print(f"📋 ORDINI APERTI TROVATI: {len(orders)}")

if len(orders) > 0:
    total_locked = 0
    for order in orders:
        symbol = order['symbol']
        side = order['side']
        qty = float(order['origQty'])
        price = float(order['price'])
        filled = float(order['executedQty'])
        locked_value = (qty - filled) * price
        
        print(f"  🚨 {symbol} {side} {qty} @ ${price}")
        print(f"     Filled: {filled} | Locked: ${locked_value:.2f}")
        print(f"     Status: {order['status']} | OrderID: {order['orderId']}")
        total_locked += locked_value
    
    print(f"\n💰 TOTALE BLOCCATO IN ORDINI: ${total_locked:.2f}")
else:
    print("✅ Nessun ordine aperto trovato")
END

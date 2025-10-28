#!/usr/bin/env python3
"""
OTTIENI FONDI TESTNET BINANCE
"""

print("🎯 COME OTTENERE NUOVI FONDI TESTNET:")
print("=====================================")
print("1. Vai su: https://testnet.binance.vision/")
print("2. Fai login con il tuo account")
print("3. Clicca su 'Faucet' (rubinetto)")
print("4. Seleziona 'USDT' e richiedi fondi")
print("5. Ripeti per BTC, ETH, BNB se vuoi")
print("")
print("💡 CONSIGLIO: Richiedi almeno 1000 USDT")
print("⏱️  I fondi arrivano in 1-2 minuti")
print("")
print("🔑 Le tue API Key rimangono le stesse:")
print(f"   API Key: h9LX8Z2xTLVOcfDjcX410QZG3U5DxzOGBLxcbX5GYrvz9lfCs7RDjb8N2jzDWXW")
print(f"   Secret: V98bXD1RQTJTwRqEke1kkqBAFaPhQJ80RQ8R1jI8uUgnkLqX91YoNhPneuPTYsv7")
print("")
input("Premi INVIO dopo aver richiesto i fondi...")

# Verifica nuovi fondi
import requests
import hmac
import hashlib
import time

api_key = "h9LX8Z2xTLVOcfDjcX410QZG3sU5DxzOGBLxcbX5GYrvz9lfCs7RDjb8N2jzDWXW"
api_secret = "V98bXD1RQTJTwRqEke1kkqBAFaPhQJ80RQ8R1jI8uUgnkLqX91YoNhPneuPTYsv7"

timestamp = int(time.time() * 1000)
query_string = f"timestamp={timestamp}"
signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

url = f"https://testnet.binance.vision/api/v3/account?{query_string}&signature={signature}"
headers = {"X-MBX-APIKEY": api_key}

try:
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        usdt = next((b for b in data['balances'] if b['asset'] == 'USDT'), None)
        if usdt and float(usdt['free']) > 100:
            print(f"✅ SUCCESSO! Hai ora {usdt['free']} USDT")
        else:
            print("❌ Fondi ancora insufficienti. Riprova il faucet.")
except Exception as e:
    print(f"❌ Errore: {e}")

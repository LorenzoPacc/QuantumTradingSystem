#!/usr/bin/env python3
import os
import time
import requests
import hmac
import hashlib
from datetime import datetime

# Carica environment
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("BINANCE_TESTNET_API_KEY")
api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")

print("🔍 Testing Binance Testnet API Keys...")
print(f"API Key: {api_key[:10]}...{api_key[-4:] if api_key else 'MISSING'}")
print(f"API Secret: {'***PRESENT***' if api_secret else 'MISSING'}")

if not api_key or not api_secret:
    print("❌ API keys mancanti nel file .env")
    exit(1)

# Test connection
try:
    # Test semplice senza signature
    url = "https://testnet.binance.com/api/v3/ping"
    response = requests.get(url)
    print(f"✅ Ping Testnet: {response.status_code}")
    
    # Test con signature
    timestamp = int(time.time() * 1000)
    params = {'timestamp': timestamp, 'recvWindow': 5000}
    
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(
        api_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    params['signature'] = signature
    
    url = "https://testnet.binance.com/api/v3/account"
    headers = {"X-MBX-APIKEY": api_key}
    response = requests.get(url, headers=headers, params=params, timeout=10)
    
    if response.status_code == 200:
        print("🎉 SUCCESSO! API Keys FUNZIONANO correttamente!")
        data = response.json()
        print(f"💰 Balance disponibile: {len(data.get('balances', []))} assets")
        
        # Mostra balance USDT
        for balance in data.get('balances', []):
            if balance['asset'] == 'USDT':
                free_balance = float(balance['free'])
                print(f"💵 USDT Balance: {free_balance:,.2f} USDT")
                break
                
    else:
        print(f"❌ Errore API: {response.status_code}")
        print(f"📝 Response: {response.text}")
        
except Exception as e:
    print(f"❌ Errore durante il test: {e}")
    import traceback
    traceback.print_exc()

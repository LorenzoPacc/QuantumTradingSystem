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

# Test 1: Ping semplice
try:
    url = "https://testnet.binance.com/api/v3/ping"
    response = requests.get(url, timeout=10)
    print(f"✅ Ping Testnet: {response.status_code}")
except Exception as e:
    print(f"❌ Ping failed: {e}")

# Test 2: Ticker price (public endpoint)
try:
    url = "https://testnet.binance.com/api/v3/ticker/price"
    params = {"symbol": "BTCUSDT"}
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Price data: {data['symbol']} = ${float(data['price']):,.2f}")
    else:
        print(f"❌ Price error: {response.status_code}")
except Exception as e:
    print(f"❌ Price test failed: {e}")

# Test 3: Account info con signature
try:
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
    
    print("🔐 Testing signed request...")
    response = requests.get(url, headers=headers, params=params, timeout=15)
    
    print(f"📊 Response status: {response.status_code}")
    print(f"📝 Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print("🎉 SUCCESSO! API Keys FUNZIONANO!")
        print(f"💰 Account canTrade: {data.get('canTrade', 'N/A')}")
        print(f"💰 Balances: {len(data.get('balances', []))} assets")
        
        for balance in data.get('balances', []):
            if balance['asset'] == 'USDT':
                free = float(balance['free'])
                locked = float(balance['locked'])
                print(f"💵 USDT: Free={free:.2f}, Locked={locked:.2f}")
                break
                
    elif response.status_code == 401:
        print("❌ Error 401: Unauthorized - API Key invalid")
    elif response.status_code == 400:
        print("❌ Error 400: Bad Request - Check signature/timestamp")
        print(f"Response text: {response.text}")
    else:
        print(f"❌ Unexpected status: {response.status_code}")
        print(f"Response text: {response.text}")
        
except Exception as e:
    print(f"❌ Signed request failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("📋 SUMMARY:")
print("• Se vedi 'SUCCESSO', le API keys funzionano!")
print("• Se vedi errori 401, le API keys sono sbagliate")
print("• Se vedi errori 400, problema di signature")
print("="*50)

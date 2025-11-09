#!/usr/bin/env python3
import requests
import hmac
import hashlib
import time
from config_auto_trading import API_KEY, API_SECRET, BASE_URL

print("🔐 TEST API KEYS TESTNET")
print("=" * 40)

# Test 1: Account info
try:
    endpoint = "/api/v3/account"
    timestamp = int(time.time() * 1000)
    
    params = {'timestamp': timestamp}
    query_string = f"timestamp={timestamp}"
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    params['signature'] = signature
    headers = {'X-MBX-APIKEY': API_KEY}
    
    response = requests.get(f"{BASE_URL}{endpoint}", params=params, headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API Keys: VALIDE")
        print(f"✅ Balance USDT: {[b for b in data['balances'] if b['asset']=='USDT'][0]['free']}")
        print("✅ Pronto per trading automatico!")
    else:
        print(f"❌ Errore: {response.status_code}")
        print(f"   {response.text}")
        exit(1)
        
except Exception as e:
    print(f"❌ Errore connessione: {e}")
    exit(1)

print("\n🎯 TUTTO OK - Puoi attivare il trading automatico!")

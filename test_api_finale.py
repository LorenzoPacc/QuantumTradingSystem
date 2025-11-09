#!/usr/bin/env python3
import os
import requests
import hmac
import hashlib
import time
from pathlib import Path

print("🧪 TEST FINALE API KEYS")
print("=======================")

# Carica dal file
env_file = Path('.env.testnet')
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

API_KEY = os.getenv('BINANCE_TESTNET_API_KEY', '').strip()
SECRET_KEY = os.getenv('BINANCE_TESTNET_SECRET_KEY', '').strip()

print(f"🔑 API Key: {API_KEY[:20]}..." if API_KEY else "❌ API Key: VUOTA")
print(f"🔒 Secret: {SECRET_KEY[:20]}..." if SECRET_KEY else "❌ Secret: VUOTO")
print("")

BASE_URL = "https://testnet.binance.vision"

try:
    # Test connessione
    print("1. 🔌 Test connessione...")
    response = requests.get(f"{BASE_URL}/api/v3/ping", timeout=10)
    if response.status_code == 200:
        print("   ✅ Connessione: OK")
    else:
        print(f"   ❌ Connessione: {response.status_code}")

    # Test API Keys
    if API_KEY and SECRET_KEY:
        print("2. 🔐 Test API Keys...")
        timestamp = int(time.time() * 1000)
        params = {'timestamp': timestamp}
        
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            SECRET_KEY.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        params['signature'] = signature
        headers = {'X-MBX-APIKEY': API_KEY}
        
        response = requests.get(
            f"{BASE_URL}/api/v3/account",
            params=params,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            account = response.json()
            print("   ✅ API Keys: VALIDE E FUNZIONANTI!")
            # Mostra USDT balance
            usdt_balance = next((b for b in account['balances'] if b['asset'] == 'USDT'), None)
            if usdt_balance:
                free = float(usdt_balance['free'])
                locked = float(usdt_balance['locked'])
                print(f"   💰 USDT Balance: {free} (free) + {locked} (locked) = {free + locked} total")
        else:
            print(f"   ❌ API Keys errore: {response.text}")
    else:
        print("2. ⚠️  API Keys non trovate nel file")
        
except Exception as e:
    print(f"❌ Errore: {e}")

print("")
if API_KEY and SECRET_KEY:
    print("🎯 ORA PUOI RIAVVIARE L'AUTO TRADER!")
    print("   ./quantum_commands.sh restart")
else:
    print("❌ Configura prima le API Keys nel file .env.testnet")

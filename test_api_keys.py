#!/usr/bin/env python3
import os
import requests
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

# Leggi le API keys dal .env
api_key = os.getenv("BINANCE_TESTNET_API_KEY")
api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")

print("🔍 TEST API KEYS BINANCE TESTNET")
print("="*50)
print(f"API Key: {api_key[:10]}...{api_key[-4:] if api_key else 'MISSING'}")
print(f"API Secret: {api_secret[:10]}...{api_secret[-4:] if api_secret else 'MISSING'}")
print("="*50)

if not api_key or not api_secret:
    print("❌ API Keys mancanti nel file .env")
    exit(1)

# Test semplice - get server time
try:
    response = requests.get("https://testnet.binance.vision/api/v3/time")
    if response.status_code == 200:
        print("✅ Connessione a Binance Testnet: OK")
    else:
        print(f"❌ Connessione fallita: {response.status_code}")
except Exception as e:
    print(f"❌ Errore connessione: {e}")

# Test autenticato - get account info
try:
    timestamp = int(requests.get("https://testnet.binance.vision/api/v3/time").json()["serverTime"])
    
    params = {
        "timestamp": timestamp,
        "recvWindow": 5000
    }
    
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(
        api_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    params['signature'] = signature
    
    headers = {"X-MBX-APIKEY": api_key}
    response = requests.get(
        "https://testnet.binance.vision/api/v3/account",
        params=params,
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ Autenticazione API: SUCCESSO")
        account_info = response.json()
        print(f"💰 Account Type: {account_info.get('accountType', 'N/A')}")
        print(f"💼 Permissions: {account_info.get('permissions', ['N/A'])}")
        
        # Mostra balances
        for balance in account_info.get('balances', []):
            if float(balance['free']) > 0 or float(balance['locked']) > 0:
                print(f"   {balance['asset']}: Free={balance['free']}, Locked={balance['locked']}")
                
    elif response.status_code == 401:
        print("❌ Autenticazione API: FALLITA - Invalid API Key")
        print("   Possibili cause:")
        print("   - API Key scaduta (testnet keys scadono dopo 3 mesi)")
        print("   - API Secret errato")
        print("   - IP non autorizzato")
        print("   - Permessi insufficienti")
    else:
        print(f"❌ Autenticazione API: Errore {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"❌ Errore durante il test: {e}")

print("="*50)

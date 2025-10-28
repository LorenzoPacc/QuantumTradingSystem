#!/usr/bin/env python3
import os
import requests
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("BINANCE_TESTNET_API_KEY")
api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")

print("🔍 ANALISI DETTAGLIATA API KEYS")
print("="*60)

if not api_key:
    print("❌ API KEY: NON TROVATA nel file .env")
else:
    print(f"🔑 API KEY: {api_key}")
    print(f"   Lunghezza: {len(api_key)} caratteri")
    print(f"   Formato: {'✅ Valido' if len(api_key) > 20 else '❌ Troppo corta'}")

if not api_secret:
    print("❌ API SECRET: NON TROVATO nel file .env")
else:
    print(f"🔒 API SECRET: {api_secret[:8]}...{api_secret[-4:]}")
    print(f"   Lunghezza: {len(api_secret)} caratteri")
    print(f"   Formato: {'✅ Valido' if len(api_secret) > 20 else '❌ Troppo corto'}")

print("")
print("📡 TEST CONNESSIONE A BINANCE...")

# Test 1: Server time (non richiede auth)
try:
    response = requests.get("https://testnet.binance.vision/api/v3/time", timeout=10)
    if response.status_code == 200:
        server_time = response.json()["serverTime"]
        from datetime import datetime
        dt = datetime.fromtimestamp(server_time/1000)
        print(f"✅ Server Time: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"❌ Server Time: Errore {response.status_code}")
except Exception as e:
    print(f"❌ Server Time: {e}")

# Test 2: Exchange info (non richiede auth)
try:
    response = requests.get("https://testnet.binance.vision/api/v3/exchangeInfo", timeout=10)
    if response.status_code == 200:
        print("✅ Exchange Info: Connessione OK")
    else:
        print(f"❌ Exchange Info: Errore {response.status_code}")
except Exception as e:
    print(f"❌ Exchange Info: {e}")

print("")
print("🔐 TEST AUTENTICAZIONE...")

if api_key and api_secret:
    try:
        # Prendi server time
        timestamp = int(requests.get("https://testnet.binance.vision/api/v3/time").json()["serverTime"])
        
        # Prepara richiesta autenticata
        params = {"timestamp": timestamp, "recvWindow": 60000}
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        params['signature'] = signature
        
        headers = {"X-MBX-APIKEY": api_key}
        response = requests.get("https://testnet.binance.vision/api/v3/account", params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("🎉 SUCCESSO! API Keys VALIDE")
            account = response.json()
            print(f"   Account Type: {account.get('accountType', 'N/A')}")
            print(f"   Can Trade: {account.get('canTrade', False)}")
            
            # Mostra balances con fondi
            print("   Balances con fondi:")
            for balance in account.get('balances', []):
                free = float(balance['free'])
                locked = float(balance['locked'])
                if free > 0 or locked > 0:
                    print(f"     {balance['asset']}: Free={free}, Locked={locked}")
                    
        elif response.status_code == 401:
            print("❌ FALLITO: Invalid API Key")
            print("   Le tue API keys sono scadute o non valide")
            print("   Devi rigenerarle su: https://testnet.binance.vision/")
        elif response.status_code == 400:
            print("❌ FALLITO: Bad Request - possibili problemi:")
            print("   - API Secret errato")
            print("   - Timestamp non sincronizzato")
        else:
            print(f"❌ FALLITO: Errore {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Errore durante l'autenticazione: {e}")

print("="*60)
print("💡 CONCLUSIONE:")
if api_key and api_secret:
    print("Le tue API Keys esistono ma sono INVALIDE/SCADUTE")
    print("🔧 Soluzione: Rigenerale su Binance Testnet")
else:
    print("API Keys mancanti nel file .env")

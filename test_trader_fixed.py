import os
import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode

print("🧪 Test Quantum Trader con variabili d'ambiente...")

# Carica le chiavi dalle variabili d'ambiente
api_key = os.getenv('BINANCE_TESTNET_API_KEY')
api_secret = os.getenv('BINANCE_TESTNET_SECRET_KEY')

print(f"🔐 API Key presente: {'✅' if api_key else '❌'}")
print(f"🔐 API Secret presente: {'✅' if api_secret else '❌'}")

if not api_key or not api_secret:
    print("\\n❌ ERRORE: Variabili d'ambiente non impostate!")
    print("💡 Esegui questi comandi nel terminale:")
    print("   export BINANCE_TESTNET_API_KEY='EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1'")
    print("   export BINANCE_TESTNET_SECRET_KEY='yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI'")
    exit(1)

print(f"🔐 API Key: {api_key[:10]}...{api_key[-10:]}")
print(f"🔐 API Secret: {api_secret[:10]}...{api_secret[-10:]}")

# Test connessione API TestNet
BASE_URL = "https://testnet.binance.vision"

print("\\n🔌 Test connessione API TestNet...")

# Test 1: Server time
try:
    response = requests.get(f'{BASE_URL}/api/v3/time', timeout=10)
    server_time = response.json()
    print(f"✅ Server time: {server_time}")
except Exception as e:
    print(f"❌ Server time error: {e}")

# Test 2: Account info (con autenticazione)
timestamp = int(time.time() * 1000)
params = {
    'timestamp': timestamp,
    'recvWindow': 60000
}

query_string = urlencode(params)
signature = hmac.new(
    api_secret.encode('utf-8'),
    query_string.encode('utf-8'),
    hashlib.sha256
).hexdigest()

params['signature'] = signature
headers = {'X-MBX-APIKEY': api_key}

try:
    response = requests.get(
        f'{BASE_URL}/api/v3/account',
        headers=headers,
        params=params,
        timeout=10
    )
    
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        account_info = response.json()
        print("🎉 SUCCESSO! API TestNet funzionante con nuove chiavi")
        print(f"💰 Balances: {len(account_info['balances'])} assets")
        
        # Mostra balances principali
        main_assets = ['BTC', 'ETH', 'USDT', 'BNB', 'XRP', 'ADA', 'SOL']
        print("\\n💰 Balances principali:")
        for asset in main_assets:
            balance = next((b for b in account_info['balances'] if b['asset'] == asset), None)
            if balance and (float(balance['free']) > 0 or float(balance['locked']) > 0):
                print(f"   {asset}: Free={balance['free']}, Locked={balance['locked']}")
                
    else:
        print(f"❌ Errore API: {response.text}")
        
except Exception as e:
    print(f"❌ Errore connessione: {e}")

print("\\n✅ Test completato!")

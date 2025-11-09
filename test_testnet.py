import hmac
import hashlib
import requests
import time
from urllib.parse import urlencode

# === CHIAVI TESTNET PULITE (senza spazi!) ===
API_KEY = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
API_SECRET = b"yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"

print("🔐 Testing Binance TESTNET...")
print(f"📝 API Key: {API_KEY[:10]}...{API_KEY[-10:]}")
print(f"📝 Secret: {API_SECRET[:10].decode()}...{API_SECRET[-10:].decode()}")

# URL TESTNET
BASE_URL = "https://testnet.binance.vision"

# Test 1: Server Time
try:
    response = requests.get(f'{BASE_URL}/api/v3/time', timeout=10)
    server_time = response.json()
    print(f"✅ Server Time: {server_time}")
except Exception as e:
    print(f"❌ Errore Server Time: {e}")

# Test 2: Account Info
timestamp = int(time.time() * 1000)
params = {
    'timestamp': timestamp,
    'recvWindow': 60000
}

query_string = urlencode(params)
signature = hmac.new(API_SECRET, query_string.encode('utf-8'), hashlib.sha256).hexdigest()
params['signature'] = signature

headers = {'X-MBX-APIKEY': API_KEY}
url = f'{BASE_URL}/api/v3/account'

try:
    response = requests.get(url, headers=headers, params=params, timeout=10)
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        account_info = response.json()
        print("🎉 SUCCESSO! TestNet API funzionante!")
        print(f"💰 Balances: {len(account_info['balances'])} assets")
        
        # Mostra balances (TestNet ha fondi fittizi)
        non_zero = [b for b in account_info['balances'] if float(b['free']) > 0 or float(b['locked']) > 0]
        for balance in non_zero:
            print(f"   {balance['asset']}: Free={balance['free']}, Locked={balance['locked']}")
            
    else:
        print(f"❌ Errore: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
except Exception as e:
    print(f"💥 Eccezione: {e}")

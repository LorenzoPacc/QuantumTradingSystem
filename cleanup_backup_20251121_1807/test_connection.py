import requests
import time

print("🔍 TEST CONNESSIONE API")
print("=" * 30)

apis = [
    ("Binance", "https://api.binance.com/api/v3/ping"),
    ("GitHub", "https://api.github.com"),
    ("Fear & Greed", "https://api.alternative.me/fng/")
]

for name, url in apis:
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        end = time.time()
        
        if response.status_code == 200:
            print(f"✅ {name}: CONNESSO ({response.status_code}) - {end-start:.2f}s")
        else:
            print(f"⚠️  {name}: Errore {response.status_code} - {end-start:.2f}s")
    except Exception as e:
        print(f"❌ {name}: ERRORE - {str(e)}")

print(f"\n🕒 Orario sistema: {time.strftime('%Y-%m-%d %H:%M:%S')}")

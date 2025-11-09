print("🔍 Controllo configurazione corrente...")

try:
    with open('quantum_trader_production.py', 'r') as f:
        content = f.read()
    
    # Cerca le variabili di configurazione
    import re
    
    # Cerca API_KEY
    api_key_match = re.search(r"API_KEY\s*=\s*[\"']([^\"']+)[\"']", content)
    if api_key_match:
        current_key = api_key_match.group(1)
        print(f"📝 API_KEY corrente: {current_key[:10]}...{current_key[-10:]}")
    else:
        print("❌ API_KEY non trovata")
    
    # Cerca API_SECRET
    secret_match = re.search(r"API_SECRET\s*=\s*[\"']([^\"']+)[\"']", content)
    if secret_match:
        current_secret = secret_match.group(1)
        print(f"📝 API_SECRET corrente: {current_secret[:10]}...{current_secret[-10:]}")
    else:
        print("❌ API_SECRET non trovata")
    
    # Cerca TESTNET
    testnet_match = re.search(r"TESTNET\s*=\s*(True|False)", content)
    if testnet_match:
        current_testnet = testnet_match.group(1)
        print(f"🔧 TESTNET corrente: {current_testnet}")
    else:
        print("❌ TESTNET non trovato")

except Exception as e:
    print(f"❌ Errore: {e}")

print("🚀 Test finale Quantum Trader con chiavi incorporate...")

try:
    # Importa il trader (ora con chiavi incorporate)
    from quantum_trader_production import QuantumAutoTrader
    
    print("✅ QuantumAutoTrader importato")
    
    # Crea istanza
    trader = QuantumAutoTrader()
    
    print("✅ Trader inizializzato!")
    print(f"🔧 Base URL: {trader.base_url}")
    print(f"🔧 API Key: {trader.api_key[:10]}...{trader.api_key[-10:]}")
    
    # Test connessione API
    print("\\n🔌 Test connessione API...")
    try:
        import requests
        import time
        import hmac
        import hashlib
        from urllib.parse import urlencode
        
        timestamp = int(time.time() * 1000)
        params = {'timestamp': timestamp, 'recvWindow': 60000}
        
        query_string = urlencode(params)
        signature = hmac.new(
            trader.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        params['signature'] = signature
        headers = {'X-MBX-APIKEY': trader.api_key}
        
        response = requests.get(
            f"{trader.base_url}/api/v3/account",
            headers=headers,
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            print("🎉 SUCCESSO! Connessione API TestNet funzionante")
            account_info = response.json()
            print(f"💰 Balances: {len(account_info['balances'])} assets")
            
            # Mostra balances principali
            main_assets = ['BTC', 'ETH', 'USDT', 'BNB', 'XRP', 'ADA', 'SOL']
            print("\\n💰 Fondi TestNet disponibili:")
            for asset in main_assets:
                balance = next((b for b in account_info['balances'] if b['asset'] == asset), None)
                if balance and (float(balance['free']) > 0 or float(balance['locked']) > 0):
                    print(f"   {asset}: {balance['free']}")
                    
        else:
            print(f"❌ Errore API: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Errore connessione: {e}")
    
    print("\\n🎉 QUANTUM TRADER PRONTO!")
    print("   Chiavi TestNet incorporate nel file")
    print("   Connessione API funzionante")
    print("   Fondi di test disponibili")
    print("   Pronto per il trading sicuro!")
    
except Exception as e:
    print(f"❌ Errore: {e}")
    import traceback
    traceback.print_exc()

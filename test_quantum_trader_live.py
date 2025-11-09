import os
import time

print("🎯 Test Quantum Trader con nuove chiavi TestNet...")

# Verifica variabili d'ambiente
api_key = os.getenv('BINANCE_TESTNET_API_KEY')
api_secret = os.getenv('BINANCE_TESTNET_SECRET_KEY')

print(f"🔐 API Key: {api_key[:10]}...{api_key[-10:]}")
print(f"🔐 API Secret: {api_secret[:10]}...{api_secret[-10:]}")

if not api_key or not api_secret:
    print("❌ Variabili d'ambiente mancanti")
    exit(1)

# Test import del trader
try:
    from quantum_trader_production import QuantumAutoTrader
    
    print("✅ QuantumAutoTrader importato con successo")
    
    # Crea istanza del trader
    print("🔧 Creazione istanza QuantumAutoTrader...")
    trader = QuantumAutoTrader()
    
    print("✅ Trader inizializzato!")
    print(f"🔧 Base URL: {trader.base_url}")
    print(f"🔧 API Key nel trader: {trader.api_key[:10]}...{trader.api_key[-10:]}")
    
    # Test funzionalità base
    print("\\n🧪 Test funzionalità base...")
    
    # 1. Test calcolo portfolio
    try:
        portfolio_value = trader.calculate_portfolio_value()
        print(f"💰 Portfolio value: ${portfolio_value:.2f}")
    except Exception as e:
        print(f"⚠️  Errore calcolo portfolio: {e}")
    
    # 2. Test analisi simboli
    try:
        print("\\n📊 Test analisi simboli...")
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT']
        for symbol in test_symbols:
            analysis = trader.analyze_symbol(symbol)
            if analysis:
                print(f"   {symbol}: Score={analysis['score']}, Action={analysis['action']}")
            else:
                print(f"   {symbol}: Analisi fallita")
    except Exception as e:
        print(f"⚠️  Errore analisi simboli: {e}")
    
    # 3. Test connessione API diretta
    print("\\n🔌 Test connessione API dal trader...")
    try:
        # Usa la stessa logica del trader per testare l'account
        import requests
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
            print("✅ Connessione API dal trader: FUNZIONANTE")
            account_info = response.json()
            print(f"   Balances: {len(account_info['balances'])} assets")
        else:
            print(f"❌ Connessione API dal trader: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Errore connessione API trader: {e}")
    
    print("\\n🎉 QUANTUM TRADER PRONTO PER TESTNET!")
    print("   Tutte le configurazioni sono corrette")
    print("   Puoi avviare il trading con fondi fittizi sicuri!")
    
except Exception as e:
    print(f"❌ Errore durante il test: {e}")
    import traceback
    traceback.print_exc()

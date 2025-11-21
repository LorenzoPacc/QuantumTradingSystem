import re

# Leggi il file del trader
with open('quantum_trader_production.py', 'r') as f:
    content = f.read()

# Cerca la sezione di inizializzazione Binance
if "self.client = Client(api_key, api_secret)" in content:
    # Sostituisci con gestione TestNet
    new_code = '''
        # Configurazione TestNet
        try:
            import json
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
            
            testnet_mode = config.get('binance', {}).get('testnet', False)
            if testnet_mode:
                self.client = Client(api_key, api_secret, testnet=True)
                print("🔧 MODALITÀ TESTNET ATTIVA - Trading sicuro con fondi fittizi")
            else:
                self.client = Client(api_key, api_secret)
                print("🔧 MODALITÀ PRODUCTION - Trading con fondi reali")
                
        except Exception as e:
            print(f"⚠️  Errore caricamento configurazione: {e}")
            self.client = Client(api_key, api_secret)
    '''
    
    content = content.replace("self.client = Client(api_key, api_secret)", new_code)
    print("✅ Patch TestNet applicata con successo!")
else:
    print("⚠️  Impossibile trovare la sezione di inizializzazione Binance")

# Salva il file modificato
with open('quantum_trader_production.py', 'w') as f:
    f.write(content)

print("✅ Quantum Trader aggiornato per TestNet!")

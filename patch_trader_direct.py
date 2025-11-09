print("🔧 Applicazione patch diretta per TestNet...")

# Leggi il file
with open('quantum_trader_production.py', 'r') as f:
    content = f.read()

# Nuove chiavi TestNet
NEW_API_KEY = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
NEW_API_SECRET = "yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"

# Sostituisci le righe che caricano dalle variabili d'ambiente con valori diretti
old_api_key_line = "API_KEY = os.getenv('BINANCE_TESTNET_API_KEY', '')"
new_api_key_line = f'API_KEY = "{NEW_API_KEY}"  # TestNet Key'

old_api_secret_line = "API_SECRET = os.getenv('BINANCE_TESTNET_SECRET_KEY', '')"  
new_api_secret_line = f'API_SECRET = "{NEW_API_SECRET}"  # TestNet Secret'

# Applica le sostituzioni
if old_api_key_line in content:
    content = content.replace(old_api_key_line, new_api_key_line)
    print("✅ API_KEY sostituita con valore diretto")
else:
    print("❌ Impossibile trovare la riga API_KEY")

if old_api_secret_line in content:
    content = content.replace(old_api_secret_line, new_api_secret_line)
    print("✅ API_SECRET sostituita con valore diretto")
else:
    print("❌ Impossibile trovare la riga API_SECRET")

# Salva il file modificato
with open('quantum_trader_production.py', 'w') as f:
    f.write(content)

print("✅ File quantum_trader_production.py aggiornato con chiavi TestNet!")
print("🔐 Le chiavi sono ora incorporate direttamente nel file")

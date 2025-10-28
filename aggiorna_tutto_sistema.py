#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

new_api_key = os.getenv("BINANCE_TESTNET_API_KEY")
new_api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")

print("🔄 AGGIORNAMENTO SISTEMA COMPLETO")
print("="*60)

if not new_api_key or not new_api_secret:
    print("❌ Nuove API keys non trovate nel file .env")
    print("   Aggiorna prima il file .env principale")
    exit(1)

print(f"🔑 Nuova API Key: {new_api_key[:12]}...{new_api_key[-4:]}")
print(f"🔒 Nuovo Secret: {new_api_secret[:8]}...{new_api_secret[-4:]}")
print("")

# File che DEVONO essere aggiornati
files_to_update = [
    {
        "file": "config/quantum_config.py",
        "pattern": "BINANCE_TESTNET",
        "description": "CONFIGURAZIONE PRINCIPALE"
    }
]

print("🎯 FILE DA AGGIORNARE MANUALMENTE:")
for item in files_to_update:
    if os.path.exists(item["file"]):
        print(f"  📝 {item['file']} - {item['description']}")
        
        # Mostra le righe correnti
        with open(item["file"], 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if item["pattern"] in line:
                    print(f"     Linea {i+1}: {line.strip()}")
    else:
        print(f"  ❌ {item['file']} - NON TROVATO")

print("")
print("✅ FILE CHE LEGGONO AUTOMATICAMENTE DA .env:")
auto_files = [
    "quantum_trader_ultimate_final.py",
    "quantum_trader_pro_final.py", 
    "test_api.py",
    "test_api_keys.py",
    "test_api_detailed.py",
    "test_api_robust.py",
    "test_api_fixed.py"
]

for file in auto_files:
    if os.path.exists(file):
        print(f"  ✅ {file} - AUTO-AGGIORNAMENTO")
    else:
        print(f"  ❌ {file} - NON TROVATO")

print("")
print("🔄 PROCEDURA:")
print("1. nano .env (già fatto)")
print("2. nano config/quantum_config.py")
print("3. Testa: python test_api_detailed.py")
print("4. Avvia: ./run_quantum_final_live.sh")
print("="*60)

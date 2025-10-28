#!/usr/bin/env python3
"""
RESET TESTNET BINANCE
Ottieni nuovi fondi per il testnet
"""

import requests
import time

# URL per reset testnet (documentazione Binance)
reset_url = "https://testnet.binance.vision/api/v3/account"

print("🔄 Reset Testnet Binance")
print("========================")

print("📝 Istruzioni per reset manuale:")
print("1. Vai su: https://testnet.binance.vision/")
print("2. Fai login con:")
print("   - Email/Password: Crea un account gratuito")
print("   - Oppure usa GitHub login")
print("3. Clicca 'Faucet' per ottenere fondi gratuiti")
print("4. Seleziona 'USDT' e richiedi fondi")
print("5. Usa queste API Key nel tuo .env:")
print("   - API Key: quella che hai già")
print("   - Secret Key: quella che hai già")
print("6. I fondi appariranno in pochi minuti")

print("\n💡 Alternative:")
print("• Crea nuovo account testnet per nuovi fondi")
print("• Usa paper trading con dati simulati")

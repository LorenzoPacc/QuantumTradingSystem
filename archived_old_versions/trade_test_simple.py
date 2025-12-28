#!/usr/bin/env python3
"""
Script semplificato per testare il trading su Binance TestNet
"""

import os
import sys

# Forza il caricamento del .env
from dotenv import load_dotenv
load_dotenv()

# Verifica API Key
API_KEY = os.getenv('BINANCE_TESTNET_API_KEY')
SECRET_KEY = os.getenv('BINANCE_TESTNET_SECRET_KEY')

if not API_KEY or API_KEY == 'la_tua_api_key_vera_qui':
    print("❌ ERRORE: Configura le tue API Key nel file .env")
    print("   Modifica il file .env con le tue chiavi reali")
    sys.exit(1)

print(f"✅ API Key configurate: {API_KEY[:10]}...")

# Importa il trader
try:
    from quantum_trader_testnet_final import BinanceTestNetTrader
except ImportError:
    print("❌ File quantum_trader_testnet_final.py non trovato")
    sys.exit(1)

# Test connessione
try:
    print("🔌 Connessione a Binance TestNet...")
    trader = BinanceTestNetTrader()
    print("✅ Connessione riuscita!")
    
    # Mostra stato
    trader.print_status()
    
    # Test ordine
    print("\n🎯 Test ordine BTC...")
    result = trader.auto_trade('BTCUSDT', {'signal': 'BUY', 'score': 0.8})
    
    if result:
        print("✅ ORDINE REALE INVIATO AL TESTNET!")
        print(f"   Order ID: {result.get('orderId', 'N/A')}")
    else:
        print("⚠️  Nessun ordine eseguito (normale per fondi insufficienti o prezzo)")
        
except Exception as e:
    print(f"❌ Errore: {e}")

print("\n✨ Test completato!")

#!/usr/bin/env python3
"""
Configurazione Trading Automatico
"""

# === BINANCE TESTNET ===
TESTNET = True
BASE_URL = "https://testnet.binance.vision" if TESTNET else "https://api.binance.com"

# === API KEYS ===
import os
from pathlib import Path

env_file = Path('.env.testnet')
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

API_KEY = os.getenv('BINANCE_TESTNET_API_KEY', 'YOUR_API_KEY_HERE')
API_SECRET = os.getenv('BINANCE_TESTNET_SECRET_KEY', 'YOUR_SECRET_KEY_HERE')

# === TRADING AUTOMATICO ===
AUTO_TRADING = {
    "enabled": True,
    "mode": "FULL_AUTO",
    "buy_threshold": 3.0,
    "sell_threshold": 2.3,
    "max_trade_size": 0.10,
    "min_trade_usdt": 10.0,
    "stop_loss": 0.05,
    "take_profit": 0.08
}

print("✅ Configurazione caricata")

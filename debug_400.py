#!/usr/bin/env python3
"""
Debug dell'errore 400 delle API Binance
"""

import requests
import hmac
import hashlib
import time
import sys
import os

sys.path.append(os.path.dirname(__file__))

try:
    from config.quantum_config import BINANCE_TESTNET
    
    api_key = BINANCE_TESTNET["api_key"]
    api_secret = BINANCE_TESTNET["api_secret"]
    base_url = BINANCE_TESTNET["base_url"]
    
    print("🔍 Debug errore 400...")
    print(f"API Key: {api_key}")
    print(f"API Secret: {api_secret[:10]}...")
    
    # Test 1: Richiesta base
    timestamp = int(time.time() * 1000)
    params = {'timestamp': timestamp}
    
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(
        api_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    params['signature'] = signature
    headers = {"X-MBX-APIKEY": api_key}
    
    print("📡 Invio richiesta...")
    response = requests.get(
        f"{base_url}/account",
        params=params,
        headers=headers,
        timeout=10
    )
    
    print(f"📊 Status Code: {response.status_code}")
    print(f"📄 Response: {response.text}")
    
    if response.status_code == 400:
        error_data = response.json()
        print(f"🔴 Errore 400: {error_data}")
        print("\n💡 Possibili cause:")
        print("1. API Key disabilitata su Binance Testnet")
        print("2. API Key scaduta")
        print("3. Permessi insufficienti")
        print("4. Formato API Key non valido")
        
except Exception as e:
    print(f"💥 Eccezione: {e}")

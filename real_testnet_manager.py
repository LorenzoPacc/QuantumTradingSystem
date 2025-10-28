#!/usr/bin/env python3
"""
Manager reale per Binance Testnet con API vere
"""

import requests
import hmac
import hashlib
import time
import json
from datetime import datetime

# Configurazione diretta (modifica con le tue chiavi)
TESTNET_CONFIG = {
    "api_key": "la_tua_api_key_qui",      # ✅ SOSTITUISCI CON LA TUA API KEY
    "api_secret": "il_tuo_secret_qui",    # ✅ SOSTITUISCI CON IL TUO SECRET
    "base_url": "https://testnet.binance.vision/api/v3"
}

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]

class RealBinanceTestnetManager:
    def __init__(self):
        self.api_key = TESTNET_CONFIG["api_key"]
        self.api_secret = TESTNET_CONFIG["api_secret"]
        self.base_url = TESTNET_CONFIG["base_url"]
    
    def _generate_signature(self, params):
        """Genera signature HMAC SHA256"""
        query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(self, endpoint, params=None, signed=False):
        """Esegue richiesta API"""
        url = f"{self.base_url}/{endpoint}"
        headers = {"X-MBX-APIKEY": self.api_key}
        
        if params is None:
            params = {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            return response.json()
        except Exception as e:
            print(f"❌ Errore API: {e}")
            return None
    
    def get_account_info(self):
        """Ottieni informazioni account reali da Testnet"""
        print("🔗 Connessione a Binance Testnet...")
        
        # Se le credenziali sono quelle di default, usa dati simulati
        if self.api_key == "la_tua_api_key_qui":
            print("⚠️ Usando dati simulati - configura le tue API Key in real_testnet_manager.py")
            return self.get_simulated_account()
        
        data = self._make_request("account", {}, signed=True)
        
        if data and 'balances' in data:
            return self._parse_account_data(data)
        else:
            print("❌ Errore nel recupero dati reali, uso simulati")
            return self.get_simulated_account()
    
    def _parse_account_data(self, data):
        """Elabora i dati dell'account"""
        balances = {}
        total_usdt = 0
        
        # Prezzi correnti
        prices = self.get_current_prices()
        
        for balance in data['balances']:
            asset = balance['asset']
            free = float(balance['free'])
            locked = float(balance['locked'])
            
            if free > 0 or locked > 0:
                balances[asset] = {
                    'free': free,
                    'locked': locked,
                    'total': free + locked
                }
                
                # Calcola valore in USDT
                if asset == 'USDT':
                    total_usdt += free
                else:
                    symbol = f"{asset}USDT"
                    if symbol in prices:
                        total_usdt += free * prices[symbol]
        
        return {
            'balances': balances,
            'total_usdt': total_usdt,
            'update_time': datetime.now().isoformat(),
            'source': 'REAL_TESTNET'
        }
    
    def get_current_prices(self):
        """Prezzi correnti reali"""
        prices = {}
        for symbol in SYMBOLS:
            try:
                data = self._make_request("ticker/price", {"symbol": symbol})
                if data and 'price' in data:
                    prices[symbol] = float(data['price'])
            except:
                # Fallback prices
                prices[symbol] = 107028.70 if symbol == "BTCUSDT" else \
                               3735.25 if symbol == "ETHUSDT" else \
                               178.60 if symbol == "SOLUSDT" else 1.0
        return prices
    
    def get_simulated_account(self):
        """Account simulato per testing"""
        prices = self.get_current_prices()
        
        simulated_balances = {
            'USDT': {'free': 4850.75, 'locked': 0, 'total': 4850.75},
            'BTC': {'free': 0.0052, 'locked': 0, 'total': 0.0052},
            'ETH': {'free': 0.128, 'locked': 0, 'total': 0.128},
            'SOL': {'free': 2.5, 'locked': 0, 'total': 2.5}
        }
        
        # Calcola totale USDT con prezzi reali
        total_usdt = simulated_balances['USDT']['free']
        btc_price = prices.get('BTCUSDT', 107028.70)
        eth_price = prices.get('ETHUSDT', 3735.25)
        sol_price = prices.get('SOLUSDT', 178.60)
        
        total_usdt += simulated_balances['BTC']['free'] * btc_price
        total_usdt += simulated_balances['ETH']['free'] * eth_price
        total_usdt += simulated_balances['SOL']['free'] * sol_price
        
        return {
            'balances': simulated_balances,
            'total_usdt': total_usdt,
            'pnl_today': +87.32,
            'pnl_percent_today': +1.78,
            'update_time': datetime.now().isoformat(),
            'source': 'SIMULATED'
        }
    
    def test_connection(self):
        """Test connessione a Testnet"""
        print("🧪 Test connessione Binance Testnet...")
        data = self.get_account_info()
        
        if data['source'] == 'REAL_TESTNET':
            print("✅ Connesso a Binance Testnet REALE!")
            print(f"💰 Balance totale: ${data['total_usdt']:,.2f}")
        else:
            print("⚠️ Usando dati simulati")
            print("💡 Modifica real_testnet_manager.py con le tue API Key")

# Test
if __name__ == "__main__":
    manager = RealBinanceTestnetManager()
    manager.test_connection()

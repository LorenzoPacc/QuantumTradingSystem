#!/usr/bin/env python3
"""
Auto Trading Engine
"""
import requests
import hmac
import hashlib
import time
from config_auto_trading import *

class AutoTradingEngine:
    def __init__(self):
        self.base_url = BASE_URL
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.config = AUTO_TRADING
        
    def _sign_request(self, params):
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def get_balance(self, asset='USDT'):
        try:
            endpoint = "/api/v3/account"
            timestamp = int(time.time() * 1000)
            params = {'timestamp': timestamp}
            params['signature'] = self._sign_request(params)
            headers = {'X-MBX-APIKEY': self.api_key}
            
            response = requests.get(f"{self.base_url}{endpoint}", params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                account = response.json()
                for b in account['balances']:
                    if b['asset'] == asset:
                        return float(b['free'])
            return 0.0
        except Exception as e:
            print(f"❌ Errore balance: {e}")
            return 0.0
    
    def get_price(self, symbol):
        try:
            url = f"{self.base_url}/api/v3/ticker/price"
            response = requests.get(url, params={'symbol': symbol}, timeout=5)
            if response.status_code == 200:
                return float(response.json()['price'])
            return None
        except:
            return None
    
    def execute_market_buy(self, symbol, usdt_amount):
        if not self.config['enabled']:
            return None
        
        if usdt_amount < self.config['min_trade_usdt']:
            print(f"⚠️  Importo troppo piccolo: ${usdt_amount:.2f}")
            return None
        
        try:
            endpoint = "/api/v3/order"
            timestamp = int(time.time() * 1000)
            
            params = {
                'symbol': symbol,
                'side': 'BUY',
                'type': 'MARKET',
                'quoteOrderQty': int(usdt_amount),
                'timestamp': timestamp
            }
            
            params['signature'] = self._sign_request(params)
            headers = {'X-MBX-APIKEY': self.api_key}
            
            response = requests.post(f"{self.base_url}{endpoint}", params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                order = response.json()
                print(f"✅ BUY: {symbol} - ${usdt_amount}")
                return order
            else:
                print(f"❌ BUY fallito: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Errore BUY: {e}")
            return None
    
    def execute_market_sell(self, symbol, quantity):
        if not self.config['enabled']:
            return None
        
        try:
            quantity = round(quantity, 4)
            if quantity == 0:
                return None
            
            endpoint = "/api/v3/order"
            timestamp = int(time.time() * 1000)
            
            params = {
                'symbol': symbol,
                'side': 'SELL',
                'type': 'MARKET',
                'quantity': quantity,
                'timestamp': timestamp
            }
            
            params['signature'] = self._sign_request(params)
            headers = {'X-MBX-APIKEY': self.api_key}
            
            response = requests.post(f"{self.base_url}{endpoint}", params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                order = response.json()
                print(f"✅ SELL: {quantity} {symbol}")
                return order
            else:
                print(f"❌ SELL fallito: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Errore SELL: {e}")
            return None
    
    def decide_and_execute(self, symbol, score):
        buy_threshold = self.config['buy_threshold']
        sell_threshold = self.config['sell_threshold']
        
        usdt_balance = self.get_balance('USDT')
        current_price = self.get_price(symbol)
        
        if not current_price:
            return None
        
        if score >= buy_threshold:
            trade_amount = usdt_balance * self.config['max_trade_size']
            if trade_amount >= self.config['min_trade_usdt']:
                print(f"🟢 DECISIONE: BUY {symbol} (Score: {score:.2f})")
                return self.execute_market_buy(symbol, trade_amount)
            else:
                print(f"⏸️  {symbol}: HOLD - Balance insufficiente")
                
        elif score <= sell_threshold:
            asset = symbol.replace('USDT', '')
            position = self.get_balance(asset)
            if position > 0:
                print(f"🔴 DECISIONE: SELL {symbol} (Score: {score:.2f})")
                return self.execute_market_sell(symbol, position)
            else:
                print(f"⏸️  {symbol}: HOLD - Nessuna posizione")
                
        else:
            print(f"⏸️  {symbol}: HOLD (Score: {score:.2f})")
        
        return None

if __name__ == "__main__":
    engine = AutoTradingEngine()
    print("✅ Motore trading inizializzato")

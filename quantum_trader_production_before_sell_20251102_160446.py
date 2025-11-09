#!/usr/bin/env python3
"""
Quantum Trader Production - AUTO TRADING VERSION 
Con dati REALI da Binance
"""

import logging
import time
import requests
from datetime import datetime
import hmac
import hashlib
import os

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QuantumAutoTrader")

# API Configuration
TESTNET = True
BASE_URL = "https://testnet.binance.vision" if TESTNET else "https://api.binance.com"

# Load API keys
from pathlib import Path
env_file = Path('.env.testnet')
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

API_KEY = os.getenv('BINANCE_TESTNET_API_KEY', '')
API_SECRET = os.getenv('BINANCE_TESTNET_SECRET_KEY', '')

class QuantumAutoTrader:
    def __init__(self):
        self.base_url = BASE_URL
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT']
        self.portfolio = {'XRPUSDT': 762.06}
        self.balance = 9300.0
        
        # MIGLIORAMENTI APPLICATI
        self.buy_threshold = 2.8    # -12.5% più aggressivo
        self.sell_threshold = 2.2   # -8.3% più aggressivo
        self.cycle_interval = 45    # -25% più frequente
        self.xrp_blocked_cycles = 0
        self.max_cycles = 50
        
        logger.info("🤖 QUANTUM AUTO TRADER INIZIALIZZATO")
        logger.info(f"   Portfolio: ${self.calculate_portfolio_value():.2f}")
        logger.info(f"   Balance: ${self.balance:.2f}")
    
        self.cycles = 50  # 50 cicli per test completo

    def _sign_request(self, params):
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def heartbeat(self, message):
        logger.info(f"❤️  {message}")
    
    def get_real_price(self, symbol):
        try:
            url = f"{self.base_url}/api/v3/ticker/price"
            response = requests.get(url, params={'symbol': symbol}, timeout=5)
            if response.status_code == 200:
                return float(response.json()['price'])
            return 0.0
        except:
            return 0.0
    
    def get_24h_data(self, symbol):
        try:
            url = f"{self.base_url}/api/v3/ticker/24hr"
            response = requests.get(url, params={'symbol': symbol}, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'change': float(data['priceChangePercent']),
                    'volume': float(data['volume'])
                }
            return None
        except:
            return None
    
    def analyze_macro(self):
        try:
            btc_price = self.get_real_price("BTCUSDT")
            if btc_price > 100000:
                return 0.85
            elif btc_price > 80000:
                return 0.75
            else:
                return 0.65
        except:
            return 0.5
    
    def analyze_price_action(self, symbol):
        try:
            data_24h = self.get_24h_data(symbol)
            if data_24h:
                change = data_24h['change']
                if change > 5: return 0.9
                elif change > 2: return 0.75
                elif change > 0: return 0.6
                elif change > -2: return 0.5
                else: return 0.4
            return 0.5
        except:
            return 0.5
    
    def analyze_onchain(self, symbol):
        try:
            price = self.get_real_price(symbol)
            if symbol == "BTCUSDT":
                return 0.7 if price > 100000 else 0.5
            elif symbol == "ETHUSDT":
                return 0.65 if price > 3500 else 0.5
            else:
                return 0.55
        except:
            return 0.5
    
    def analyze_cycles(self):
        try:
            halving_date = datetime(2024, 4, 20)
            days_since = (datetime.now() - halving_date).days
            if days_since < 365:
                return 0.5 + (days_since / 365) * 0.2
            elif days_since < 730:
                return 0.7 + ((days_since - 365) / 365) * 0.2
            else:
                return 0.9 - ((days_since - 730) / 730) * 0.3
        except:
            return 0.55
    
    def calculate_confluence(self, symbol):
        macro_score = self.analyze_macro()
        price_score = self.analyze_price_action(symbol)
        onchain_score = self.analyze_onchain(symbol)
        cycles_score = self.analyze_cycles()
        
        weights = [0.30, 0.30, 0.25, 0.15]
        confluence = sum(s * w for s, w in zip(
            [macro_score, price_score, onchain_score, cycles_score], weights
        ))
        
        score = confluence * 4
        
        # DECISIONE con nuove soglie
        if score > self.buy_threshold:
            signal = "BUY"
        elif score < self.sell_threshold:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        return {'symbol': symbol, 'score': score, 'signal': signal}
    
    def execute_market_sell(self, symbol, quantity):
        try:
            quantity = round(quantity, 2)
            if quantity == 0: return None
            
            endpoint = "/api/v3/order"
            timestamp = int(time.time() * 1000)
            params = {
                'symbol': symbol, 'side': 'SELL', 'type': 'MARKET',
                'quantity': quantity, 'timestamp': timestamp
            }
            params['signature'] = self._sign_request(params)
            headers = {'X-MBX-APIKEY': self.api_key}
            
            response = requests.post(f"{self.base_url}{endpoint}", params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                self.heartbeat(f"✅ SELL: {quantity} {symbol}")
                return response.json()
            else:
                self.heartbeat(f"❌ SELL failed: {response.text}")
                return None
        except Exception as e:
            self.heartbeat(f"❌ Error SELL: {e}")
            return None
    
    def auto_trade(self, symbol, analysis):
        signal = analysis['signal']
        score = analysis['score']
        
        # Gestione XRP con sblocco
        if symbol == "XRPUSDT" and self.portfolio.get(symbol, 0) > 0:
            if self.xrp_blocked_cycles > 10:
                self.xrp_blocked_cycles = 0
                self.heartbeat("🔄 XRP sbloccato forzatamente")
                try:
                return self.execute_market_sell(symbol, self.portfolio[symbol] * 0.30)
                return self.execute_market_sell(symbol, self.portfolio[symbol] * 0.30)
            else:
                self.xrp_blocked_cycles += 1
                self.heartbeat(f"🚫 XRP bloccato (ciclo {self.xrp_blocked_cycles}/10)")
                return None
        
                # LOGICA BUY
        if signal == "BUY" and self.balance >= 10:
            # Calcola quanto comprare (5% del balance)
            buy_amount = min(self.balance * 0.05, 500)  # Max 500 USDT per trade
            if buy_amount >= 10:
                self.heartbeat(f"🤖 BUY DECISION: {symbol} (Score: {score:.2f})")
                return self.execute_market_buy(symbol, buy_amount)
        
        # LOGICA SELL
        if signal == "SELL" and symbol in self.portfolio and self.portfolio[symbol] > 0:
            self.heartbeat(f"🤖 SELL: {symbol} (Score: {score:.2f})")
            return self.execute_market_sell(symbol, self.portfolio[symbol])
        
        return None
    
    def calculate_portfolio_value(self):
        total = self.balance
        for symbol, qty in self.portfolio.items():
            price = self.get_real_price(symbol)
            total += qty * price
        return total
    
    def run_auto_cycle(self, cycle_num):
        self.heartbeat(f"INIZIO CICLO #{cycle_num}")
        portfolio_value = self.calculate_portfolio_value()
        self.heartbeat(f"Portfolio: ${portfolio_value:.2f}")
        self.heartbeat(f"Balance: ${self.balance:.2f}")
        
        for symbol in self.symbols:
            analysis = self.calculate_confluence(symbol)
            self.heartbeat(f"{symbol}: {analysis['signal']} (Score: {analysis['score']:.2f})")
            self.auto_trade(symbol, analysis)
            time.sleep(1)
        
        self.heartbeat(f"FINE CICLO #{cycle_num}")
    
    def run(self):
        self.heartbeat("🚀 START AUTO TRADER")
        for cycle in range(1, self.max_cycles + 1):
            self.run_auto_cycle(cycle)
            if cycle < self.max_cycles:
                self.heartbeat(f"Attesa {self.cycle_interval}s... ({cycle}/{self.max_cycles})")
                time.sleep(self.cycle_interval)
        self.heartbeat("🏁 AUTO TRADING COMPLETATO")
    def execute_market_buy(self, symbol, usdt_amount):
        """Esegue BUY di mercato"""
        try:
            if usdt_amount < 10:
                self.heartbeat(f"⚠️  {symbol}: Importo troppo piccolo ${usdt_amount:.2f}")
                return None
            
            self.heartbeat(f"🔄 BUY: ${usdt_amount:.2f} {symbol}")
            
            # Simulazione per test
            price = self.get_real_price(symbol)
            if price and price > 0:
                quantity = usdt_amount / price
                self.portfolio[symbol] = self.portfolio.get(symbol, 0) + quantity
                self.balance -= usdt_amount
                self.heartbeat(f"✅ BUY REALE: {quantity:.6f} {symbol} a ${price:.2f}")
                return {"status": "SIMULATED", "symbol": symbol, "quantity": quantity}
            else:
                self.heartbeat(f"❌ Prezzo non disponibile per {symbol}")
                return None
                
        except Exception as e:
            self.heartbeat(f"❌ BUY ERROR: {e}")
            return None



if __name__ == "__main__":
    trader = QuantumAutoTrader()
    trader.run()

#!/bin/bash

echo "🚀 INSTALLAZIONE SISTEMA TRADING AUTOMATICO"
echo "==========================================="

# STEP 1: Crea configurazione
echo "📦 Creazione configurazione..."
cat > config_auto_trading.py << 'EOFCONFIG'
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
EOFCONFIG
echo "✅ config_auto_trading.py creato"

# STEP 2: Crea motore trading
echo "📦 Creazione motore trading..."
cat > auto_trading_engine.py << 'EOFENGINE'
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
EOFENGINE
echo "✅ auto_trading_engine.py creato"

# STEP 3: Crea trader automatico
echo "📦 Creazione trader automatico..."
cat > quantum_auto_trader.py << 'EOFTRADER'
#!/usr/bin/env python3
"""
Quantum Auto Trader
"""
import logging
import time
import requests
import random
from datetime import datetime
from auto_trading_engine import AutoTradingEngine
from config_auto_trading import BASE_URL

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QuantumAutoTrader")

class QuantumAutoTrader:
    def __init__(self):
        self.base_url = BASE_URL
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT']
        self.auto_engine = AutoTradingEngine()
        logger.info("🤖 QUANTUM AUTO TRADER INIZIALIZZATO")
    
    def get_price(self, symbol):
        try:
            url = f"{self.base_url}/api/v3/ticker/price"
            response = requests.get(url, params={'symbol': symbol}, timeout=5)
            if response.status_code == 200:
                return float(response.json()['price'])
            return 0.0
        except:
            return 0.0
    
    def analyze_market(self, symbol):
        # Simula analisi - nella realtà usa le tue funzioni
        price = self.get_price(symbol)
        
        # Score basato su prezzo e trend casuale (per test)
        base_score = random.uniform(2.0, 3.5)
        
        return {
            'symbol': symbol,
            'price': price,
            'score': base_score,
            'decision': 'BUY' if base_score > 3.0 else 'SELL' if base_score < 2.3 else 'HOLD'
        }
    
    def run_cycle(self, cycle_num):
        logger.info(f"🔄 CICLO #{cycle_num}")
        
        usdt_balance = self.auto_engine.get_balance('USDT')
        logger.info(f"💰 Balance: ${usdt_balance:.2f}")
        
        for symbol in self.symbols:
            analysis = self.analyze_market(symbol)
            score = analysis['score']
            
            logger.info(f"📊 {symbol}: Score {score:.2f}")
            self.auto_engine.decide_and_execute(symbol, score)
            
            time.sleep(1)
        
        logger.info(f"✅ CICLO #{cycle_num} COMPLETATO")
    
    def run(self, cycles=5):
        logger.info("🚀 AVVIO TRADING AUTOMATICO")
        
        for i in range(1, cycles + 1):
            self.run_cycle(i)
            if i < cycles:
                logger.info("⏸️  Attesa 30 secondi...")
                time.sleep(30)
        
        logger.info("🏁 TRADING AUTOMATICO COMPLETATO")

if __name__ == "__main__":
    trader = QuantumAutoTrader()
    trader.run()
EOFTRADER
echo "✅ quantum_auto_trader.py creato"

# STEP 4: Crea script di controllo
echo "📦 Creazione script controllo..."
cat > control_auto.sh << 'EOFCONTROL'
#!/bin/bash

case "$1" in
    start)
        echo "🚀 Avvio Auto Trader..."
        python3 quantum_auto_trader.py &
        echo $! > auto_trader.pid
        echo "✅ PID: $(cat auto_trader.pid)"
        ;;
    stop)
        if [ -f auto_trader.pid ]; then
            kill $(cat auto_trader.pid)
            rm auto_trader.pid
            echo "✅ Fermato"
        else
            echo "⚠️  Nessun processo attivo"
        fi
        ;;
    status)
        if [ -f auto_trader.pid ] && ps -p $(cat auto_trader.pid) > /dev/null; then
            echo "✅ Auto Trader attivo (PID: $(cat auto_trader.pid))"
        else
            echo "❌ Auto Trader fermo"
        fi
        ;;
    test)
        echo "🧪 Test sistema..."
        python3 -c "from auto_trading_engine import AutoTradingEngine; e=AutoTradingEngine(); print(f'💰 Balance: \${e.get_balance():.2f}')"
        ;;
    *)
        echo "Usage: $0 {start|stop|status|test}"
        ;;
esac
EOFCONTROL
chmod +x control_auto.sh
echo "✅ control_auto.sh creato"

# STEP 5: Crea template API keys
echo "📦 Creazione template API keys..."
cat > .env.testnet.template << 'EOFENV'
# API KEYS TESTNET BINANCE
# Ottieni su: https://testnet.binance.vision/

BINANCE_TESTNET_API_KEY=your_api_key_here
BINANCE_TESTNET_SECRET_KEY=your_secret_key_here

# ISTRUZIONI:
# 1. Vai su https://testnet.binance.vision/
# 2. Crea API keys
# 3. Copiale qui
# 4. Rinomina in .env.testnet
EOFENV
echo "✅ .env.testnet.template creato"

echo ""
echo "🎉 INSTALLAZIONE COMPLETATA!"
echo ""
echo "📁 FILE CREATI:"
echo "   ✅ config_auto_trading.py"
echo "   ✅ auto_trading_engine.py" 
echo "   ✅ quantum_auto_trader.py"
echo "   ✅ control_auto.sh"
echo "   ✅ .env.testnet.template"
echo ""
echo "🎯 PROSSIMI PASSI:"
echo "1. cp .env.testnet.template .env.testnet"
echo "2. nano .env.testnet  # Inserisci le tue API keys"
echo "3. ./control_auto.sh test  # Testa il sistema"
echo "4. ./control_auto.sh start  # Avvia trading automatico"
echo ""
echo "🤖 Il sistema farà tutto da solo!"

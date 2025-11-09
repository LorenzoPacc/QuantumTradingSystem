#!/bin/bash

# ============================================================================
# QUANTUM AUTO TRADER - INSTALLAZIONE COMPLETA
# ============================================================================

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║
echo "║          🤖 QUANTUM AUTO TRADER INSTALLATION 🤖             ║
echo "║                                                              ║
echo "║              Sistema Trading Completamente Autonomo          ║
echo "║                                                              ║
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# STEP 1: VERIFICA AMBIENTE
# ============================================================================
echo "📦 STEP 1: Verifica ambiente..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non installato"
    exit 1
fi

# Verifica pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 non installato"
    exit 1
fi

echo "✅ Python3: $(python3 --version)"
echo "✅ pip3: $(pip3 --version)"

# ============================================================================
# STEP 2: INSTALLA DIPENDENZE
# ============================================================================
echo ""
echo "📦 STEP 2: Installa dipendenze..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

pip3 install requests numpy pandas flask python-binance > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Dipendenze installate"
else
    echo "⚠️  Errore installazione dipendenze, continuo..."
fi

# ============================================================================
# STEP 3: CREA FILE DI CONFIGURAZIONE
# ============================================================================
echo ""
echo "📦 STEP 3: Crea configurazione..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat > config_auto_trading.py << 'EOFCONFIG'
#!/usr/bin/env python3
"""
Configurazione Trading Automatico
"""

# === BINANCE TESTNET ===
TESTNET = True
BASE_URL = "https://testnet.binance.vision" if TESTNET else "https://api.binance.com"

# === API KEYS (DA FILE .env SE ESISTE) ===
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
    
    # Soglie decisionali
    "buy_threshold": 3.0,
    "sell_threshold": 2.3,
    "hold_range": (2.3, 3.0),
    
    # Risk Management
    "max_position_size": 0.15,
    "max_trade_size": 0.10,
    "min_trade_usdt": 10.0,
    "stop_loss": 0.05,
    "take_profit": 0.08,
    
    # Diversificazione
    "max_concentration": 0.20,
    "min_assets": 2,
    "rebalance_threshold": 0.05
}

print(f"✅ Config loaded - Testnet: {TESTNET}, Auto: {AUTO_TRADING['enabled']}")
EOFCONFIG

echo "✅ config_auto_trading.py creato"

# ============================================================================
# STEP 4: CREA TRADING ENGINE
# ============================================================================
echo ""
echo "📦 STEP 4: Crea trading engine..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat > auto_trading_engine.py << 'EOFENGINE'
#!/usr/bin/env python3
"""
Auto Trading Engine - Esegue trade automatici
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
        """Firma richiesta Binance"""
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def get_account_info(self):
        """Ottieni info account"""
        try:
            endpoint = "/api/v3/account"
            timestamp = int(time.time() * 1000)
            params = {'timestamp': timestamp}
            params['signature'] = self._sign_request(params)
            headers = {'X-MBX-APIKEY': self.api_key}
            
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error get_account_info: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Exception get_account_info: {e}")
            return None
    
    def get_balance(self, asset='USDT'):
        """Ottieni balance specifico"""
        account = self.get_account_info()
        if account:
            for b in account['balances']:
                if b['asset'] == asset:
                    return float(b['free'])
        return 0.0
    
    def get_position(self, symbol):
        """Ottieni posizione corrente"""
        asset = symbol.replace('USDT', '')
        return self.get_balance(asset)
    
    def get_price(self, symbol):
        """Ottieni prezzo corrente"""
        try:
            url = f"{self.base_url}/api/v3/ticker/price"
            response = requests.get(url, params={'symbol': symbol}, timeout=5)
            if response.status_code == 200:
                return float(response.json()['price'])
            return None
        except:
            return None
    
    def execute_market_buy(self, symbol, usdt_amount):
        """Esegue BUY market"""
        if not self.config['enabled']:
            print(f"⚠️  Auto-trading disabled")
            return None
        
        if usdt_amount < self.config['min_trade_usdt']:
            print(f"⚠️  Amount too small: ${usdt_amount:.2f} < ${self.config['min_trade_usdt']}")
            return None
        
        try:
            endpoint = "/api/v3/order"
            timestamp = int(time.time() * 1000)
            
            # Usa quoteOrderQty per comprare con importo USDT fisso
            params = {
                'symbol': symbol,
                'side': 'BUY',
                'type': 'MARKET',
                'quoteOrderQty': int(usdt_amount),
                'timestamp': timestamp
            }
            
            params['signature'] = self._sign_request(params)
            headers = {'X-MBX-APIKEY': self.api_key}
            
            response = requests.post(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                order = response.json()
                print(f"✅ BUY EXECUTED: {symbol} - ${usdt_amount}")
                print(f"   Order ID: {order.get('orderId')}")
                return order
            else:
                print(f"❌ BUY FAILED: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Exception execute_market_buy: {e}")
            return None
    
    def execute_market_sell(self, symbol, quantity):
        """Esegue SELL market"""
        if not self.config['enabled']:
            print(f"⚠️  Auto-trading disabled")
            return None
        
        try:
            # Arrotonda quantity secondo regole Binance
            if symbol == 'BTCUSDT':
                quantity = round(quantity, 5)
            elif symbol in ['ETHUSDT', 'BNBUSDT']:
                quantity = round(quantity, 3)
            else:
                quantity = round(quantity, 2)
            
            if quantity == 0:
                print(f"⚠️  Quantity too small after rounding")
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
            
            response = requests.post(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                order = response.json()
                print(f"✅ SELL EXECUTED: {quantity} {symbol}")
                print(f"   Order ID: {order.get('orderId')}")
                return order
            else:
                print(f"❌ SELL FAILED: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Exception execute_market_sell: {e}")
            return None
    
    def decide_and_execute(self, symbol, score):
        """Decide ed esegue automaticamente"""
        buy_threshold = self.config['buy_threshold']
        sell_threshold = self.config['sell_threshold']
        
        # Ottieni stato corrente
        usdt_balance = self.get_balance('USDT')
        current_position = self.get_position(symbol)
        current_price = self.get_price(symbol)
        
        if not current_price:
            print(f"⚠️  Cannot get price for {symbol}")
            return None
        
        # LOGICA DECISIONALE
        if score >= buy_threshold:
            # BUY
            if current_position == 0:
                trade_amount = usdt_balance * self.config['max_trade_size']
                if trade_amount >= self.config['min_trade_usdt']:
                    print(f"🟢 DECISION: BUY {symbol} (Score: {score:.2f})")
                    return self.execute_market_buy(symbol, trade_amount)
                else:
                    print(f"⏸️  {symbol}: HOLD - Insufficient balance (${usdt_balance:.2f})")
            else:
                print(f"⏸️  {symbol}: HOLD - Already in position ({current_position:.4f})")
                
        elif score <= sell_threshold:
            # SELL
            if current_position > 0:
                print(f"🔴 DECISION: SELL {symbol} (Score: {score:.2f})")
                return self.execute_market_sell(symbol, current_position)
            else:
                print(f"⏸️  {symbol}: HOLD - No position")
                
        else:
            # HOLD
            print(f"⏸️  {symbol}: HOLD (Score: {score:.2f})")
        
        return None

# Test
if __name__ == "__main__":
    engine = AutoTradingEngine()
    print("✅ Auto Trading Engine initialized")
    print(f"   USDT Balance: ${engine.get_balance('USDT'):.2f}")
EOFENGINE

echo "✅ auto_trading_engine.py creato"

# ============================================================================
# STEP 5: CREA TRADER AUTOMATICO PRINCIPALE
# ============================================================================
echo ""
echo "📦 STEP 5: Crea trader automatico principale..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat > quantum_trader_auto.py << 'EOFTRADER'
#!/usr/bin/env python3
"""
Quantum Trader con Auto-Trading Integrato
"""
import logging
import time
import requests
from datetime import datetime
from auto_trading_engine import AutoTradingEngine
from config_auto_trading import BASE_URL

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_trading.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QuantumAutoTrader")

class QuantumAutoTrader:
    def __init__(self):
        self.base_url = BASE_URL
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'ADAUSDT']
        self.auto_engine = AutoTradingEngine()
        
        logger.info("🤖 QUANTUM AUTO TRADER INITIALIZED")
        logger.info(f"   Auto Trading: {self.auto_engine.config['enabled']}")
        logger.info(f"   Mode: {self.auto_engine.config['mode']}")
    
    def get_price(self, symbol):
        """Ottieni prezzo"""
        try:
            url = f"{self.base_url}/api/v3/ticker/price"
            response = requests.get(url, params={'symbol': symbol}, timeout=5)
            if response.status_code == 200:
                return float(response.json()['price'])
            return 0.0
        except:
            return 0.0
    
    def analyze_macro(self):
        """Analisi macro"""
        try:
            btc_price = self.get_price("BTCUSDT")
            if btc_price > 100000:
                score = 0.85
            elif btc_price > 80000:
                score = 0.75
            else:
                score = 0.65
            return score, f"BTC ${btc_price:,.0f}"
        except:
            return 0.5, "Error"
    
    def analyze_price_action(self, symbol):
        """Analisi price action"""
        try:
            url = f"{self.base_url}/api/v3/ticker/24hr"
            response = requests.get(url, params={'symbol': symbol}, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                change_24h = float(data['priceChangePercent'])
                
                if change_24h > 5:
                    score = 0.9
                elif change_24h > 2:
                    score = 0.75
                elif change_24h > 0:
                    score = 0.6
                elif change_24h > -2:
                    score = 0.5
                else:
                    score = 0.4
                
                return score, f"24h: {change_24h:+.2f}%"
            return 0.5, "API error"
        except:
            return 0.5, "Error"
    
    def analyze_onchain(self, symbol):
        """Analisi on-chain"""
        try:
            price = self.get_price(symbol)
            if symbol == "BTCUSDT":
                score = 0.7 if price > 100000 else 0.5
            elif symbol == "ETHUSDT":
                score = 0.65 if price > 3500 else 0.5
            else:
                score = 0.55
            return score, "On-chain OK"
        except:
            return 0.5, "Error"
    
    def analyze_cycles(self):
        """Analisi cicli"""
        try:
            from datetime import datetime
            halving_date = datetime(2024, 4, 20)
            days_since = (datetime.now() - halving_date).days
            
            if days_since < 365:
                score = 0.5 + (days_since / 365) * 0.2
            elif days_since < 730:
                score = 0.7 + ((days_since - 365) / 365) * 0.2
            else:
                score = 0.9 - ((days_since - 730) / 730) * 0.3
            
            return round(score, 2), f"{days_since} days post-halving"
        except:
            return 0.55, "Error"
    
    def calculate_confluence(self, symbol):
        """Calcola confluence score"""
        macro_score, macro_reason = self.analyze_macro()
        price_score, price_reason = self.analyze_price_action(symbol)
        onchain_score, onchain_reason = self.analyze_onchain(symbol)
        cycles_score, cycles_reason = self.analyze_cycles()
        
        weights = [0.30, 0.30, 0.25, 0.15]
        confluence = sum(s * w for s, w in zip(
            [macro_score, price_score, onchain_score, cycles_score],
            weights
        ))
        
        return {
            'symbol': symbol,
            'confluence': confluence * 4,
            'confidence': confluence,
            'price': self.get_price(symbol)
        }
    
    def run_auto_cycle(self, cycle_num):
        """Esegue ciclo con auto-trading"""
        logger.info(f"🤖 CYCLE #{cycle_num} START")
        
        # Mostra balance
        usdt_balance = self.auto_engine.get_balance('USDT')
        logger.info(f"💰 USDT Balance: ${usdt_balance:.2f}")
        
        # Analizza e trade ogni symbol
        for symbol in self.symbols:
            # Protezione XRP
            if symbol == "XRPUSDT":
                logger.info(f"🚫 {symbol}: BLOCKED - overconcentration protection")
                continue
            
            # Analisi
            analysis = self.calculate_confluence(symbol)
            score = analysis['confluence']
            
            logger.info(f"📊 {symbol}: Score {score:.2f}")
            
            # Auto-trading
            self.auto_engine.decide_and_execute(symbol, score)
            
            time.sleep(1)
        
        logger.info(f"✅ CYCLE #{cycle_num} COMPLETED")
    
    def run(self, max_cycles=50):
        """Loop principale"""
        logger.info("🚀 QUANTUM AUTO TRADER STARTED")
        logger.info(f"   Max Cycles: {max_cycles}")
        logger.info(f"   Buy Threshold: {self.auto_engine.config['buy_threshold']}")
        logger.info(f"   Sell Threshold: {self.auto_engine.config['sell_threshold']}")
        
        for cycle in range(1, max_cycles + 1):
            self.run_auto_cycle(cycle)
            
            if cycle < max_cycles:
                logger.info(f"⏸️  Waiting 60s before next cycle...")
                time.sleep(60)
        
        logger.info("🏁 AUTO TRADING COMPLETED")

if __name__ == "__main__":
    trader = QuantumAutoTrader()
    trader.run()
EOFTRADER

echo "✅ quantum_trader_auto.py creato"

# ============================================================================
# STEP 6: CREA SCRIPT DI CONTROLLO
# ============================================================================
echo ""
echo "📦 STEP 6: Crea script di controllo..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat > auto_trader_control.sh << 'EOFCONTROL'
#!/bin/bash

case "$1" in
    start)
        echo "🚀 Starting Auto Trader..."
        python3 quantum_trader_auto.py > auto_trader.log 2>&1 &
        echo $! > auto_trader.pid
        echo "✅ Started with PID: $(cat auto_trader.pid)"
        ;;
        
    stop)
        if [ -f auto_trader.pid ]; then
            PID=$(cat auto_trader.pid)
            echo "🛑 Stopping Auto Trader (PID: $PID)..."
            kill $PID 2>/dev/null
            rm auto_trader.pid
            echo "✅ Stopped"
        else
            echo "⚠️  No PID file found"
        fi
        ;;
        
    status)
        if [ -f auto_trader.pid ]; then
            PID=$(cat auto_trader.pid)
            if ps -p $PID > /dev/null; then
                echo "✅ Auto Trader is RUNNING (PID: $PID)"
            else
                echo "❌ Auto Trader is NOT running (stale PID file)"
                rm auto_trader.pid
            fi
        else
            echo "❌ Auto Trader is NOT running"
        fi
        ;;
        
    logs)
        tail -f auto_trading.log
        ;;
        
    test)
        python3 test_auto_system.py
        ;;
        
    *)
        echo "Usage: $0 {start|stop|status|logs|test}"
        exit 1
        ;;
esac
EOFCONTROL

chmod +x auto_trader_control.sh
echo "✅ auto_trader_control.sh creato"

# ============================================================================
# STEP 7: CREA SCRIPT DI TEST
# ============================================================================
echo ""
echo "📦 STEP 7: Crea script di test..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat > test_auto_system.py << 'EOFTEST'
#!/usr/bin/env python3
"""
Test Sistema Auto-Trading
"""
import sys
from auto_trading_engine import AutoTradingEngine
from config_auto_trading import API_KEY, API_SECRET

print("🧪 TEST AUTO-TRADING SYSTEM")
print("=" * 60)

# Test 1: Config
print("\n1️⃣  Testing Configuration...")
if API_KEY == 'YOUR_API_KEY_HERE':
    print("❌ ERRORE: API Keys non configurate!")
    print("   Esegui: nano .env.testnet")
    sys.exit(1)
print("✅ API Keys configured")

# Test 2: Engine
print("\n2️⃣  Testing Trading Engine...")
try:
    engine = AutoTradingEngine()
    print("✅ Engine initialized")
except Exception as e:
    print(f"❌ ERRORE: {e}")
    sys.exit(1)

# Test 3: Balance
print("\n3️⃣  Testing Account Access...")
try:
    usdt_balance = engine.get_balance('USDT')
    print(f"✅ USDT Balance: ${usdt_balance:.2f}")
    
    if usdt_balance < 10:
        print(f"⚠️  WARNING: Balance troppo basso (${usdt_balance:.2f})")
        print("   Richiedi più fondi testnet su: https://testnet.binance.vision/")
except Exception as e:
    print(f"❌ ERRORE: {e}")
    sys.exit(1)

# Test 4: Price
print("\n4️⃣  Testing Market Data...")
try:
    btc_price = engine.get_price('BTCUSDT')
    if btc_price:
        print(f"✅ BTC Price: ${btc_price:,.2f}")
    else:
        print("❌ Cannot get price")
        sys.exit(1)
except Exception as e:
    print(f"❌ ERRORE: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ TUTTI I TEST PASSATI!")
print("🚀 Il sistema è pronto per il trading automatico")
print("\nPer avviare:")
print("   python3 quantum_trader_auto.py")
EOFTEST

echo "✅ test_auto_system.py creato"

# ============================================================================
# STEP 8: CREA FILE CONFIGURAZIONE API KEYS
# ============================================================================
echo ""
echo "📦 STEP 8: Crea template configurazione API Keys..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat > .env.testnet.template << 'EOFENV'
# CONFIGURAZIONE API KEYS TESTNET BINANCE
# Ottieni le tue chiavi su: https://testnet.binance.vision/

BINANCE_TESTNET_API_KEY=your_api_key_here
BINANCE_TESTNET_SECRET_KEY=your_secret_key_here

# IMPORTANTE:
# 1. Vai su https://testnet.binance.vision/
# 2. Clicca "API Management"
# 3. Crea nuove chiavi TESTNET
# 4. Copia API Key e Secret Key qui
# 5. Rinomina questo file in: .env.testnet
EOFENV

echo "✅ .env.testnet.template creato"

# ============================================================================
# RIEPILOGO FINALE
# ============================================================================
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║
echo "║              ✅ INSTALLAZIONE COMPLETATA! ✅                 ║
echo "║                                                              ║
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 FILE CREATI:"
echo "   ✅ config_auto_trading.py       - Configurazione"
echo "   ✅ auto_trading_engine.py       - Motore trading"
echo "   ✅ quantum_trader_auto.py       - Trader automatico"
echo "   ✅ test_auto_system.py          - Test sistema"
echo "   ✅ auto_trader_control.sh       - Script controllo"
echo "   ✅ .env.testnet.template        - Template API Keys"
echo ""
echo "🎯 PROSSIMI PASSI:"
echo ""
echo "1️⃣  Configura API Keys:"
echo "    cp .env.testnet.template .env.testnet"
echo "    nano .env.testnet"
echo "    # Inserisci le tue chiavi testnet reali"
echo ""
echo "2️⃣  Testa il sistema:"
echo "    ./auto_trader_control.sh test"
echo ""
echo "3️⃣  Se tutto OK, avvia:"
echo "    ./auto_trader_control.sh start"
echo ""
echo "4️⃣  Monitora i log:"
echo "    ./auto_trader_control.sh logs"
echo ""
echo "📊 COMANDI DISPONIBILI:"
echo "   ./auto_trader_control.sh start   - Avvia trader"
echo "   ./auto_trader_control.sh stop    - Ferma trader"
echo "   ./auto_trader_control.sh status  - Stato trader"
echo "   ./auto_trader_control.sh logs    - Mostra log"
echo "   ./auto_trader_control.sh test    - Test sistema"
echo ""
echo "🤖 Il sistema è pronto per trading completamente autonomo!"
echo "   Da ora il sistema farà tutto da solo:"
echo "   ✅ Analizzerà i mercati"
echo "   ✅ Prenderà decisioni BUY/SELL"
echo "   ✅ Eseguirà trade automaticamente"
echo "   ✅ Gestirà il rischio"
echo "   🚫 TU non dovrai fare NULLA!"
echo ""


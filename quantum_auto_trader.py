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

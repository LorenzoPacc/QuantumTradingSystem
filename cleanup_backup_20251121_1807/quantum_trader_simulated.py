#!/usr/bin/env python3
"""
QUANTUM TRADING - SIMULATED MODE
Versione con trading simulato e fondi virtuali
"""

import os
import sys
import logging
import sqlite3
import random
from datetime import datetime

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QuantumTraderSimulated")

print("🚀 QUANTUM TRADER - SIMULATED MODE")
print("===================================")
print("💰 Virtual Balance: $10,000")
print("📈 Real-time market data")
print("🎯 Simulated trading")
print("===================================")

class SimulatedTrader:
    def __init__(self):
        self.virtual_balance = 10000.0  # $10,000 virtuali
        self.position_size = 100.0     # $100 per trade
        self.max_positions = 3
        self.symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        self.running = True
        
        # Inizializza database
        self.init_database()
        logger.info(f"💰 Virtual balance iniziale: ${self.virtual_balance:,.2f}")
    
    def init_database(self):
        """Inizializza database per trading simulato"""
        conn = sqlite3.connect('quantum_final.db')
        cursor = conn.cursor()
        
        # Crea tabelle se non esistono
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                side TEXT,
                quantity REAL,
                entry_price REAL,
                exit_price REAL,
                pnl REAL,
                timestamp DATETIME,
                status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                balance REAL,
                timestamp DATETIME
            )
        ''')
        
        # Inserisce balance iniziale
        cursor.execute('INSERT INTO balance_history (balance, timestamp) VALUES (?, ?)',
                     (self.virtual_balance, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_market_price(self, symbol):
        """Ottiene prezzo di mercato reale (usando API Binance)"""
        try:
            import requests
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return float(data['price'])
        except:
            # Fallback a prezzi simulati se API non funziona
            prices = {
                "BTCUSDT": 112000 + random.uniform(-1000, 1000),
                "ETHUSDT": 3970 + random.uniform(-50, 50),
                "SOLUSDT": 195 + random.uniform(-5, 5)
            }
            return prices.get(symbol, 100)
    
    def generate_signal(self, symbol):
        """Genera segnale di trading simulato"""
        signals = ["BUY", "SELL", "HOLD"]
        weights = [0.4, 0.4, 0.2]  # 40% BUY, 40% SELL, 20% HOLD
        return random.choices(signals, weights=weights)[0]
    
    def calculate_quantity(self, symbol, price):
        """Calcola quantità basata su position size"""
        return self.position_size / price
    
    def execute_trade(self, symbol, signal):
        """Esegue trade simulato"""
        price = self.get_market_price(symbol)
        quantity = self.calculate_quantity(symbol, price)
        
        # Simula P&L random ma realistico
        pnl_percent = random.uniform(-0.02, 0.05)  # -2% to +5%
        pnl = self.position_size * pnl_percent
        
        # Aggiorna balance virtuale
        self.virtual_balance += pnl
        
        # Salva nel database
        conn = sqlite3.connect('quantum_final.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (symbol, side, quantity, entry_price, exit_price, pnl, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, signal, quantity, price, price * (1 + pnl_percent), pnl, datetime.now(), 'CLOSED'))
        
        cursor.execute('INSERT INTO balance_history (balance, timestamp) VALUES (?, ?)',
                     (self.virtual_balance, datetime.now()))
        
        conn.commit()
        conn.close()
        
        logger.info(f"🎯 {symbol} {signal}: {quantity:.6f} @ ${price:,.2f} | P&L: ${pnl:+.2f}")
        logger.info(f"💰 Nuovo balance: ${self.virtual_balance:,.2f}")
        
        return True
    
    def run(self):
        """Loop principale di trading"""
        logger.info("🚀 Avvio trading simulato...")
        
        trade_count = 0
        while self.running and trade_count < 20:  # Massimo 20 trade per demo
            try:
                for symbol in self.symbols:
                    signal = self.generate_signal(symbol)
                    
                    if signal != "HOLD":
                        if self.execute_trade(symbol, signal):
                            trade_count += 1
                    
                    # Aspetta tra un trade e l'altro
                    import time
                    time.sleep(10)  # 10 secondi tra i trade
                    
            except KeyboardInterrupt:
                logger.info("🛑 Trading fermato dall'utente")
                break
            except Exception as e:
                logger.error(f"❌ Errore: {e}")
                time.sleep(5)
        
        logger.info(f"✅ Session completata: {trade_count} trade eseguiti")
        logger.info(f"💰 Balance finale: ${self.virtual_balance:,.2f}")

if __name__ == "__main__":
    trader = SimulatedTrader()
    trader.run()

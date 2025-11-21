#!/usr/bin/env python3
"""
QUANTUM TRADING - SIMULATED MODE FIXED
Versione corretta che gestisce il database esistente
"""

import os
import sys
import logging
import sqlite3
import random
import time
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
        """Inizializza database compatibile con struttura esistente"""
        conn = sqlite3.connect('quantum_final.db')
        cursor = conn.cursor()
        
        # Crea tabelle se non esistono (compatibili con struttura originale)
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
                status TEXT DEFAULT 'CLOSED'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                balance REAL,
                timestamp DATETIME
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS open_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                side TEXT,
                quantity REAL,
                entry_price REAL,
                current_price REAL,
                unrealized_pnl REAL,
                timestamp DATETIME,
                status TEXT DEFAULT 'OPEN'
            )
        ''')
        
        # Verifica se la colonna status esiste in trades, altrimenti la aggiunge
        try:
            cursor.execute("SELECT status FROM trades LIMIT 1")
        except sqlite3.OperationalError:
            logger.info("🔄 Aggiungendo colonna 'status' alla tabella trades...")
            cursor.execute("ALTER TABLE trades ADD COLUMN status TEXT DEFAULT 'CLOSED'")
        
        # Pulisce posizioni aperte precedenti
        cursor.execute("DELETE FROM open_positions")
        
        # Inserisce balance iniziale
        from datetime import datetime
        cursor.execute('INSERT INTO balance_history (balance, timestamp) VALUES (?, ?)',
                     (self.virtual_balance, datetime.now()))
        
        conn.commit()
        conn.close()
        logger.info("✅ Database inizializzato correttamente")
    
    def get_market_price(self, symbol):
        """Ottiene prezzo di mercato reale"""
        try:
            import requests
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                price = float(data['price'])
                logger.info(f"📊 {symbol}: ${price:,.2f}")
                return price
        except Exception as e:
            logger.warning(f"⚠️  API Binance non disponibile, uso prezzi simulati: {e}")
            # Fallback a prezzi simulati
            prices = {
                "BTCUSDT": 112000 + random.uniform(-1000, 1000),
                "ETHUSDT": 3970 + random.uniform(-50, 50),
                "SOLUSDT": 195 + random.uniform(-5, 5)
            }
            return prices.get(symbol, 100)
    
    def generate_signal(self, symbol):
        """Genera segnale di trading simulato con logica migliorata"""
        # Maggiore probabilità di BUY in trend rialzista simulato
        price = self.get_market_price(symbol)
        
        # Simula analisi tecnica base
        signals = ["BUY", "SELL", "HOLD"]
        
        # Logica semplice: se prezzo sopra/sotto una media mobile simulata
        moving_avg = {
            "BTCUSDT": 111500,
            "ETHUSDT": 3950, 
            "SOLUSDT": 194
        }
        
        if price > moving_avg.get(symbol, price):
            weights = [0.6, 0.2, 0.2]  # 60% BUY se sopra media
        else:
            weights = [0.2, 0.6, 0.2]  # 60% SELL se sotto media
            
        signal = random.choices(signals, weights=weights)[0]
        logger.info(f"🔍 {symbol} Signal: {signal} (Price: ${price:,.2f})")
        return signal
    
    def calculate_quantity(self, symbol, price):
        """Calcola quantità basata su position size"""
        quantity = self.position_size / price
        
        # Arrotonda per lot size di Binance
        if symbol == "BTCUSDT":
            quantity = round(quantity, 6)
        elif symbol == "ETHUSDT":
            quantity = round(quantity, 5)
        else:
            quantity = round(quantity, 3)
            
        return quantity
    
    def execute_trade(self, symbol, signal):
        """Esegue trade simulato"""
        try:
            price = self.get_market_price(symbol)
            quantity = self.calculate_quantity(symbol, price)
            
            # Simula P&L più realistico (meno estremo)
            if signal == "BUY":
                pnl_percent = random.uniform(-0.01, 0.03)  # -1% to +3% per BUY
            else:  # SELL
                pnl_percent = random.uniform(-0.015, 0.025)  # -1.5% to +2.5% per SELL
                
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
            
            # Log colorato in base al P&L
            if pnl > 0:
                pnl_str = f"🟢 +${pnl:+.2f}"
            else:
                pnl_str = f"🔴 ${pnl:+.2f}"
                
            logger.info(f"🎯 {symbol} {signal}: {quantity:.6f} @ ${price:,.2f} | P&L: {pnl_str}")
            logger.info(f"💰 Nuovo balance: ${self.virtual_balance:,.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore durante execute_trade: {e}")
            return False
    
    def run(self):
        """Loop principale di trading"""
        logger.info("🚀 Avvio trading simulato...")
        
        trade_count = 0
        max_trades = 10  # Massimo 10 trade per demo
        
        while self.running and trade_count < max_trades:
            try:
                for symbol in self.symbols:
                    signal = self.generate_signal(symbol)
                    
                    if signal != "HOLD":
                        logger.info(f"🎯 Tentativo trade {trade_count + 1}/{max_trades}")
                        if self.execute_trade(symbol, signal):
                            trade_count += 1
                            logger.info(f"📈 Progresso: {trade_count}/{max_trades} trade completati")
                    
                    # Aspetta tra un trade e l'altro
                    if trade_count < max_trades:
                        wait_time = random.randint(5, 15)  # 5-15 secondi tra i trade
                        logger.info(f"⏳ Prossimo trade tra {wait_time} secondi...")
                        time.sleep(wait_time)
                    
                if trade_count >= max_trades:
                    break
                    
            except KeyboardInterrupt:
                logger.info("🛑 Trading fermato dall'utente")
                break
            except Exception as e:
                logger.error(f"❌ Errore nel loop principale: {e}")
                time.sleep(5)
        
        logger.info(f"✅ Session completata: {trade_count} trade eseguiti")
        logger.info(f"💰 Balance finale: ${self.virtual_balance:,.2f}")
        
        # Statistiche finali
        if trade_count > 0:
            conn = sqlite3.connect('quantum_final.db')
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(pnl) FROM trades WHERE timestamp > datetime('now', '-1 hour')")
            total_pnl = cursor.fetchone()[0] or 0
            conn.close()
            
            logger.info(f"📊 P&L Totale: ${total_pnl:+.2f}")
            logger.info(f"📈 Performance: {(total_pnl/10000)*100:+.2f}%")

if __name__ == "__main__":
    try:
        trader = SimulatedTrader()
        trader.run()
    except KeyboardInterrupt:
        print("\n🛑 Programma terminato dall'utente")
    except Exception as e:
        logger.error(f"❌ Errore critico: {e}")
        import traceback
        traceback.print_exc()

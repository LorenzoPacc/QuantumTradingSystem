import logging
import time
import sqlite3
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import random
import warnings
warnings.filterwarnings('ignore')

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QuantumTraderUltimateFixed:
    def __init__(self, initial_capital=1000):
        self.cash_balance = initial_capital
        self.portfolio = {}
        self.cycle_count = 0
        self.cycle_delay = 600  # 10 minuti
        self.trade_logger = TradeLogger()
        logging.info("🚀 QUANTUM TRADER ULTIMATE FIXED - SENZA BUG DECIMAL")
    
    def get_portfolio_value(self):
        total = self.cash_balance
        for symbol, position in self.portfolio.items():
            current_price = self.market_data.get_real_price(symbol)
            if current_price:
                total += position['quantity'] * current_price
        return total
    
    def check_and_execute_exits(self):
        """🚨 CONTROLLA E VENDE AUTOMATICAMENTE PER STOP LOSS E TAKE PROFIT"""
        try:
            if not hasattr(self, 'portfolio') or not self.portfolio:
                return False
                
            for symbol, position in list(self.portfolio.items()):
                current_price = self.market_data.get_real_price(symbol)
                if not current_price:
                    continue
                
                entry_price = position['entry_price']
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
                
                # 🚨 STOP LOSS -4%
                if pnl_pct <= -4.0:
                    print(f"🔴 STOP LOSS ATTIVATO: {symbol} ({pnl_pct:.2f}%) - VENDO!")
                    # Simula vendita
                    if symbol in self.portfolio:
                        quantity = self.portfolio[symbol]['quantity']
                        sale_value = quantity * current_price
                        del self.portfolio[symbol]
                        self.cash_balance += sale_value
                        print(f"✅ Venduto {quantity:.6f} {symbol} a ${current_price:.2f}")
                        print(f"💰 Incassato: ${sale_value:.2f}")
                        return True
                
                # 🟢 TAKE PROFIT +8%
                elif pnl_pct >= 8.0:
                    print(f"🟢 TAKE PROFIT ATTIVATO: {symbol} ({pnl_pct:.2f}%) - VENDO!")
                    if symbol in self.portfolio:
                        quantity = self.portfolio[symbol]['quantity']
                        sale_value = quantity * current_price
                        del self.portfolio[symbol]
                        self.cash_balance += sale_value
                        print(f"✅ Venduto {quantity:.6f} {symbol} a ${current_price:.2f}")
                        print(f"💰 Incassato: ${sale_value:.2f}")
                        return True
                        
        except Exception as e:
            print(f"❌ Errore in check_and_execute_exits: {e}")
        
        return False

    def execute_trading_cycle(self):
        """Esegue un ciclo completo di trading"""
        self.cycle_count += 1
        
        # 🎯 CONTROLLA STOP LOSS PRIMA DI ACQUISTARE
        self.check_and_execute_exits()
        
        portfolio_value = self.get_portfolio_value()
        
        print("")
        print("=" * 80)
        print(f"🧠 CICLO {self.cycle_count} - QUANTUM ULTIMATE FIXED")
        print("=" * 80)
        
        # Simula Fear & Greed Index
        fgi = 22  # Extreme Fear
        print(f"😨 FEAR & GREED: {fgi} | 💰 Portfolio: ${portfolio_value:.2f}")
        print("")
        
        # Simula analisi acquisti (semplificata)
        print("💰 ANALISI ACQUISTI:")
        symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT', 'LINKUSDT', 'DOTUSDT']
        
        for symbol in symbols:
            score = 0.95  # High score in Extreme Fear
            if score > 0.8 and self.cash_balance > 10:
                amount = min(self.cash_balance * 0.15, 45)
                print(f"   📊 {symbol}: Score {score:.3f} -> 🤖 ACQUISTO: ${amount:.2f}")
        
        # Report finale
        cash = self.cash_balance
        portfolio_val = self.get_portfolio_value()
        profit = portfolio_val - 200
        profit_pct = (profit / 200) * 100
        positions = len(self.portfolio)
        
        print("")
        print("📊 QUANTUM FIXED REPORT:")
        print(f"   💰 Cash: ${cash:.2f}")
        print(f"   📦 Portfolio: ${portfolio_val:.2f}")
        print(f"   💎 TOTALE: ${portfolio_val:.2f} (+{profit:.2f} / +{profit_pct:.1f}%)")
        print(f"   🤖 Acquisti eseguiti: 0")
        print(f"   🎯 Posizioni attive: {positions}")
        print(f"   ⏳ Prossimo ciclo in {self.cycle_delay}s...")

    def run_continuous_trading(self, cycles=1000, delay=600):
        """Esegue trading continuo"""
        self.cycle_delay = delay
        print("")
        print("=" * 80)
        print("🚀 QUANTUM ULTIMATE FIXED - SENZA BUG DECIMAL")
        print(f"🎯 STRATEGIA: Extreme Fear Aggressive")
        print(f"⏰ Intervallo cicli: {delay} secondi")
        print("=" * 80)
        print("")
        
        for _ in range(cycles):
            self.execute_trading_cycle()
            time.sleep(delay)

class TradeLogger:
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect('trading_performance.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT, action TEXT, quantity REAL,
                entry_price REAL, exit_price REAL, pnl_percent REAL,
                reason TEXT, amount REAL
            )
        ''')
        conn.commit()
        conn.close()

class MockMarketData:
    def get_real_price(self, symbol):
        prices = {
            'BTCUSDT': 101600 + random.randint(-1000, 1000),
            'ETHUSDT': 3380 + random.randint(-50, 50),
            'SOLUSDT': 157 + random.randint(-5, 5),
            'AVAXUSDT': 17.2 + random.uniform(-1, 1),
            'LINKUSDT': 15.3 + random.uniform(-0.5, 0.5),
            'DOTUSDT': 3.17 + random.uniform(-0.1, 0.1)
        }
        return prices.get(symbol, 100)

# Aggiungi market_data al trader
QuantumTraderUltimateFixed.market_data = MockMarketData()

print("✅ QUANTUM TRADER CLEAN - READY!")

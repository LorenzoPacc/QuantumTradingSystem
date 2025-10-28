#!/usr/bin/env python3
"""
QUANTUM TRADER - VERSIONE ENHANCED COMPLETA
Anti-overconcentration + Diversificazione
"""
import requests
import logging
import time
import sqlite3
import os
from datetime import datetime, timedelta
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("QuantumEnhanced")

class EnhancedDB:
    def __init__(self):
        self.db_name = 'quantum_enhanced.db'
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                side TEXT,
                quantity REAL,
                entry_price REAL,
                confluence_score REAL,
                confidence REAL,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_balance REAL,
                available_balance REAL,
                portfolio_value REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS confluence_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                confluence_score REAL,
                confidence REAL,
                signal TEXT,
                factors_json TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database enhanced inizializzato")
    
    def log_trade(self, symbol, side, quantity, price, confluence, confidence, status):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trades (symbol, side, quantity, entry_price, confluence_score, confidence, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, side, quantity, price, confluence, confidence, status))
        conn.commit()
        conn.close()
    
    def log_balance(self, total, available, portfolio_value=0):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO balance_history (total_balance, available_balance, portfolio_value)
            VALUES (?, ?, ?)
        ''', (total, available, portfolio_value))
        conn.commit()
        conn.close()
    
    def log_confluence(self, symbol, confluence, confidence, signal, factors):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO confluence_logs (symbol, confluence_score, confidence, signal, factors_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (symbol, confluence, confidence, signal, str(factors)))
        conn.commit()
        conn.close()

db = EnhancedDB()

class EnhancedTrader:
    def __init__(self):
        self.base_url = "https://api.binance.com"
        
        self.symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT"]
        
        self.min_confluence = 2.6
        self.min_confidence = 0.70
        self.max_risk_per_trade = 0.07
        
        self.virtual_balance = 10000.0
        self.available_balance = 10000.0
        self.portfolio = {}
        self.trade_count = 0
        
        logger.info(f"\n{'#'*80}")
        logger.info(f"🚀 QUANTUM ENHANCED TRADER - ANTI-OVERCONCENTRATION")
        logger.info(f"{'#'*80}")
        logger.info(f"💰 BALANCE: ${self.virtual_balance:,.2f}")
        logger.info(f"🎯 LIMITI: Max 10% per asset • Max 30% portfolio")
        logger.info(f"⚙️  Risk: {self.max_risk_per_trade:.1%} per trade")
        logger.info(f"{'#'*80}\n")

    def get_real_price(self, symbol: str) -> float:
        try:
            url = f"{self.base_url}/api/v3/ticker/price"
            params = {'symbol': symbol}
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                return float(response.json()['price'])
            return 0.0
        except:
            return 0.0

    def get_real_klines(self, symbol: str, interval: str = "1h", limit: int = 100):
        try:
            url = f"{self.base_url}/api/v3/klines"
            params = {'symbol': symbol, 'interval': interval, 'limit': limit}
            response = requests.get(url, params=params, timeout=10)
            return response.json() if response.status_code == 200 else []
        except:
            return []

    def analyze_macro(self) -> tuple:
        try:
            btc_price = self.get_real_price("BTCUSDT")
            if btc_price == 0:
                return 0.5, "Dati non disponibili"
            
            if btc_price > 110000:
                score = 0.90
            elif btc_price > 100000:
                score = 0.80
            elif btc_price > 80000:
                score = 0.70
            elif btc_price > 60000:
                score = 0.60
            elif btc_price > 50000:
                score = 0.50
            else:
                score = 0.40
            
            reason = f"BTC ${btc_price:,.0f}"
            return score, reason
            
        except Exception as e:
            logger.error(f"❌ Errore analyze_macro: {e}")
            return 0.5, "Errore analisi macro"

    def analyze_price_action(self, symbol: str) -> tuple:
        try:
            klines = self.get_real_klines(symbol, "1h", 50)
            if not klines or len(klines) < 20:
                return 0.5, "Dati insufficienti"
            
            closes = np.array([float(k[4]) for k in klines])
            highs = np.array([float(k[2]) for k in klines])
            lows = np.array([float(k[3]) for k in klines])
            volumes = np.array([float(k[5]) for k in klines])
            
            typical_prices = (highs + lows + closes) / 3
            vwap = np.sum(typical_prices * volumes) / np.sum(volumes)
            current_price = closes[-1]
            price_vs_vwap = (current_price - vwap) / vwap
            
            vwap_score = 0.5 + (price_vs_vwap * 2)
            final_score = max(0.1, min(0.95, vwap_score))
            
            reason = f"Price ${current_price:.2f} vs VWAP ${vwap:.2f} ({price_vs_vwap*100:+.1f}%)"
            return final_score, reason
            
        except Exception as e:
            logger.error(f"❌ Errore analyze_price_action: {e}")
            return 0.5, "Errore price action"

    def analyze_onchain(self, symbol: str) -> tuple:
        try:
            klines = self.get_real_klines(symbol, "1d", 30)
            if not klines or len(klines) < 10:
                return 0.5, "Dati insufficienti"
            
            closes = np.array([float(k[4]) for k in klines])
            volumes = np.array([float(k[5]) for k in klines])
            
            obv = 0
            for i in range(1, len(closes)):
                if closes[i] > closes[i-1]:
                    obv += volumes[i]
                elif closes[i] < closes[i-1]:
                    obv -= volumes[i]
            
            obv_trend = obv / np.sum(volumes) if np.sum(volumes) > 0 else 0
            obv_score = 0.5 + (obv_trend * 2)
            final_score = max(0.1, min(0.95, obv_score))
            
            reason = f"OBV trend: {obv_trend:.3f}"
            return final_score, reason
            
        except Exception as e:
            logger.error(f"❌ Errore analyze_onchain: {e}")
            return 0.5, "Errore on-chain"

    def analyze_cycles(self) -> tuple:
        try:
            last_halving = datetime(2024, 4, 20)
            days_since_halving = (datetime.now() - last_halving).days
            
            if days_since_halving < 180:
                score = 0.88
            elif days_since_halving < 365:
                score = 0.78
            elif days_since_halving < 550:
                score = 0.68
            elif days_since_halving < 730:
                score = 0.55
            else:
                score = 0.45
            
            reason = f"{days_since_halving} giorni post-halving"
            return score, reason
            
        except Exception as e:
            logger.error(f"❌ Errore analyze_cycles: {e}")
            return 0.5, "Errore cycles"

    def should_avoid_overconcentration(self, symbol: str, analysis: dict) -> bool:
        """Evita di over-investire sullo stesso symbol"""
        try:
            # Se già abbiamo position in questo symbol
            if symbol in self.portfolio:
                current_position = self.portfolio[symbol] * analysis['price']
                position_percent = current_position / self.virtual_balance
                
                # MAX 10% per singolo asset
                if position_percent > 0.10:
                    logger.warning(f"🚫 OVER-CONCENTRATION: {symbol} già al {position_percent:.1%} > 10% - SKIP")
                    return False
                
                # Se confluence non è MOLTO alta (>3.3), evita di aggiungere
                if analysis['confluence'] < 3.3 and position_percent > 0.05:
                    logger.info(f"ℹ️  Position esistente {symbol} al {position_percent:.1%} - Solo confluence > 3.3")
                    return False
            
            # Controlla diversificazione generale - MAX 30% portfolio
            total_invested = sum(qty * self.get_real_price(sym) for sym, qty in self.portfolio.items())
            portfolio_percent = total_invested / self.virtual_balance
            
            if portfolio_percent > 0.30:
                logger.warning(f"🚫 PORTFOLIO FULL: Già investito {portfolio_percent:.1%} > 30% - SKIP")
                return False
                
            # Se portfolio già >20% invested, richiedi confluence più alta
            if portfolio_percent > 0.20 and analysis['confluence'] < 3.1:
                logger.info(f"ℹ️  Portfolio già al {portfolio_percent:.1%} - Richiesta confluence > 3.1")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore controllo overconcentration: {e}")
            return True

    def calculate_confluence(self, symbol: str) -> dict:
        logger.info(f"\n{'='*80}")
        logger.info(f"🎯 ANALISI CONFLUENCE: {symbol}")
        logger.info(f"{'='*80}")
        
        macro_score, macro_reason = self.analyze_macro()
        price_score, price_reason = self.analyze_price_action(symbol)
        onchain_score, onchain_reason = self.analyze_onchain(symbol)
        cycles_score, cycles_reason = self.analyze_cycles()
        
        weights = {'macro': 0.30, 'price_action': 0.30, 'onchain': 0.25, 'cycles': 0.15}
        
        confluence = (
            macro_score * weights['macro'] +
            price_score * weights['price_action'] +
            onchain_score * weights['onchain'] +
            cycles_score * weights['cycles']
        )
        
        confluence_scaled = confluence * 4
        
        if confluence_scaled >= self.min_confluence and confluence >= self.min_confidence:
            if confluence >= 0.75:
                signal = "BUY"
            elif confluence <= 0.35:
                signal = "SELL"
            else:
                signal = "HOLD"
        else:
            signal = "HOLD"
        
        result = {
            'symbol': symbol,
            'confluence': confluence_scaled,
            'confidence': confluence,
            'signal': signal,
            'price': self.get_real_price(symbol),
            'factors': {
                'macro': macro_score,
                'price': price_score,
                'onchain': onchain_score,
                'cycles': cycles_score
            }
        }
        
        logger.info(f"📊 RISULTATO: Score {confluence_scaled:.2f}/4.0 - Confidence {confluence:.2%} - Signal: {signal}")
        
        db.log_confluence(symbol, confluence_scaled, confluence, signal, result['factors'])
        
        return result

    def calculate_position_size(self, symbol: str, price: float) -> float:
        position_usd = self.available_balance * self.max_risk_per_trade
        
        # Limite per diversificazione
        if symbol in self.portfolio:
            current_value = self.portfolio[symbol] * price
            max_additional = self.virtual_balance * 0.10 - current_value
            position_usd = min(position_usd, max(10, max_additional))
        
        position_usd = max(10.0, min(position_usd, self.available_balance * 0.9))
        
        quantity = position_usd / price
        
        if "BTC" in symbol:
            quantity = round(quantity, 6)
        elif "ETH" in symbol:
            quantity = round(quantity, 5)
        else:
            quantity = round(quantity, 3)
        
        logger.info(f"📏 POSITION SIZE: ${position_usd:.2f} = {quantity} {symbol}")
        return quantity

    def execute_virtual_trade(self, symbol: str, side: str, quantity: float, price: float, confluence: float, confidence: float):
        cost = quantity * price
        
        if side == "BUY":
            if cost > self.available_balance:
                logger.warning(f"⚠️  Fondi insufficienti: ${cost:.2f} > ${self.available_balance:.2f}")
                return False
            
            self.available_balance -= cost
            self.portfolio[symbol] = self.portfolio.get(symbol, 0) + quantity
            self.trade_count += 1
            
            logger.info(f"\n🟢 VIRTUAL BUY EXECUTED!")
            logger.info(f"   {quantity} {symbol} @ ${price:.2f}")
            logger.info(f"   💵 Costo: ${cost:.2f}")
            logger.info(f"   💰 Nuovo Balance: ${self.available_balance:.2f}")
            
        db.log_trade(symbol, side, quantity, price, confluence, confidence, 'EXECUTED')
        
        portfolio_value = self.calculate_portfolio_value()
        db.log_balance(self.virtual_balance, self.available_balance, portfolio_value)
        
        return True

    def calculate_portfolio_value(self) -> float:
        total_value = self.available_balance
        for asset, qty in self.portfolio.items():
            price = self.get_real_price(asset)
            if price > 0:
                total_value += qty * price
        return total_value

    def run_trading_cycle(self):
        logger.info(f"\n{'='*80}")
        logger.info(f"🔄 CICLO TRADING - {datetime.now().strftime('%H:%M:%S')}")
        logger.info(f"{'='*80}")
        
        portfolio_value = self.calculate_portfolio_value()
        if self.portfolio:
            logger.info("\n📦 PORTFOLIO ATTUALE:")
            for asset, qty in self.portfolio.items():
                price = self.get_real_price(asset)
                value = qty * price
                logger.info(f"   {asset}: {qty} @ ${price:,.2f} = ${value:.2f}")
        
        logger.info(f"💰 BALANCE: ${self.available_balance:.2f}")
        logger.info(f"📊 VALORE TOTALE: ${portfolio_value:.2f}")
        
        for symbol in self.symbols:
            try:
                analysis = self.calculate_confluence(symbol)
                
                if analysis['signal'] == 'BUY':
                    # 🔥 CONTROLLO ANTI-OVERCONCENTRATION
                    if not self.should_avoid_overconcentration(symbol, analysis):
                        continue  # ⬅️ QUESTO È IL continue CORRETTO
                    
                    price = analysis['price']
                    if price == 0:
                        continue
                    
                    quantity = self.calculate_position_size(symbol, price)
                    
                    logger.info(f"\n🎯 SEGNALE BUY RILEVATO!")
                    logger.info(f"   Symbol: {symbol}")
                    logger.info(f"   Prezzo: ${price:,.2f}")
                    logger.info(f"   Quantità: {quantity}")
                    
                    if self.execute_virtual_trade(symbol, 'BUY', quantity, price, 
                                                analysis['confluence'], analysis['confidence']):
                        logger.info(f"🎉 TRADE COMPLETATO!")
                        return True
                
            except Exception as e:
                logger.error(f"❌ Errore con {symbol}: {e}")
        
        logger.info("\n⏭️  Nessun trade questo ciclo")
        return False

    def run(self):
        cycle_count = 0
        max_cycles = 15
        
        while cycle_count < max_cycles:
            try:
                cycle_count += 1
                logger.info(f"\n📈 CICLO #{cycle_count}/{max_cycles}")
                
                self.run_trading_cycle()
                
                wait_time = 300
                logger.info(f"⏳ Prossimo ciclo tra {wait_time//60} minuti...")
                time.sleep(wait_time)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"💥 ERRORE: {e}")
                time.sleep(60)
        
        logger.info(f"\n🏁 SIMULAZIONE COMPLETATA - {self.trade_count} trade eseguiti")

if __name__ == "__main__":
    trader = EnhancedTrader()
    trader.run()

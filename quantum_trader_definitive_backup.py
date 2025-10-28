#!/usr/bin/env python3
"""
QUANTUM TRADER - VERSIONE DEFINITIVA 2024
✅ Dati REALI Binance API • Balance VIRTUALE 
✅ Strategia Multi-Fattore Confluence Avanzata
✅ Database Completo • Performance Tracking
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
logger = logging.getLogger("QuantumDefinitive")

class AdvancedDB:
    def __init__(self):
        self.db_name = 'quantum_definitive.db'
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_value REAL,
                pnl REAL,
                pnl_percent REAL,
                trade_count INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database avanzato inizializzato")
    
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
    
    def log_performance(self, total_value, pnl, pnl_percent, trade_count):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO performance (total_value, pnl, pnl_percent, trade_count)
            VALUES (?, ?, ?, ?)
        ''', (total_value, pnl, pnl_percent, trade_count))
        conn.commit()
        conn.close()

db = AdvancedDB()

class DefinitiveTrader:
    def __init__(self):
        self.base_url = "https://api.binance.com"
        
        # SYMBOLS ottimizzati per liquidità
        self.symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT"]
        
        # PARAMETRI OTTIMIZZATI CONSERVATIVI
        self.min_confluence = 2.8
        self.min_confidence = 0.75
        self.max_risk_per_trade = 0.05
        
        # Balance virtuale
        self.virtual_balance = 10000.0
        self.available_balance = 10000.0
        self.portfolio = {}
        self.trade_count = 0
        self.initial_balance = 10000.0
        self.start_time = datetime.now()
        
        logger.info(f"\n{'#'*80}")
        logger.info(f"🚀 QUANTUM DEFINITIVE TRADER - DATI REALI BINANCE")
        logger.info(f"{'#'*80}")
        logger.info(f"💰 BALANCE INIZIALE: ${self.virtual_balance:,.2f}")
        logger.info(f"🎯 STRATEGIA: Multi-Fattore Confluence Avanzata")
        logger.info(f"⚙️  PARAMETRI: Confluence ≥{self.min_confluence}/4.0, Confidence ≥{self.min_confidence:.0%}")
        logger.info(f"📈 RISK: {self.max_risk_per_trade:.1%} per trade")
        logger.info(f"🕒 AVVIATO: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'#'*80}\n")

    def get_real_price(self, symbol: str) -> float:
        """Ottieni prezzo REALE da Binance"""
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
        """Candele REALI da Binance"""
        try:
            url = f"{self.base_url}/api/v3/klines"
            params = {'symbol': symbol, 'interval': interval, 'limit': limit}
            response = requests.get(url, params=params, timeout=10)
            return response.json() if response.status_code == 200 else []
        except:
            return []

    def get_price_change_24h(self, symbol: str) -> float:
        """Ottieni variazione prezzo 24h"""
        try:
            url = f"{self.base_url}/api/v3/ticker/24hr"
            params = {'symbol': symbol}
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return float(data.get('priceChangePercent', 0))
            return 0.0
        except:
            return 0.0

    def analyze_macro(self) -> tuple:
        """Analisi Macro MIGLIORATA con correlation"""
        try:
            btc_price = self.get_real_price("BTCUSDT")
            eth_price = self.get_real_price("ETHUSDT")
            
            if btc_price == 0:
                return 0.5, "Dati non disponibili"
            
            # Correlation analysis
            btc_change = self.get_price_change_24h("BTCUSDT")
            eth_change = self.get_price_change_24h("ETHUSDT")
            
            # Price-based analysis
            if btc_price > 110000:
                base_score = 0.90
            elif btc_price > 100000:
                base_score = 0.80
            elif btc_price > 80000:
                base_score = 0.70
            elif btc_price > 60000:
                base_score = 0.60
            elif btc_price > 50000:
                base_score = 0.50
            else:
                base_score = 0.40
            
            # Market correlation bonus
            correlation_bonus = 0
            if btc_change > 0 and eth_change > 0:
                correlation_bonus = 0.05
            elif btc_change < 0 and eth_change < 0:
                correlation_bonus = -0.03
            
            final_score = max(0.1, min(0.95, base_score + correlation_bonus))
            
            reason = f"BTC ${btc_price:,.0f} | 24h: {btc_change:+.1f}% | ETH: {eth_change:+.1f}%"
            return final_score, reason
            
        except Exception as e:
            logger.error(f"❌ Errore analyze_macro: {e}")
            return 0.5, "Errore analisi macro"

    def calculate_rsi(self, prices: np.array, period: int = 14) -> float:
        """Calcola RSI"""
        try:
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gains = np.mean(gains[-period:])
            avg_losses = np.mean(losses[-period:])
            
            if avg_losses == 0:
                return 100.0 if avg_gains > 0 else 50.0
            
            rs = avg_gains / avg_losses
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except:
            return 50.0

    def analyze_price_action(self, symbol: str) -> tuple:
        """Price Action MIGLIORATA - VWAP + RSI + Volume"""
        try:
            klines = self.get_real_klines(symbol, "1h", 50)
            if not klines or len(klines) < 20:
                return 0.5, "Dati insufficienti"
            
            closes = np.array([float(k[4]) for k in klines])
            highs = np.array([float(k[2]) for k in klines])
            lows = np.array([float(k[3]) for k in klines])
            volumes = np.array([float(k[5]) for k in klines])
            
            # VWAP calculation
            typical_prices = (highs + lows + closes) / 3
            vwap = np.sum(typical_prices * volumes) / np.sum(volumes)
            current_price = closes[-1]
            price_vs_vwap = (current_price - vwap) / vwap
            
            # RSI calculation
            rsi = self.calculate_rsi(closes)
            
            # Volume trend
            volume_trend = np.mean(volumes[-5:]) / np.mean(volumes[-20:]) if np.mean(volumes[-20:]) > 0 else 1
            
            # Score composito
            vwap_score = 0.5 + (price_vs_vwap * 2)
            rsi_score = 1 - abs(rsi - 50) / 50
            volume_score = min(1.0, volume_trend * 0.8)
            
            composite_score = (vwap_score * 0.6 + rsi_score * 0.3 + volume_score * 0.1)
            final_score = max(0.1, min(0.95, composite_score))
            
            reason = f"Price ${current_price:.2f} vs VWAP ${vwap:.2f} ({price_vs_vwap*100:+.1f}%) | RSI: {rsi:.1f}"
            return final_score, reason
            
        except Exception as e:
            logger.error(f"❌ Errore analyze_price_action: {e}")
            return 0.5, "Errore price action"

    def analyze_onchain(self, symbol: str) -> tuple:
        """On-Chain MIGLIORATA - OBV + Volume analysis"""
        try:
            klines = self.get_real_klines(symbol, "1d", 30)
            if not klines or len(klines) < 10:
                return 0.5, "Dati insufficienti"
            
            closes = np.array([float(k[4]) for k in klines])
            volumes = np.array([float(k[5]) for k in klines])
            
            # OBV calculation
            obv = 0
            for i in range(1, len(closes)):
                if closes[i] > closes[i-1]:
                    obv += volumes[i]
                elif closes[i] < closes[i-1]:
                    obv -= volumes[i]
            
            obv_trend = obv / np.sum(volumes) if np.sum(volumes) > 0 else 0
            
            # Volume consistency
            volume_std = np.std(volumes[-10:]) / np.mean(volumes[-10:]) if np.mean(volumes[-10:]) > 0 else 1
            volume_stability = max(0, 1 - volume_std)
            
            # Score composito
            obv_score = 0.5 + (obv_trend * 2)
            stability_score = volume_stability * 0.3
            
            final_score = max(0.1, min(0.95, obv_score + stability_score))
            
            reason = f"OBV trend: {obv_trend:.3f} | Volume stability: {volume_stability:.2f}"
            return final_score, reason
            
        except Exception as e:
            logger.error(f"❌ Errore analyze_onchain: {e}")
            return 0.5, "Errore on-chain"

    def analyze_cycles(self) -> tuple:
        """Analisi Cicli - Halving timing"""
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

    def calculate_confluence(self, symbol: str) -> dict:
        """Calcola CONFLUENCE SCORE - Strategia Multi-Fattore"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🎯 ANALISI CONFLUENCE: {symbol}")
        logger.info(f"{'='*80}")
        
        # Esegui analisi
        macro_score, macro_reason = self.analyze_macro()
        price_score, price_reason = self.analyze_price_action(symbol)
        onchain_score, onchain_reason = self.analyze_onchain(symbol)
        cycles_score, cycles_reason = self.analyze_cycles()
        
        # Weighted confluence
        weights = {'macro': 0.30, 'price_action': 0.30, 'onchain': 0.25, 'cycles': 0.15}
        
        confluence = (
            macro_score * weights['macro'] +
            price_score * weights['price_action'] +
            onchain_score * weights['onchain'] +
            cycles_score * weights['cycles']
        )
        
        confluence_scaled = confluence * 4
        
        # Signal determination
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
        
        # Enhanced logging
        logger.info(f"\n📊 RISULTATO CONFLUENCE:")
        logger.info(f"   🎯 Score: {confluence_scaled:.2f}/4.0")
        logger.info(f"   📈 Confidence: {confluence:.2%}")
        logger.info(f"   🔔 Signal: {signal}")
        logger.info(f"\n🔍 FATTORI DETTAGLIATI:")
        logger.info(f"   🌍 Macro ({weights['macro']:.0%}): {macro_score:.2f} - {macro_reason}")
        logger.info(f"   💹 Price ({weights['price_action']:.0%}): {price_score:.2f} - {price_reason}")
        logger.info(f"   ⛓️  On-Chain ({weights['onchain']:.0%}): {onchain_score:.2f} - {onchain_reason}")
        logger.info(f"   🔄 Cycles ({weights['cycles']:.0%}): {cycles_score:.2f} - {cycles_reason}")
        
        # Salva nel database
        db.log_confluence(symbol, confluence_scaled, confluence, signal, result['factors'])
        
        return result

    def calculate_position_size(self, symbol: str, price: float) -> float:
        """Calcola position size sicuro"""
        position_usd = self.available_balance * self.max_risk_per_trade
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
        """Esegue trade VIRTUALE con dati REALI"""
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
            
        else:  # SELL
            if symbol not in self.portfolio or self.portfolio[symbol] < quantity:
                logger.warning(f"⚠️  Quantità insufficiente")
                return False
            
            self.available_balance += cost
            self.portfolio[symbol] -= quantity
            if self.portfolio[symbol] < 0.000001:
                del self.portfolio[symbol]
            self.trade_count += 1
            
            logger.info(f"\n🔴 VIRTUAL SELL EXECUTED!")
            logger.info(f"   {quantity} {symbol} @ ${price:.2f}")
            logger.info(f"   💵 Ricavo: ${cost:.2f}")
            logger.info(f"   💰 Nuovo Balance: ${self.available_balance:.2f}")
        
        # Salva nel database
        db.log_trade(symbol, side, quantity, price, confluence, confidence, 'EXECUTED')
        
        # Calcola portfolio value
        portfolio_value = self.calculate_portfolio_value()
        db.log_balance(self.virtual_balance, self.available_balance, portfolio_value)
        
        return True

    def calculate_portfolio_value(self) -> float:
        """Calcola valore totale portfolio"""
        total_value = self.available_balance
        for asset, qty in self.portfolio.items():
            price = self.get_real_price(asset)
            if price > 0:
                total_value += qty * price
        return total_value

    def run_trading_cycle(self):
        """Ciclo di trading completo"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🔄 CICLO TRADING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*80}")
        
        # Mostra portfolio attuale
        portfolio_value = self.calculate_portfolio_value()
        if self.portfolio:
            logger.info("\n📦 PORTFOLIO ATTUALE:")
            for asset, qty in self.portfolio.items():
                price = self.get_real_price(asset)
                value = qty * price
                logger.info(f"   {asset}: {qty} @ ${price:,.2f} = ${value:.2f}")
        
        logger.info(f"\n💰 BALANCE: ${self.available_balance:.2f}")
        logger.info(f"📊 VALORE TOTALE: ${portfolio_value:.2f}")
        logger.info(f"🎯 TRADE ESEGUITI: {self.trade_count}")
        
        # Analizza symbols
        for symbol in self.symbols:
            try:
                analysis = self.calculate_confluence(symbol)
                
                if analysis['signal'] in ['BUY', 'SELL']:
                    price = analysis['price']
                    if price == 0:
                        logger.warning(f"⚠️  Prezzo non disponibile per {symbol}")
                        continue
                    
                    quantity = self.calculate_position_size(symbol, price)
                    
                    logger.info(f"\n🎯 SEGNALE {analysis['signal']} RILEVATO!")
                    logger.info(f"   Symbol: {symbol}")
                    logger.info(f"   Prezzo REALE: ${price:,.2f}")
                    logger.info(f"   Quantità: {quantity}")
                    logger.info(f"   Valore Trade: ${quantity * price:.2f}")
                    
                    if self.execute_virtual_trade(symbol, analysis['signal'], quantity, price, 
                                                analysis['confluence'], analysis['confidence']):
                        logger.info(f"🎉 TRADE COMPLETATO!")
                        return True
                
            except Exception as e:
                logger.error(f"❌ Errore con {symbol}: {e}")
        
        logger.info("\n⏭️  Nessun trade questo ciclo")
        return False

    def generate_performance_report(self):
        """Genera report performance finale"""
        total_value = self.calculate_portfolio_value()
        pnl = total_value - self.initial_balance
        pnl_percent = (pnl / self.initial_balance) * 100
        runtime = datetime.now() - self.start_time
        
        logger.info(f"\n\n{'#'*80}")
        logger.info(f"🏁 PERFORMANCE REPORT FINALE")
        logger.info(f"{'#'*80}")
        logger.info(f"💰 Balance Iniziale: ${self.initial_balance:,.2f}")
        logger.info(f"💰 Valore Finale: ${total_value:,.2f}")
        logger.info(f"📈 P&L Assoluto: ${pnl:+.2f}")
        logger.info(f"📈 P&L Percentuale: {pnl_percent:+.2f}%")
        logger.info(f"🎯 Trade Eseguiti: {self.trade_count}")
        logger.info(f"⏱️  Runtime: {runtime}")
        
        if self.portfolio:
            logger.info(f"\n📦 PORTFOLIO FINALE:")
            for asset, qty in self.portfolio.items():
                price = self.get_real_price(asset)
                value = qty * price
                logger.info(f"   {asset}: {qty} @ ${price:,.2f} = ${value:.2f}")
        
        # Salva performance nel database
        db.log_performance(total_value, pnl, pnl_percent, self.trade_count)

    def run(self):
        """Loop principale"""
        cycle_count = 0
        max_cycles = 20
        
        try:
            while cycle_count < max_cycles:
                cycle_count += 1
                logger.info(f"\n\n{'#'*80}")
                logger.info(f"📈 CICLO #{cycle_count}/{max_cycles}")
                logger.info(f"{'#'*80}")
                
                self.run_trading_cycle()
                
                wait_time = 300  # 5 minuti
                logger.info(f"\n⏳ Prossimo ciclo tra {wait_time//60} minuti...")
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 TRADER FERMATO DALL'UTENTE")
        except Exception as e:
            logger.error(f"💥 ERRORE CRITICO: {e}")
        finally:
            self.generate_performance_report()

if __name__ == "__main__":
    trader = DefinitiveTrader()
    trader.run()

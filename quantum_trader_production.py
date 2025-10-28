#!/usr/bin/env python3
"""
QUANTUM TRADER - VERSIONE HEARTBEAT
Auto-recovery + monitoring continuo
"""
import requests
import logging
import time
import sqlite3
import os
import sys
from datetime import datetime
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - HEARTBEAT - %(message)s'
)
logger = logging.getLogger("QuantumHeartbeat")

class HeartbeatTrader:
    def __init__(self):
        self.base_url = "https://api.binance.com"
        self.symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT"]
        
        self.min_confluence = 2.6
        self.min_confidence = 0.70
        self.max_risk_per_trade = 0.07
        
        # INIZIALIZZA CON PORTFOLIO ESISTENTE
        self.virtual_balance = 10000.0
        self.available_balance = 9300.0
        self.portfolio = {"XRPUSDT": 260.233 + 241.971 + 259.856}
        self.trade_count = 3
        
        logger.info("🚀 HEARTBEAT TRADER INIZIALIZZATO")
        logger.info(f"💰 Balance: ${self.available_balance:.2f}")
        logger.info(f"📦 Portfolio: {self.portfolio}")

    def heartbeat(self, message):
        """Log heartbeat per tracciare vitalità"""
        logger.info(f"❤️  {message}")

    def safe_sleep(self, seconds):
        """Sleep con heartbeat per evitare crash"""
        chunks = seconds // 30  # Sleep in chunks di 30 secondi
        for i in range(chunks):
            self.heartbeat(f"Sleep... {i+1}/{chunks}")
            time.sleep(30)
        
        remaining = seconds % 30
        if remaining > 0:
            time.sleep(remaining)

    def get_real_price(self, symbol: str) -> float:
        try:
            self.heartbeat(f"Get price {symbol}")
            url = f"{self.base_url}/api/v3/ticker/price"
            params = {'symbol': symbol}
            response = requests.get(url, params=params, timeout=10)
            return float(response.json()['price']) if response.status_code == 200 else 0.0
        except Exception as e:
            logger.error(f"❌ Price error {symbol}: {e}")
            return 0.0

    def analyze_macro(self) -> tuple:
        self.heartbeat("Analisi macro")
        try:
            btc_price = self.get_real_price("BTCUSDT")
            score = 0.87  # Semplicificato per test
            return score, f"BTC ${btc_price:,.0f}"
        except:
            return 0.5, "Errore macro"

    def analyze_price_action(self, symbol: str) -> tuple:
        self.heartbeat(f"Price action {symbol}")
        return 0.6, "Price action test"

    def analyze_onchain(self, symbol: str) -> tuple:
        self.heartbeat(f"On-chain {symbol}")
        return 0.5, "On-chain test"

    def analyze_cycles(self) -> tuple:
        self.heartbeat("Analisi cicli")
        return 0.55, "556 giorni post-halving"

    def calculate_confluence(self, symbol: str) -> dict:
        self.heartbeat(f"Confluence {symbol}")
        
        macro_score, macro_reason = self.analyze_macro()
        price_score, price_reason = self.analyze_price_action(symbol)
        onchain_score, onchain_reason = self.analyze_onchain(symbol)
        cycles_score, cycles_reason = self.analyze_cycles()
        
        weights = [0.30, 0.30, 0.25, 0.15]
        confluence = sum(s * w for s, w in zip([macro_score, price_score, onchain_score, cycles_score], weights))
        
        signal = "HOLD"
        if symbol == "XRPUSDT":
            self.heartbeat("🚫 XRP bloccato - overconcentration")
        
        return {
            'symbol': symbol,
            'confluence': confluence * 4,
            'confidence': confluence,
            'signal': signal,
            'price': self.get_real_price(symbol)
        }

    def run_trading_cycle(self, cycle_num: int):
        """Ciclo di trading con heartbeat"""
        self.heartbeat(f"INIZIO CICLO #{cycle_num}")
        
        try:
            # Portfolio snapshot
            portfolio_value = self.available_balance
            for asset, qty in self.portfolio.items():
                price = self.get_real_price(asset)
                portfolio_value += qty * price
            
            self.heartbeat(f"Portfolio: ${portfolio_value:.2f}")
            
            # Analisi symbols
            for symbol in self.symbols:
                analysis = self.calculate_confluence(symbol)
                self.heartbeat(f"{symbol}: {analysis['signal']} (Score: {analysis['confluence']:.2f})")
            
            self.heartbeat(f"FINE CICLO #{cycle_num}")
            return True
            
        except Exception as e:
            logger.error(f"💥 CICLO #{cycle_num} CRASH: {e}")
            return False

    def run(self):
        """Loop principale con recovery integrata"""
        self.heartbeat("START HEARTBEAT TRADER")
        cycle_count = 0
        max_cycles = 20
        
        while cycle_count < max_cycles:
            try:
                cycle_count += 1
                success = self.run_trading_cycle(cycle_count)
                
                if not success:
                    logger.warning("🔄 Ciclo fallito, ma continuo...")
                
                # ⚠️ SLEEP SICURO con heartbeat
                self.heartbeat(f"Attesa 60s prima del prossimo ciclo... ({cycle_count}/{max_cycles})")
                self.safe_sleep(300)  # Solo 1 minuto per test
                
            except KeyboardInterrupt:
                self.heartbeat("🛑 Fermato dall'utente")
                break
            except Exception as e:
                logger.error(f"💥 ERRORE GLOBALE: {e}")
                self.heartbeat("🔄 Ripristino tra 30s...")
                time.sleep(30)
        
        self.heartbeat("🏁 SIMULAZIONE COMPLETATA")

if __name__ == "__main__":
    trader = HeartbeatTrader()
    trader.run()

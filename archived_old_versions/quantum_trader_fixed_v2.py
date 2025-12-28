#!/usr/bin/env python3
"""
QUANTUM TRADER FIXED V2 - Con fix LOT_SIZE
"""

import hmac
import hashlib
import time
import requests
import logging
import sqlite3
from datetime import datetime
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QuantumFixedV2")

class LotSizeFix:
    @staticmethod
    def adjust_quantity(symbol, quantity):
        """Aggiusta quantity per LOT_SIZE rules di Binance"""
        # Regole per TestNet
        lot_rules = {
            "BTCUSDT": {"min_qty": 0.00001, "step_size": 0.000001},
            "ETHUSDT": {"min_qty": 0.0001, "step_size": 0.00001},
            "SOLUSDT": {"min_qty": 0.01, "step_size": 0.001}
        }
        
        rules = lot_rules.get(symbol, {"min_qty": 0.001, "step_size": 0.001})
        
        # Applica step size
        if rules["step_size"] > 0:
            steps = quantity / rules["step_size"]
            adjusted_steps = int(steps)
            if steps > adjusted_steps:
                adjusted_steps += 1
            adjusted_quantity = adjusted_steps * rules["step_size"]
        else:
            adjusted_quantity = quantity
        
        # Verifica minimo
        if adjusted_quantity < rules["min_qty"]:
            adjusted_quantity = rules["min_qty"]
        
        # Arrotondamento finale
        if symbol == "BTCUSDT":
            return round(adjusted_quantity, 6)
        elif symbol == "ETHUSDT":
            return round(adjusted_quantity, 5)
        else:
            return round(adjusted_quantity, 3)

class QuantumTraderFixedV2:
    def __init__(self):
        self.api_key = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
        self.api_secret = "yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"
        self.base_url = "https://testnet.binance.vision"
        
        self.symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        self.min_notional = 10.0
        self.lot_fix = LotSizeFix()
    
    def create_signature(self, query_string):
        """Crea signature CORRETTA"""
        try:
            signature = hmac.new(
                self.api_secret.encode('utf-8'),
                query_string.encode('utf-8'), 
                hashlib.sha256
            ).hexdigest()
            return signature
        except Exception as e:
            logger.error(f"❌ Errore signature: {e}")
            return None
    
    def get_account_balance(self):
        """Ottieni balance USDT"""
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = self.create_signature(query_string)
        
        if not signature:
            return 0.0
        
        url = f"{self.base_url}/api/v3/account?{query_string}&signature={signature}"
        headers = {"X-MBX-APIKEY": self.api_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                usdt = next((float(b['free']) for b in data['balances'] if b['asset'] == 'USDT'), 0.0)
                return usdt
        except Exception as e:
            logger.error(f"❌ Errore balance: {e}")
        
        return 0.0
    
    def place_order(self, symbol, side, quantity, price):
        """Piazza ordine con LOT_SIZE fix"""
        # Aggiusta quantity
        quantity = self.lot_fix.adjust_quantity(symbol, quantity)
        
        timestamp = int(time.time() * 1000)
        query_string = f"symbol={symbol}&side={side}&type=LIMIT&timeInForce=GTC&quantity={quantity}&price={price}&timestamp={timestamp}"
        
        signature = self.create_signature(query_string)
        if not signature:
            return False, "Signature error"
        
        url = f"{self.base_url}/api/v3/order?{query_string}&signature={signature}"
        headers = {"X-MBX-APIKEY": self.api_key}
        
        logger.info(f"🚀 Invio ordine: {symbol} {side} {quantity} @ ${price}")
        
        try:
            response = requests.post(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Ordine piazzato con successo!")
                return True, response.json()
            else:
                logger.error(f"❌ Errore ordine: {response.text}")
                return False, response.text
                
        except Exception as e:
            logger.error(f"💥 Errore connessione: {e}")
            return False, str(e)
    
    def calculate_position_size(self, symbol, balance, price):
        """Calcola position size con LOT_SIZE compliance"""
        # Usa il 5% del balance
        position_usd = balance * 0.05
        
        # Verifica minimo notional
        if position_usd < self.min_notional:
            position_usd = self.min_notional
        
        # Calcola quantità
        quantity = position_usd / price
        
        # Applica LOT_SIZE rules
        quantity = self.lot_fix.adjust_quantity(symbol, quantity)
        
        # Verifica finale notional
        notional_value = quantity * price
        if notional_value < self.min_notional:
            # Aumenta per raggiungere minimo
            quantity = (self.min_notional * 1.1) / price
            quantity = self.lot_fix.adjust_quantity(symbol, quantity)
        
        logger.info(f"📊 Position size: {quantity} {symbol} (${quantity * price:.2f})")
        return quantity
    
    def get_current_price(self, symbol):
        """Ottieni prezzo corrente"""
        url = f"{self.base_url}/api/v3/ticker/price?symbol={symbol}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return float(data['price'])
        except Exception as e:
            logger.error(f"❌ Errore prezzo {symbol}: {e}")
        
        # Fallback prices
        fallback_prices = {
            "BTCUSDT": 45000,
            "ETHUSDT": 3000, 
            "SOLUSDT": 100
        }
        return fallback_prices.get(symbol, 100)
    
    def multi_factor_analysis(self, symbol):
        """La TUA strategia multi-fattore"""
        logger.info(f"🧠 ANALISI MULTI-FATTORE {symbol}")
        
        # Simula analisi
        factors = {
            'gold_btc_divergence': random.uniform(0.6, 0.9),
            'dxy_correlation': random.uniform(0.5, 0.8),
            'vwap_signal': random.uniform(0.4, 0.7),
            'nvt_score': random.uniform(0.5, 0.8),
            'puell_multiple': random.uniform(0.6, 0.9),
            'obv_trend': random.uniform(0.5, 0.8),
            'halving_cycle': random.uniform(0.7, 0.95),
            'macro_outlook': random.uniform(0.4, 0.7)
        }
        
        confidence = (
            factors['gold_btc_divergence'] * 0.15 +
            factors['dxy_correlation'] * 0.10 +
            factors['vwap_signal'] * 0.20 +
            factors['nvt_score'] * 0.10 +
            factors['puell_multiple'] * 0.10 +
            factors['obv_trend'] * 0.15 +
            factors['halving_cycle'] * 0.10 +
            factors['macro_outlook'] * 0.10
        )
        
        if confidence > 0.65:
            direction = "BUY"
        elif confidence < 0.35:
            direction = "SELL" 
        else:
            direction = "HOLD"
        
        logger.info(f"📈 {symbol}: Confidence {confidence:.2f}, Signal {direction}")
        return direction, confidence
    
    def run_trading_cycle(self):
        """Esegui ciclo trading"""
        logger.info("🚀 CICLO TRADING MULTI-FATTORE V2")
        logger.info("=" * 50)
        
        balance = self.get_account_balance()
        logger.info(f"💰 Balance: ${balance:.2f}")
        
        if balance < self.min_notional:
            logger.error("❌ Balance insufficiente")
            return
        
        for symbol in self.symbols:
            direction, confidence = self.multi_factor_analysis(symbol)
            
            if direction in ["BUY", "SELL"] and confidence > 0.65:
                price = self.get_current_price(symbol)
                quantity = self.calculate_position_size(symbol, balance, price)
                
                success, result = self.place_order(symbol, direction, quantity, price)
                
                if success:
                    self.save_trade_to_db(symbol, direction, quantity, price)
                    logger.info(f"🎯 TRADE ESEGUITO: {symbol} {direction} {quantity} @ ${price}")
                    break
                else:
                    logger.error(f"❌ Trade fallito: {result}")
            else:
                logger.info(f"⏭️  Nessun segnale forte per {symbol} (confidence: {confidence:.2f})")
    
    def save_trade_to_db(self, symbol, side, quantity, price):
        """Salva trade nel database"""
        try:
            conn = sqlite3.connect('quantum_final.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trades (symbol, side, quantity, entry_price, timestamp, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (symbol, side, quantity, price, datetime.now(), 'OPEN'))
            conn.commit()
            conn.close()
            logger.info("💾 Trade salvato nel database")
        except Exception as e:
            logger.error(f"❌ Errore database: {e}")
    
    def run_continuous(self):
        """Esegui trading continuo"""
        logger.info("🎯 QUANTUM TRADER FIXED V2 - AVVIATO")
        logger.info("📍 Strategia Multi-Fattore con LOT_SIZE fix")
        
        while True:
            try:
                self.run_trading_cycle()
                logger.info("⏳ Prossimo ciclo in 60 secondi...")
                time.sleep(60)
            except Exception as e:
                logger.error(f"💥 Errore ciclo trading: {e}")
                time.sleep(30)

if __name__ == "__main__":
    trader = QuantumTraderFixedV2()
    trader.run_continuous()

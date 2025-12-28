#!/usr/bin/env python3
"""
QUANTUM WORKING FINAL - TRADER CHE FUNZIONA
"""

import requests
import hmac
import hashlib
import time
import logging
import sqlite3
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QuantumWorking")

class WorkingTrader:
    def __init__(self):
        self.api_key = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
        self.api_secret = "yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"
        self.position_size = 15.0  # $15 per trade
        self.symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        
    def get_balance(self):
        """Ottieni balance"""
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        url = f"https://testnet.binance.vision/api/v3/account?{query_string}&signature={signature}"
        headers = {"X-MBX-APIKEY": self.api_key}
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            usdt = next((b for b in data['balances'] if b['asset'] == 'USDT'), None)
            return float(usdt['free']) if usdt else 0.0
        return 0.0
    
    def place_order(self, symbol, side, quantity, price):
        """Piazza ordine"""
        timestamp = int(time.time() * 1000)
        query_string = f"symbol={symbol}&side={side}&type=LIMIT&timeInForce=GTC&quantity={quantity}&price={price}&timestamp={timestamp}"
        signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        
        url = f"https://testnet.binance.vision/api/v3/order?{query_string}&signature={signature}"
        headers = {"X-MBX-APIKEY": self.api_key}
        
        logger.info(f"🎯 {side} {symbol}: {quantity} @ ${price:.2f}")
        response = requests.post(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            order_data = response.json()
            logger.info(f"✅ ORDINE RIUSCITO! ID: {order_data['orderId']}")
            
            # Salva nel database
            self.save_trade(symbol, side, quantity, price, order_data['orderId'])
            return True
        else:
            logger.error(f"❌ FALLITO: {response.text}")
            return False
    
    def save_trade(self, symbol, side, quantity, price, order_id):
        """Salva trade nel database"""
        conn = sqlite3.connect('quantum_final.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trades (symbol, side, quantity, entry_price, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (symbol, side, quantity, price, datetime.now(), 'OPEN'))
        conn.commit()
        conn.close()
    
    def run(self):
        """Esegui trading"""
        logger.info("🚀 QUANTUM WORKING TRADER - AVVIATO")
        
        while True:
            try:
                balance = self.get_balance()
                logger.info(f"💰 Balance: ${balance:.2f}")
                
                if balance < self.position_size:
                    logger.warning(f"⛔ Fondi insufficienti: ${balance:.2f} < ${self.position_size}")
                    break
                
                # Prova ordine per ogni symbol
                for symbol in self.symbols:
                    price_url = f"https://testnet.binance.vision/api/v3/ticker/price?symbol={symbol}"
                    price_data = requests.get(price_url).json()
                    price = float(price_data['price'])
                    
                    # Calcola quantità
                    if symbol == "BTCUSDT":
                        quantity = round(self.position_size / price, 6)
                    elif symbol == "ETHUSDT":
                        quantity = round(self.position_size / price, 5)
                    else:
                        quantity = round(self.position_size / price, 3)
                    
                    logger.info(f"🎯 Tentativo: {quantity} {symbol} @ ${price:.2f}")
                    
                    # Piazza ordine BUY
                    if self.place_order(symbol, "BUY", quantity, price):
                        logger.info("🎉 NUOVO TRADE REALE ESEGUITO!")
                        return  # Ferma dopo primo successo
                
                time.sleep(30)  # Aspetta 30 secondi
                
            except KeyboardInterrupt:
                logger.info("🛑 Fermato dall'utente")
                break
            except Exception as e:
                logger.error(f"❌ Errore: {e}")
                time.sleep(10)

if __name__ == "__main__":
    trader = WorkingTrader()
    trader.run()

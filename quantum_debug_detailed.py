#!/usr/bin/env python3
"""
QUANTUM DEBUG DETAILED - Scopriamo PERCHÉ il trader fallisce
"""

import requests, hmac, hashlib, time, logging, os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QuantumDebug")

class DebugTrader:
    def __init__(self):
        self.api_key = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
        self.api_secret = "yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"
        self.symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        
    def debug_balance(self):
        """Debug balance con dettagli completi"""
        logger.info("\n" + "="*50)
        logger.info("💰 DEBUG BALANCE COMPLETO")
        logger.info("="*50)
        
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        
        url = f"https://testnet.binance.vision/api/v3/account?{query_string}&signature={signature}"
        headers = {"X-MBX-APIKEY": self.api_key}
        
        logger.info(f"📤 URL: {url}")
        logger.info(f"🔑 API Key: {self.api_key[:20]}...")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        logger.info(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            usdt = next((b for b in data['balances'] if b['asset'] == 'USDT'), None)
            if usdt:
                logger.info(f"✅ USDT Reale: Free={usdt['free']}, Locked={usdt['locked']}")
            else:
                logger.error("❌ USDT non trovato!")
            
            # Mostra tutti i balance
            logger.info("📊 TUTTI I BALANCE:")
            for asset in ['USDT', 'BTC', 'ETH', 'SOL', 'BNB']:
                balance = next((b for b in data['balances'] if b['asset'] == asset), None)
                if balance and (float(balance['free']) > 0 or float(balance['locked']) > 0):
                    logger.info(f"   {asset}: Free={balance['free']}, Locked={balance['locked']}")
        else:
            logger.error(f"❌ ERRORE API: {response.text}")
    
    def debug_order_flow(self, symbol):
        """Debug completo del flusso ordine"""
        logger.info(f"\n🎯 DEBUG ORDINE FLOW: {symbol}")
        logger.info("-" * 40)
        
        try:
            # 1. Ottieni prezzo
            price_url = f"https://testnet.binance.vision/api/v3/ticker/price?symbol={symbol}"
            logger.info(f"📡 Getting price from: {price_url}")
            price_response = requests.get(price_url)
            logger.info(f"📥 Price status: {price_response.status_code}")
            
            if price_response.status_code != 200:
                logger.error(f"❌ Price error: {price_response.text}")
                return
                
            price_data = price_response.json()
            price = float(price_data['price'])
            logger.info(f"💰 Price: ${price:.2f}")
            
            # 2. Calcola position size (simula trader principale)
            balance = 29.70  # Balance reale
            max_position_percent = 0.5  # 50%
            position_size = balance * max_position_percent
            
            logger.info(f"💵 Position size calc: ${balance:.2f} * {max_position_percent} = ${position_size:.2f}")
            
            # 3. Calcola quantità
            if symbol == "BTCUSDT":
                quantity = round(position_size / price, 6)
            elif symbol == "ETHUSDT":
                quantity = round(position_size / price, 5)
            else:
                quantity = round(position_size / price, 3)
                
            logger.info(f"📊 Quantity: {quantity}")
            logger.info(f"💸 Total: ${price * quantity:.2f}")
            
            # 4. Verifica minimi
            min_notional = 5.0  # Minimo Binance
            notional_value = price * quantity
            logger.info(f"📏 Min notional: ${min_notional} | Our: ${notional_value:.2f}")
            
            if notional_value < min_notional:
                logger.error(f"❌ NOTIONAL TOO SMALL: ${notional_value:.2f} < ${min_notional}")
                return
            else:
                logger.info(f"✅ Notional OK: ${notional_value:.2f} >= ${min_notional}")
            
            # 5. Prepara ordine
            timestamp = int(time.time() * 1000)
            query_string = f"symbol={symbol}&side=BUY&type=LIMIT&timeInForce=GTC&quantity={quantity}&price={price}&timestamp={timestamp}"
            signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
            
            url = f"https://testnet.binance.vision/api/v3/order?{query_string}&signature={signature}"
            headers = {"X-MBX-APIKEY": self.api_key}
            
            logger.info(f"📤 Order URL: {url}")
            logger.info(f"📤 Query: {query_string}")
            logger.info(f"🔑 API Key: {self.api_key[:20]}...")
            logger.info(f"🔐 Signature: {signature[:20]}...")
            
            # 6. Invia ordine
            logger.info("🚀 SENDING ORDER...")
            response = requests.post(url, headers=headers, timeout=10)
            
            logger.info(f"📥 Response status: {response.status_code}")
            logger.info(f"📥 Response text: {response.text}")
            
            if response.status_code == 200:
                logger.info("✅ ORDER SUCCESS!")
                order_data = response.json()
                logger.info(f"📄 Order ID: {order_data['orderId']}")
            else:
                logger.error("❌ ORDER FAILED!")
                try:
                    error_data = response.json()
                    logger.error(f"💥 Error code: {error_data.get('code')}")
                    logger.error(f"💥 Error msg: {error_data.get('msg')}")
                except:
                    logger.error(f"💥 Raw error: {response.text}")
                    
        except Exception as e:
            logger.error(f"💥 Exception: {e}")
            import traceback
            logger.error(f"📝 Traceback: {traceback.format_exc()}")
    
    def run(self):
        """Esegui debug completo"""
        logger.info("🚀 QUANTUM DEBUG DETAILED - INIZIO")
        
        # 1. Debug balance
        self.debug_balance()
        
        # 2. Debug ordine per ogni symbol
        for symbol in self.symbols:
            self.debug_order_flow(symbol)
            time.sleep(2)
        
        logger.info("🎯 DEBUG COMPLETATO")

if __name__ == "__main__":
    trader = DebugTrader()
    trader.run()

#!/usr/bin/env python3
"""
QUANTUM TRADER TEST - Versione semplificata per debug
"""

import hmac
import hashlib
import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QuantumTest")

class SimpleTrader:
    def __init__(self):
        self.api_key = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
        self.api_secret = "yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"
        self.base_url = "https://testnet.binance.vision"
    
    def place_simple_order(self, symbol, side, quantity, price):
        """Piazza un ordine semplice per test"""
        timestamp = int(time.time() * 1000)
        
        # Crea query string - ATTENZIONE agli spazi!
        query_string = f"symbol={symbol}&side={side}&type=LIMIT&timeInForce=GTC&quantity={quantity}&price={price}&timestamp={timestamp}"
        
        logger.info(f"🔐 Query string: {query_string}")
        
        # Crea signature
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        logger.info(f"🔐 Signature: {signature[:20]}...")
        
        url = f"{self.base_url}/api/v3/order?{query_string}&signature={signature}"
        headers = {"X-MBX-APIKEY": self.api_key}
        
        logger.info(f"📡 URL: {url}")
        
        try:
            response = requests.post(url, headers=headers, timeout=10)
            logger.info(f"📥 Status: {response.status_code}")
            logger.info(f"📥 Response: {response.text}")
            
            if response.status_code == 200:
                return True, "SUCCESS"
            else:
                return False, response.text
                
        except Exception as e:
            return False, str(e)
    
    def run_test(self):
        """Esegui test completo"""
        logger.info("🚀 QUANTUM TRADER TEST")
        logger.info("="*40)
        
        # Test 1: Ordine piccolo SOL
        success, message = self.place_simple_order("SOLUSDT", "BUY", "0.01", "100")
        
        if success:
            logger.info("✅ TEST ORDINE SUPERATO!")
        else:
            logger.info(f"❌ TEST FALLITO: {message}")

if __name__ == "__main__":
    trader = SimpleTrader()
    trader.run_test()

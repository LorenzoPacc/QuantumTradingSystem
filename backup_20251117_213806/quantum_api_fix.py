#!/usr/bin/env python3
"""
QUANTUM API FIX - Risolve problemi signature e connessione
"""

import hmac
import hashlib
import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QuantumAPIFix")

class APIFixer:
    def __init__(self):
        self.api_key = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
        self.api_secret = "yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"
        self.base_url = "https://testnet.binance.vision"
    
    def create_signature(self, query_string):
        """Crea signature corretta"""
        try:
            signature = hmac.new(
                self.api_secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            return signature
        except Exception as e:
            logger.error(f"❌ Errore creazione signature: {e}")
            return None
    
    def test_api_connection(self):
        """Test completo connessione API"""
        logger.info("🔐 TEST CONNESSIONE API COMPLETO")
        
        # Test 1: Account info
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = self.create_signature(query_string)
        
        if not signature:
            return False
        
        url = f"{self.base_url}/api/v3/account?{query_string}&signature={signature}"
        headers = {"X-MBX-APIKEY": self.api_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                usdt = next((b for b in data['balances'] if b['asset'] == 'USDT'), None)
                if usdt:
                    logger.info(f"✅ API FUNZIONANTE - Balance: {usdt['free']} USDT")
                    return True
            else:
                logger.error(f"❌ API Error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Connection Error: {e}")
            return False
    
    def test_order_placement(self):
        """Test piazzamento ordine"""
        logger.info("🧪 TEST PIAZZAMENTO ORDINE")
        
        symbol = "SOLUSDT"
        quantity = 0.01
        price = 100  # Prezzo improbabile per test
        
        timestamp = int(time.time() * 1000)
        query_string = f"symbol={symbol}&side=BUY&type=LIMIT&timeInForce=GTC&quantity={quantity}&price={price}&timestamp={timestamp}"
        signature = self.create_signature(query_string)
        
        if not signature:
            return False
        
        url = f"{self.base_url}/api/v3/order?{query_string}&signature={signature}"
        headers = {"X-MBX-APIKEY": self.api_key}
        
        try:
            response = requests.post(url, headers=headers, timeout=10)
            # Anche se fallisce per altro motivo, se non è errore signature è OK
            if "Signature" not in response.text or response.status_code == 200:
                logger.info("✅ SIGNATURE API CORRETTA")
                return True
            else:
                logger.error(f"❌ Signature Error: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Order Test Error: {e}")
            return False

def main():
    fixer = APIFixer()
    
    print("🔧 QUANTUM API FIXER")
    print("="*50)
    
    # Test connessione
    if fixer.test_api_connection():
        print("✅ CONNESSIONE API OK")
    else:
        print("❌ PROBLEMA CONNESSIONE API")
        return
    
    # Test ordini
    if fixer.test_order_placement():
        print("✅ SIGNATURE ORDINI OK")
    else:
        print("❌ PROBLEMA SIGNATURE ORDINI")
        return
    
    print("")
    print("🎯 TUTTI I TEST API SUPERATI!")
    print("💡 Il problema potrebbe essere nel codice del trader")

if __name__ == "__main__":
    main()

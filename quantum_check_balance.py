#!/usr/bin/env python3
"""
QUANTUM CHECK BALANCE - Verifica situazione balance e posizioni
"""

import requests
import hmac
import hashlib
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QuantumBalance")

class BalanceChecker:
    def __init__(self):
        self.api_key = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
        self.api_secret = "yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"
    
    def get_complete_balance(self):
        """Ottiene balance completo e posizioni aperte"""
        logger.info("\n" + "="*60)
        logger.info("💰 ANALISI COMPLETA BALANCE E POSIZIONI")
        logger.info("="*60)
        
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        
        url = f"https://testnet.binance.vision/api/v3/account?{query_string}&signature={signature}"
        headers = {"X-MBX-APIKEY": self.api_key}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Balance USDT
            usdt = next((b for b in data['balances'] if b['asset'] == 'USDT'), None)
            if usdt:
                free_usdt = float(usdt['free'])
                locked_usdt = float(usdt['locked'])
                logger.info(f"💵 USDT BALANCE:")
                logger.info(f"   Free:  ${free_usdt:.2f}")
                logger.info(f"   Locked: ${locked_usdt:.2f}")
                logger.info(f"   Total: ${free_usdt + locked_usdt:.2f}")
            
            # Posizioni con valore
            logger.info(f"\n📊 ASSETS CON VALORE:")
            total_assets_value = 0
            
            for asset in ['BTC', 'ETH', 'SOL', 'BNB']:
                balance = next((b for b in data['balances'] if b['asset'] == asset), None)
                if balance and (float(balance['free']) > 0 or float(balance['locked']) > 0):
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    total = free + locked
                    
                    # Ottieni prezzo per calcolare valore
                    if asset != 'USDT':
                        symbol = f"{asset}USDT"
                        price_url = f"https://testnet.binance.vision/api/v3/ticker/price?symbol={symbol}"
                        price_response = requests.get(price_url)
                        
                        if price_response.status_code == 200:
                            price_data = price_response.json()
                            price = float(price_data['price'])
                            asset_value = total * price
                            total_assets_value += asset_value
                            
                            logger.info(f"   {asset}:")
                            logger.info(f"      Quantity: {total}")
                            logger.info(f"      Price: ${price:.2f}")
                            logger.info(f"      Value: ${asset_value:.2f}")
            
            # Valore totale portfolio
            total_portfolio = free_usdt + total_assets_value
            logger.info(f"\n🏦 PORTFOLIO TOTALE:")
            logger.info(f"   Cash: ${free_usdt:.2f}")
            logger.info(f"   Assets: ${total_assets_value:.2f}")
            logger.info(f"   TOTAL: ${total_portfolio:.2f}")
            
            return free_usdt, total_assets_value
            
        else:
            logger.error(f"❌ Errore API: {response.text}")
            return 0, 0
    
    def get_open_orders(self):
        """Verifica ordini aperti"""
        logger.info(f"\n📋 ORDINI APERTI:")
        
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        
        url = f"https://testnet.binance.vision/api/v3/openOrders?{query_string}&signature={signature}"
        headers = {"X-MBX-APIKEY": self.api_key}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            orders = response.json()
            if orders:
                for order in orders:
                    logger.info(f"   {order['symbol']}: {order['side']} {order['origQty']} @ ${order['price']}")
            else:
                logger.info("   ✅ Nessun ordine aperto")
        else:
            logger.error(f"❌ Errore ordini aperti: {response.text}")

if __name__ == "__main__":
    checker = BalanceChecker()
    
    # 1. Balance completo
    free_usdt, assets_value = checker.get_complete_balance()
    
    # 2. Ordini aperti
    checker.get_open_orders()
    
    # 3. Raccomandazioni
    logger.info(f"\n🎯 RACCOMANDAZIONI:")
    
    if free_usdt < 5:
        logger.info("   ❌ Balance insufficiente per nuovi trade")
        logger.info("   💡 Aspetta che le posizioni si chiudano o deposita più USDT")
    elif free_usdt < 15:
        logger.info("   ⚠️  Balance limitato")
        logger.info("   💡 Trade solo 1 posizione alla volta")
    else:
        logger.info("   ✅ Balance sufficiente per trading")
    
    logger.info(f"\n💡 STRATEGIA CONSIGLIATA:")
    logger.info(f"   Con ${free_usdt:.2f} USDT disponibili:")
    logger.info(f"   - Massimo 1 trade alla volta")
    logger.info(f"   - Position size: ${free_usdt * 0.5:.2f} (50%)")
    logger.info(f"   - Stop dopo 1 trade successful")

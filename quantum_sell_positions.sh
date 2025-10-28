#!/bin/bash
echo "🔄 VENDITA POSIZIONI PER RECUPERARE USDT"
echo "========================================"

python3 << 'END'
import requests
import hmac
import hashlib
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QuantumSell")

class PositionSeller:
    def __init__(self):
        self.api_key = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
        self.api_secret = "yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"
    
    def sell_asset(self, symbol, quantity):
        """Vendi asset per USDT"""
        try:
            # Ottieni prezzo corrente
            price_url = f"https://testnet.binance.vision/api/v3/ticker/price?symbol={symbol}"
            price_data = requests.get(price_url).json()
            current_price = float(price_data['price'])
            
            logger.info(f"🎯 VENDITA {symbol}:")
            logger.info(f"   Quantità: {quantity}")
            logger.info(f"   Prezzo corrente: ${current_price:.2f}")
            logger.info(f"   Totale: ${current_price * quantity:.2f}")
            
            # Ordine MARKET per vendita immediata
            timestamp = int(time.time() * 1000)
            query_string = f"symbol={symbol}&side=SELL&type=MARKET&quantity={quantity}&timestamp={timestamp}"
            signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
            
            url = f"https://testnet.binance.vision/api/v3/order?{query_string}&signature={signature}"
            headers = {"X-MBX-APIKEY": self.api_key}
            
            logger.info("🚀 Invio ordine di vendita...")
            response = requests.post(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                order_data = response.json()
                logger.info("✅ VENDITA RIUSCITA!")
                
                # Calcola USDT ottenuti
                fills = order_data.get('fills', [])
                total_usdt = sum(float(fill['price']) * float(fill['qty']) for fill in fills)
                logger.info(f"💰 USDT ottenuti: ${total_usdt:.2f}")
                return True
            else:
                logger.error(f"❌ Vendita fallita: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Errore: {e}")
            return False
    
    def get_balance(self, asset):
        """Ottieni balance di un asset"""
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        
        url = f"https://testnet.binance.vision/api/v3/account?{query_string}&signature={signature}"
        headers = {"X-MBX-APIKEY": self.api_key}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            balance = next((b for b in data['balances'] if b['asset'] == asset), None)
            return float(balance['free']) if balance else 0.0
        return 0.0

# Esegui vendite
seller = PositionSeller()

print("📊 BALANCE ATTUALI PRIMA DELLA VENDITA:")
eth_balance = seller.get_balance("ETH")
sol_balance = seller.get_balance("SOL") 

print(f"   ETH: {eth_balance}")
print(f"   SOL: {sol_balance}")

# Vendita posizioni (solo le quantità in eccesso)
if eth_balance > 3.5:  # Tieni 3.5 ETH, vendi il resto
    qty_to_sell = eth_balance - 3.5
    if qty_to_sell > 0.01:
        print(f"\n🔄 Vendita {qty_to_sell} ETH in eccesso...")
        seller.sell_asset("ETHUSDT", round(qty_to_sell, 4))

if sol_balance > 1.0:  # Tieni 1.0 SOL, vendi il resto  
    qty_to_sell = sol_balance - 1.0
    if qty_to_sell > 0.01:
        print(f"\n🔄 Vendita {qty_to_sell} SOL in eccesso...")
        seller.sell_asset("SOLUSDT", round(qty_to_sell, 3))

time.sleep(2)

# Verifica nuovo balance USDT
new_usdt = seller.get_balance("USDT")
print(f"\n💰 NUOVO BALANCE USDT: ${new_usdt:.2f}")
END

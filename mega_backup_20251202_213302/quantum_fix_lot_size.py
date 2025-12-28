#!/usr/bin/env python3
"""
QUANTUM FIX LOT_SIZE - Risolve i problemi di quantità minima
"""

import requests
import hmac
import hashlib
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QuantumFix")

class LotSizeFixer:
    def __init__(self):
        self.api_key = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
        self.api_secret = "yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"
        
    def get_symbol_info(self, symbol):
        """Ottiene informazioni dettagliate sul symbol (filtri LOT_SIZE)"""
        url = "https://testnet.binance.vision/api/v3/exchangeInfo"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            for s in data['symbols']:
                if s['symbol'] == symbol:
                    logger.info(f"📋 SYMBOL INFO per {symbol}:")
                    
                    # Trova filtro LOT_SIZE
                    lot_size_filter = next((f for f in s['filters'] if f['filterType'] == 'LOT_SIZE'), None)
                    if lot_size_filter:
                        logger.info(f"📏 LOT_SIZE FILTER:")
                        logger.info(f"   Min Qty: {lot_size_filter.get('minQty')}")
                        logger.info(f"   Max Qty: {lot_size_filter.get('maxQty')}")
                        logger.info(f"   Step Size: {lot_size_filter.get('stepSize')}")
                    
                    # Trova filtro MIN_NOTIONAL
                    notional_filter = next((f for f in s['filters'] if f['filterType'] == 'MIN_NOTIONAL'), None)
                    if notional_filter:
                        logger.info(f"💰 MIN_NOTIONAL FILTER:")
                        logger.info(f"   Min Notional: {notional_filter.get('minNotional')}")
                    
                    # Trova filtro PRICE_FILTER
                    price_filter = next((f for f in s['filters'] if f['filterType'] == 'PRICE_FILTER'), None)
                    if price_filter:
                        logger.info(f"💲 PRICE_FILTER:")
                        logger.info(f"   Min Price: {price_filter.get('minPrice')}")
                        logger.info(f"   Max Price: {price_filter.get('maxPrice')}")
                        logger.info(f"   Tick Size: {price_filter.get('tickSize')}")
                    
                    return lot_size_filter
        return None
    
    def calculate_proper_quantity(self, symbol, desired_usd_amount):
        """Calcola la quantità corretta rispettando LOT_SIZE"""
        # Ottieni prezzo corrente
        price_url = f"https://testnet.binance.vision/api/v3/ticker/price?symbol={symbol}"
        price_response = requests.get(price_url)
        
        if price_response.status_code != 200:
            logger.error(f"❌ Errore prezzo per {symbol}: {price_response.text}")
            return None
            
        price_data = price_response.json()
        price = float(price_data['price'])
        
        # Calcola quantità grezza
        raw_quantity = desired_usd_amount / price
        
        # Ottieni info symbol per LOT_SIZE
        lot_size_filter = self.get_symbol_info(symbol)
        
        if not lot_size_filter:
            logger.error(f"❌ Impossibile ottenere LOT_SIZE per {symbol}")
            return None
        
        # Applica regole LOT_SIZE
        min_qty = float(lot_size_filter.get('minQty', 0))
        step_size = float(lot_size_filter.get('stepSize', 0))
        
        logger.info(f"🔢 Calcolo quantità per {symbol}:")
        logger.info(f"   Prezzo: ${price:.2f}")
        logger.info(f"   Quantità grezza: {raw_quantity}")
        logger.info(f"   Min Qty: {min_qty}")
        logger.info(f"   Step Size: {step_size}")
        
        # Arrotonda per step size
        if step_size > 0:
            # Calcola quanti step
            steps = raw_quantity / step_size
            # Arrotonda per eccesso al passo successivo
            adjusted_steps = int(steps) 
            if steps > int(steps):  # Se c'è resto, aggiungi un passo
                adjusted_steps += 1
            adjusted_quantity = adjusted_steps * step_size
        else:
            adjusted_quantity = raw_quantity
        
        # Verifica minimo
        if adjusted_quantity < min_qty:
            adjusted_quantity = min_qty
            logger.warning(f"⚠️  Quantità sotto minimo, impostato a: {min_qty}")
        
        # Formatta in base al symbol
        if symbol == "BTCUSDT":
            final_quantity = round(adjusted_quantity, 6)
        elif symbol == "ETHUSDT":
            final_quantity = round(adjusted_quantity, 5)
        else:
            final_quantity = round(adjusted_quantity, 3)
        
        # Verifica notional minimo
        notional_value = price * final_quantity
        min_notional = 5.0  # Binance testnet
        
        logger.info(f"📊 QUANTITÀ FINALE:")
        logger.info(f"   Quantità: {final_quantity}")
        logger.info(f"   Valore Notional: ${notional_value:.2f}")
        logger.info(f"   Min Notional: ${min_notional}")
        
        if notional_value < min_notional:
            logger.error(f"❌ NOTIONAL TROPPO PICCOLO: ${notional_value:.2f} < ${min_notional}")
            return None
        
        logger.info(f"✅ QUANTITÀ VALIDA: {final_quantity} ({symbol})")
        return final_quantity
    
    def test_fixed_orders(self):
        """Test ordini con quantità corrette"""
        symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        desired_amount = 14.85  # 50% di $29.70
        
        for symbol in symbols:
            logger.info(f"\n🎯 TEST {symbol}:")
            logger.info("-" * 30)
            
            quantity = self.calculate_proper_quantity(symbol, desired_amount)
            
            if quantity:
                # Test ordine
                self.test_order(symbol, quantity)
            else:
                logger.error(f"❌ Impossibile calcolare quantità per {symbol}")
            
            time.sleep(1)
    
    def test_order(self, symbol, quantity):
        """Testa un ordine con la quantità corretta"""
        try:
            # Ottieni prezzo
            price_url = f"https://testnet.binance.vision/api/v3/ticker/price?symbol={symbol}"
            price_response = requests.get(price_url)
            price_data = price_response.json()
            price = float(price_data['price'])
            
            timestamp = int(time.time() * 1000)
            query_string = f"symbol={symbol}&side=BUY&type=LIMIT&timeInForce=GTC&quantity={quantity}&price={price}&timestamp={timestamp}"
            signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
            
            url = f"https://testnet.binance.vision/api/v3/order?{query_string}&signature={signature}"
            headers = {"X-MBX-APIKEY": self.api_key}
            
            logger.info(f"🚀 INVIO ORDINE TEST...")
            response = requests.post(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ ORDINE TEST RIUSCITO!")
                order_data = response.json()
                logger.info(f"📄 Order ID: {order_data['orderId']}")
                
                # Annulla ordine test
                self.cancel_order(symbol, order_data['orderId'])
            else:
                logger.error(f"❌ ORDINE TEST FALLITO: {response.text}")
                
        except Exception as e:
            logger.error(f"💥 Errore test ordine: {e}")
    
    def cancel_order(self, symbol, order_id):
        """Annulla ordine test"""
        try:
            timestamp = int(time.time() * 1000)
            query_string = f"symbol={symbol}&orderId={order_id}&timestamp={timestamp}"
            signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
            
            url = f"https://testnet.binance.vision/api/v3/order?{query_string}&signature={signature}"
            headers = {"X-MBX-APIKEY": self.api_key}
            
            response = requests.delete(url, headers=headers)
            if response.status_code == 200:
                logger.info(f"🗑️ Ordine test cancellato: {order_id}")
            else:
                logger.warning(f"⚠️ Impossibile cancellare ordine test: {response.text}")
        except Exception as e:
            logger.warning(f"⚠️ Errore cancellazione ordine: {e}")

if __name__ == "__main__":
    fixer = LotSizeFixer()
    
    # Prima mostra i requisiti per ogni symbol
    logger.info("🔍 ANALISI REQUISITI LOT_SIZE:")
    for symbol in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        fixer.get_symbol_info(symbol)
        time.sleep(0.5)
    
    # Poi testa ordini corretti
    logger.info("\n🎯 TEST ORDINI CON QUANTITÀ CORRETTE:")
    fixer.test_fixed_orders()

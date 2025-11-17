#!/usr/bin/env python3
"""
QUANTUM CHECK TRADE HISTORY - Verifica tutti i trade eseguiti
"""

import requests
import hmac
import hashlib
import time
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QuantumHistory")

class TradeHistoryAnalyzer:
    def __init__(self):
        self.api_key = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
        self.api_secret = "yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"
    
    def get_all_trades(self, symbol):
        """Ottieni tutti i trade per un symbol"""
        timestamp = int(time.time() * 1000)
        query_string = f"symbol={symbol}&timestamp={timestamp}"
        signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        
        url = f"https://testnet.binance.vision/api/v3/myTrades?{query_string}&signature={signature}"
        headers = {"X-MBX-APIKEY": self.api_key}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            trades = response.json()
            logger.info(f"📊 STORICO TRADE {symbol}: {len(trades)} trade")
            
            total_buy = 0
            total_sell = 0
            buy_qty = 0
            sell_qty = 0
            
            for trade in trades[-10:]:  # Ultimi 10 trade
                side = trade['isBuyer'] and 'BUY' or 'SELL'
                quote_qty = float(trade['quoteQty'])
                qty = float(trade['qty'])
                price = float(trade['price'])
                
                if side == 'BUY':
                    total_buy += quote_qty
                    buy_qty += qty
                else:
                    total_sell += quote_qty
                    sell_qty += qty
                
                logger.info(f"   {trade['time']} {side} {qty} @ ${price} = ${quote_qty:.2f}")
            
            logger.info(f"   TOTALE BUY: ${total_buy:.2f}")
            logger.info(f"   TOTALE SELL: ${total_sell:.2f}")
            logger.info(f"   NET: ${total_sell - total_buy:.2f}")
            logger.info(f"   POSITION: {buy_qty - sell_qty} {symbol.replace('USDT', '')}")
            
            return trades
        else:
            logger.error(f"❌ Errore storico {symbol}: {response.text}")
            return []

def main():
    analyzer = TradeHistoryAnalyzer()
    
    logger.info("🔍 ANALISI STORICO TRADE - DOVE SONO FINITI I $10,000?")
    logger.info("=" * 60)
    
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
    
    for symbol in symbols:
        analyzer.get_all_trades(symbol)
        time.sleep(1)

if __name__ == "__main__":
    main()

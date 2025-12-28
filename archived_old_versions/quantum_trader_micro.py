#!/usr/bin/env python3
"""
QUANTUM TRADING - MICRO MODE
Versione per fondi limitati ($84) con lot size minimi
"""

import os
import sys
import logging
import sqlite3
import time
from datetime import datetime

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QuantumTraderMicro")

print("🚀 QUANTUM TRADER - MICRO MODE")
print("===============================")
print("💰 Balance: $84.65")
print("📈 Trading ultra-conservativo")
print("🎯 Lot size minimi Binance")
print("===============================")

# Importa il trader originale
try:
    from quantum_trader_ultimate_final import QuantumTraderUltimateFinal
except ImportError as e:
    logger.error(f"❌ Errore importazione: {e}")
    sys.exit(1)

class MicroTrader(QuantumTraderUltimateFinal):
    def __init__(self):
        super().__init__()
        
        # PARAMETRI ULTRA-CONSERVATIVI per $84
        self.position_size = 5.0    # Solo 5 USDT per trade
        self.max_positions = 1      # Solo 1 posizione alla volta
        self.min_balance = 10.0     # Ferma se sotto 10 USDT
        
        # Lot size minimi Binance per symbol
        self.min_quantities = {
            "BTCUSDT": 0.00001,  # Min 0.00001 BTC
            "ETHUSDT": 0.0001,   # Min 0.0001 ETH  
            "SOLUSDT": 0.01      # Min 0.01 SOL
        }
        
        logger.info("🎯 PARAMETRI MICRO TRADING:")
        logger.info(f"   • Position Size: {self.position_size} USDT")
        logger.info(f"   • Max Positions: {self.max_positions}")
        logger.info(f"   • Min Balance: {self.min_balance} USDT")
        
    def calculate_quantity(self, symbol, price):
        """Calcola quantità rispettando i lot size minimi di Binance"""
        # Calcola quantità base
        base_quantity = self.position_size / price
        
        # Applica lot size minimo
        min_qty = self.min_quantities.get(symbol, 0.001)
        quantity = max(base_quantity, min_qty)
        
        # Arrotonda per precisione
        if symbol == "BTCUSDT":
            quantity = round(quantity, 6)
        elif symbol == "ETHUSDT":
            quantity = round(quantity, 5)
        else:
            quantity = round(quantity, 3)
            
        logger.info(f"📊 {symbol}: Qty={quantity:.6f} (Min: {min_qty}) @ ${price:.2f}")
        return quantity
    
    def can_open_position(self, symbol):
        """Controlli rigorosi per fondi limitati"""
        balance = self.get_available_balance()
        
        if balance < self.position_size:
            logger.warning(f"⛔ Fondi insufficienti: ${balance:.2f} < ${self.position_size:.2f}")
            return False
            
        if balance < self.min_balance:
            logger.warning(f"🛑 Balance critico: ${balance:.2f} < ${self.min_balance:.2f}")
            return False
            
        # Verifica posizioni aperte
        conn = sqlite3.connect('quantum_final.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM open_positions WHERE status = 'OPEN'")
        open_count = cursor.fetchone()[0]
        conn.close()
        
        if open_count >= self.max_positions:
            logger.warning(f"📈 Posizioni massime raggiunte: {open_count}/{self.max_positions}")
            return False
            
        logger.info(f"✅ Condizioni OK: Balance=${balance:.2f}, Posizioni={open_count}")
        return True
    
    def open_position(self, symbol, signal):
        """Override con controlli extra per micro trading"""
        if not self.can_open_position(symbol):
            return False
            
        logger.info(f"🎯 Tentativo MICRO trade: {symbol} {signal} con ${self.position_size}")
        
        # Chiama la funzione originale
        result = super().open_position(symbol, signal)
        
        if result:
            logger.info(f"✅ MICRO posizione aperta: {symbol}")
            # Aspetta prima del prossimo trade
            time.sleep(10)
        else:
            logger.warning(f"❌ Fallito MICRO trade: {symbol}")
            
        return result

if __name__ == "__main__":
    trader = MicroTrader()
    trader.run()

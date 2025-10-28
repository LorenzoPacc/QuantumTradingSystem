#!/usr/bin/env python3
"""
QUANTUM TRADING - MICRO MODE FIXED
Versione corretta con filtri Binance
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

print("🚀 QUANTUM TRADING - MICRO MODE FIXED")
print("======================================")
print("💰 Balance: $84.65")
print("🎯 Minimi Binance rispettati")
print("======================================")

# Importa il trader originale
try:
    from quantum_trader_ultimate_final import QuantumTraderUltimateFinal
except ImportError as e:
    logger.error(f"❌ Errore importazione: {e}")
    sys.exit(1)

class MicroTraderFixed(QuantumTraderUltimateFinal):
    def __init__(self):
        super().__init__()
        
        # PARAMETRI CORRETTI per minimi Binance
        self.position_size = 15.0   # $15 per rispettare NOTIONAL
        self.max_positions = 1      # Solo 1 posizione
        self.min_balance = 20.0     # Ferma se sotto $20
        
        # Minimi NOTIONAL di Binance Testnet
        self.min_notional = {
            "BTCUSDT": 10.0,   # Min $10 per BTC
            "ETHUSDT": 10.0,   # Min $10 per ETH
            "SOLUSDT": 10.0    # Min $10 per SOL
        }
        
        # Minime quantità LOT_SIZE
        self.min_quantities = {
            "BTCUSDT": 0.00001,
            "ETHUSDT": 0.0001, 
            "SOLUSDT": 0.01
        }
        
        logger.info("🎯 PARAMETRI MICRO FIXED:")
        logger.info(f"   • Position Size: {self.position_size} USDT")
        logger.info(f"   • Max Positions: {self.max_positions}")
        logger.info(f"   • Min Balance: {self.min_balance} USDT")
        logger.info("   • Min Notional: $10.00 per tutti i symbol")
        
    def calculate_quantity(self, symbol, price):
        """Calcola quantità che rispetta NOTIONAL e LOT_SIZE"""
        # Calcola quantità base
        base_quantity = self.position_size / price
        
        # Applica LOT_SIZE minimo
        min_qty = self.min_quantities.get(symbol, 0.001)
        quantity = max(base_quantity, min_qty)
        
        # Verifica NOTIONAL minimo
        notional_value = quantity * price
        min_notional = self.min_notional.get(symbol, 10.0)
        
        if notional_value < min_notional:
            # Aumenta quantità per raggiungere NOTIONAL minimo
            quantity = min_notional / price
            logger.info(f"⚡ Aumento quantità per NOTIONAL: {quantity:.6f}")
        
        # Arrotonda per precisione
        if symbol == "BTCUSDT":
            quantity = round(quantity, 6)
        elif symbol == "ETHUSDT":
            quantity = round(quantity, 5)
        else:
            quantity = round(quantity, 3)
            
        final_notional = quantity * price
        logger.info(f"📊 {symbol}: Qty={quantity:.6f} @ ${price:.2f} = ${final_notional:.2f}")
        
        return quantity
    
    def can_open_position(self, symbol):
        """Controlli rigorosi"""
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
            logger.warning(f"📈 Posizioni massime: {open_count}/{self.max_positions}")
            return False
            
        logger.info(f"✅ Condizioni OK: Balance=${balance:.2f}, Posizioni={open_count}")
        return True
    
    def open_position(self, symbol, signal):
        """Override con controlli NOTIONAL"""
        if not self.can_open_position(symbol):
            return False
            
        # Ottieni prezzo per calcolo NOTIONAL
        price = self.get_current_price(symbol)
        if not price:
            return False
            
        quantity = self.calculate_quantity(symbol, price)
        notional_value = quantity * price
        
        logger.info(f"🎯 Tentativo MICRO trade: {symbol} {signal}")
        logger.info(f"   💰 Size: ${self.position_size} | Qty: {quantity:.6f}")
        logger.info(f"   📊 Notional: ${notional_value:.2f}")
        
        # Chiama la funzione originale
        result = super().open_position(symbol, signal)
        
        if result:
            logger.info(f"✅ MICRO posizione aperta: {symbol}")
            time.sleep(15)  # Aspetta prima del prossimo
        else:
            logger.warning(f"❌ Fallito MICRO trade: {symbol}")
            
        return result

if __name__ == "__main__":
    trader = MicroTraderFixed()
    trader.run()

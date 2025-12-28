#!/usr/bin/env python3
"""
QUANTUM TRADING - TESTNET OPTIMIZED
Versione ottimizzata per fondi limitati del testnet
"""

import os
import sys
import logging
import sqlite3

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QuantumTraderTestnet")

# Importa il trader originale
sys.path.append('.')

try:
    from quantum_trader_ultimate_final import QuantumTraderUltimateFinal
    logger.info("✅ Importato QuantumTraderUltimateFinal")
except ImportError as e:
    logger.error(f"❌ Errore importazione: {e}")
    sys.exit(1)

class TestnetOptimizedTrader(QuantumTraderUltimateFinal):
    def __init__(self):
        super().__init__()
        # Override dei parametri per testnet
        self.position_size = 2.0  # Solo 2 USDT per trade
        self.max_positions = 1    # Massimo 1 posizione alla volta
        self.min_balance_threshold = 5.0  # Fermarsi se sotto 5 USDT
        logger.info("💰 PARAMETRI TESTNET OTTIMIZZATI:")
        logger.info(f"   • Position Size: {self.position_size} USDT")
        logger.info(f"   • Max Positions: {self.max_positions}")
        logger.info(f"   • Min Balance: {self.min_balance_threshold} USDT")
        
    def get_available_balance(self):
        """Ottiene il balance disponibile con controllo sicurezza"""
        try:
            balance = super().get_available_balance()
            logger.info(f"💰 Balance disponibile: ${balance:.2f}")
            return balance
        except Exception as e:
            logger.error(f"❌ Errore recupero balance: {e}")
            return 0.0
            
    def get_open_positions_count(self):
        """Conta le posizioni aperte"""
        try:
            conn = sqlite3.connect('quantum_final.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM open_positions WHERE status = 'OPEN'")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"❌ Errore conteggio posizioni: {e}")
            return 0

    def can_open_position(self, symbol):
        """Controlla se può aprire una posizione"""
        available_balance = self.get_available_balance()
        
        # Controllo fondi insufficienti
        if available_balance < self.position_size:
            logger.warning(f"⛔ Fondi insufficienti: ${available_balance:.2f} < ${self.position_size:.2f}")
            return False
            
        # Controllo balance minimo
        if available_balance < self.min_balance_threshold:
            logger.warning(f"🛑 Balance troppo basso: ${available_balance:.2f}")
            return False
            
        # Controllo numero massimo posizioni
        open_positions = self.get_open_positions_count()
        if open_positions >= self.max_positions:
            logger.warning(f"📈 Numero massimo posizioni raggiunto: {open_positions}/{self.max_positions}")
            return False
            
        logger.info(f"✅ Condizioni OK per apertura: Balance=${available_balance:.2f}, Posizioni={open_positions}")
        return True
        
    def open_position(self, symbol, signal):
        """Override della funzione di apertura con controlli aggiuntivi"""
        if not self.can_open_position(symbol):
            logger.warning(f"⏸️  Apertura bloccata per {symbol}")
            return False
            
        logger.info(f"🎯 Tentativo apertura {symbol} {signal} con {self.position_size} USDT")
        result = super().open_position(symbol, signal)
        
        if result:
            logger.info(f"✅ Posizione aperta con successo per {symbol}")
        else:
            logger.warning(f"❌ Fallita apertura posizione per {symbol}")
            
        return result

if __name__ == "__main__":
    print("🚀 QUANTUM TRADER - TESTNET OPTIMIZED")
    print("======================================")
    print("💰 Position size: 2.0 USDT")
    print("📈 Max positions: 1")
    print("🎯 Min balance: 5.0 USDT")
    print("======================================")
    
    try:
        trader = TestnetOptimizedTrader()
        trader.run()
    except KeyboardInterrupt:
        print("\n🛑 Trader fermato dall'utente")
    except Exception as e:
        logger.error(f"❌ Errore avvio trader: {e}")
        import traceback
        traceback.print_exc()

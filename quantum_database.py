#!/usr/bin/env python3
"""
QUANTUM DATABASE - GESTIONE DATI ATOMICHE
"""
import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QuantumDB")

class QuantumDatabase:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        """Inizializza database con tabelle ottimizzate"""
        conn = sqlite3.connect('quantum_secure.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # Tabella balance con timestamp
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                balance REAL NOT NULL,
                available REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabella trades con stato
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                entry_price REAL NOT NULL,
                status TEXT NOT NULL,
                order_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabella system_log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                level TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database inizializzato")
    
    def log_balance(self, balance: float, available: float):
        """Salva balance atomicamente"""
        try:
            conn = sqlite3.connect('quantum_secure.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO balance_history (balance, available) VALUES (?, ?)",
                (balance, available)
            )
            conn.commit()
            conn.close()
            logger.info(f"💾 Balance salvato: ${balance:.2f} (disponibile: ${available:.2f})")
        except Exception as e:
            logger.error(f"❌ Errore salvataggio balance: {e}")
    
    def get_last_balance(self) -> tuple:
        """Recupera ultimo balance convalidato"""
        try:
            conn = sqlite3.connect('quantum_secure.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT balance, available FROM balance_history ORDER BY timestamp DESC LIMIT 1"
            )
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0], result[1]
            return 0.0, 0.0
        except:
            return 0.0, 0.0
    
    def log_trade(self, symbol: str, side: str, quantity: float, price: float, status: str, order_id: str = ""):
        """Salva trade nel database"""
        try:
            conn = sqlite3.connect('quantum_secure.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO trades (symbol, side, quantity, entry_price, status, order_id) VALUES (?, ?, ?, ?, ?, ?)",
                (symbol, side, quantity, price, status, order_id)
            )
            conn.commit()
            conn.close()
            logger.info(f"💾 Trade salvato: {symbol} {side} {quantity} @ ${price:.2f} - {status}")
        except Exception as e:
            logger.error(f"❌ Errore salvataggio trade: {e}")
    
    def log_system(self, message: str, level: str = "INFO"):
        """Log sistema"""
        try:
            conn = sqlite3.connect('quantum_secure.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO system_log (message, level) VALUES (?, ?)",
                (message, level)
            )
            conn.commit()
            conn.close()
        except:
            pass

# Istanza globale
db = QuantumDatabase()

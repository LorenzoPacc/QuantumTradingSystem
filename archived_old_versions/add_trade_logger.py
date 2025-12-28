import sqlite3
from datetime import datetime

class TradeLogger:
    """Registra automaticamente tutti i trade nel database"""
    
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect('trading_performance.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            symbol TEXT,
            action TEXT,
            quantity REAL,
            entry_price REAL,
            exit_price REAL,
            pnl_percent REAL,
            reason TEXT,
            amount REAL
        )
        ''')
        conn.commit()
        conn.close()
    
    def log_trade(self, symbol, action, quantity, price, amount, reason, pnl_percent=0.0):
        try:
            conn = sqlite3.connect('trading_performance.db')
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO trade_performance 
            (timestamp, symbol, action, quantity, entry_price, amount, pnl_percent, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                symbol,
                action,
                quantity,
                price,
                amount,
                pnl_percent,
                reason
            ))
            
            conn.commit()
            conn.close()
            print(f"📝 Trade registrato: {action} {symbol} - {quantity} @ ${price}")
            
        except Exception as e:
            print(f"❌ Errore registrazione trade: {e}")

# Aggiungi questa riga alla classe QuantumTraderUltimateFixed
def add_trade_logging_to_trader():
    with open('quantum_ultimate_fixed.py', 'r') as f:
        content = f.read()
    
    # Aggiungi il trade logger all'__init__
    if 'class TradeLogger:' not in content:
        with open('quantum_ultimate_fixed.py', 'a') as f:
            f.write('\n\n')
            f.write(open('add_trade_logger.py').read())
    
    print("✅ TradeLogger aggiunto al trader")

add_trade_logging_to_trader()

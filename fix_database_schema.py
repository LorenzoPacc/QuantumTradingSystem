import sqlite3
import os
from datetime import datetime

def fix_database_schema():
    print("🔧 Correzione struttura database...")
    
    # Rinomina il vecchio database
    if os.path.exists('trading_performance.db'):
        os.rename('trading_performance.db', 'trading_performance_backup.db')
        print("📦 Backup database creato")
    
    # Crea nuovo database con schema corretto
    conn = sqlite3.connect('trading_performance.db')
    cursor = conn.cursor()
    
    # Crea tabella con schema completo
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trade_performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        symbol TEXT NOT NULL,
        action TEXT NOT NULL,
        quantity REAL NOT NULL,
        entry_price REAL NOT NULL,
        exit_price REAL DEFAULT NULL,
        pnl_percent REAL DEFAULT 0.0,
        reason TEXT,
        amount REAL NOT NULL,
        status TEXT DEFAULT 'OPEN'
    )
    ''')
    
    # Inserisci i trade attuali come dati iniziali REALI
    current_trades = [
        ('BTCUSDT', 'BUY', 0.000443, 101570.93, 0.0, 'FEAR_STRATEGY', 45.00),
        ('ETHUSDT', 'BUY', 0.01332, 3377.54, -0.02, 'FEAR_STRATEGY', 45.00),
        ('SOLUSDT', 'BUY', 0.27372, 157.33, 0.0, 'FEAR_STRATEGY', 43.07),
        ('AVAXUSDT', 'BUY', 1.51562, 17.29, 0.0, 'FEAR_STRATEGY', 26.21),
        ('LINKUSDT', 'BUY', 1.04153, 15.31, 0.0, 'FEAR_STRATEGY', 15.95),
        ('DOTUSDT', 'BUY', 3.125, 3.20, -0.09, 'FEAR_STRATEGY', 10.00)
    ]
    
    for symbol, action, quantity, entry_price, pnl, reason, amount in current_trades:
        cursor.execute('''
        INSERT INTO trade_performance 
        (timestamp, symbol, action, quantity, entry_price, pnl_percent, reason, amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            symbol,
            action,
            quantity,
            entry_price,
            pnl,
            reason,
            amount
        ))
    
    conn.commit()
    
    # Verifica
    cursor.execute('SELECT COUNT(*) FROM trade_performance')
    count = cursor.fetchone()[0]
    
    cursor.execute('PRAGMA table_info(trade_performance)')
    columns = [col[1] for col in cursor.fetchall()]
    
    conn.close()
    
    print(f"✅ Database corretto creato: {count} trade inseriti")
    print(f"📊 Colonne disponibili: {columns}")
    return True

if __name__ == "__main__":
    fix_database_schema()

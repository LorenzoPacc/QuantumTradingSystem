import sqlite3
import os

def create_complete_database():
    print("🗃️ CREAZIONE DATABASE COMPLETO...")
    
    # Rimuovi database esistente
    if os.path.exists('quantum_final.db'):
        os.rename('quantum_final.db', 'quantum_final.db.backup')
        print("✅ Backup database esistente creato")
    
    # Crea nuovo database con schema COMPLETO
    conn = sqlite3.connect('quantum_final.db')
    cursor = conn.cursor()
    
    # Schema COMPLETO per trades
    cursor.execute('''
        CREATE TABLE trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            quantity REAL NOT NULL,
            entry_price REAL NOT NULL,
            exit_price REAL,
            pnl REAL,
            pnl_pct REAL,
            confidence REAL,
            confluence_score REAL,
            take_profit REAL,
            stop_loss REAL,
            exit_reason TEXT,
            order_id TEXT,
            timeframe_alignment TEXT,
            strategy_version TEXT DEFAULT 'ultimate_final',
            trade_duration_minutes REAL,
            ml_confidence_boost REAL
        )
    ''')
    
    # Schema per open_positions
    cursor.execute('''
        CREATE TABLE open_positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL UNIQUE,
            side TEXT NOT NULL,
            quantity REAL NOT NULL,
            entry_price REAL NOT NULL,
            take_profit REAL,
            stop_loss REAL,
            order_id TEXT,
            opened_at TEXT NOT NULL
        )
    ''')
    
    # Schema per balance_history
    cursor.execute('''
        CREATE TABLE balance_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            balance REAL NOT NULL,
            note TEXT
        )
    ''')
    
    # Schema per multi_timeframe_analysis
    cursor.execute('''
        CREATE TABLE multi_timeframe_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            confluence_score REAL,
            confidence REAL,
            signal TEXT,
            tech_score REAL,
            macro_score REAL,
            market_score REAL,
            weight REAL
        )
    ''')
    
    # Inserisci balance iniziale
    cursor.execute('''
        INSERT INTO balance_history (timestamp, balance, note)
        VALUES (datetime('now'), 200.0, 'Balance iniziale - Database nuovo')
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Database completo creato!")
    print("💰 Balance iniziale: $200.00")

if __name__ == "__main__":
    create_complete_database()

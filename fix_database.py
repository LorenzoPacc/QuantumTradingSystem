import sqlite3
import os

db_path = "trading_final.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Aggiungi colonna order_id se manca
        cursor.execute("PRAGMA table_info(open_positions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'order_id' not in columns:
            cursor.execute("ALTER TABLE open_positions ADD COLUMN order_id INTEGER")
            print("✅ Aggiunta colonna order_id")
        
        if 'trade_duration_minutes' not in columns:
            cursor.execute("ALTER TABLE open_positions ADD COLUMN trade_duration_minutes INTEGER")
            print("✅ Aggiunta colonna trade_duration_minutes")
            
        conn.commit()
        print("✅ Database schema aggiornato!")
        
    except Exception as e:
        print(f"❌ Errore database: {e}")
    finally:
        conn.close()
else:
    print("✅ Database non esiste, sarà creato automaticamente")

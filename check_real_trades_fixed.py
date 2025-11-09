import sqlite3
import time
from datetime import datetime

def monitor_real_trades_fixed():
    print("🔍 Monitoraggio trade reali - DATABASE CORRETTO")
    
    while True:
        try:
            conn = sqlite3.connect('trading_performance.db')
            cursor = conn.cursor()
            
            # Verifica schema
            cursor.execute("PRAGMA table_info(trade_performance)")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"📋 Colonne database: {columns}")
            
            # Statistiche
            cursor.execute('''
            SELECT COUNT(*) as total_trades, 
                   AVG(pnl_percent) as avg_pnl,
                   SUM(CASE WHEN pnl_percent > 0 THEN 1 ELSE 0 END) as wins,
                   SUM(CASE WHEN pnl_percent <= 0 THEN 1 ELSE 0 END) as losses
            FROM trade_performance
            ''')
            
            result = cursor.fetchone()
            total_trades, avg_pnl, wins, losses = result
            
            # Ultimi trade
            cursor.execute('''
            SELECT symbol, action, quantity, entry_price, amount, timestamp, pnl_percent 
            FROM trade_performance 
            ORDER BY timestamp DESC LIMIT 10
            ''')
            recent_trades = cursor.fetchall()
            
            conn.close()
            
            print(f"\n📊 STATISTICHE REALI - {datetime.now().strftime('%H:%M:%S')}")
            print(f"   Trade totali: {total_trades}")
            print(f"   P&L medio: {avg_pnl:.2f}%" if avg_pnl is not None else "   P&L medio: 0%")
            print(f"   Win/Loss: {wins}/{losses}")
            
            if recent_trades:
                print("   Ultimi trade REALI:")
                for trade in recent_trades:
                    symbol, action, quantity, price, amount, timestamp, pnl = trade
                    print(f"     {action} {symbol} - {quantity:.6f} @ ${price:.2f} = ${amount:.2f} (P&L: {pnl:.2f}%)")
            else:
                print("   ⏳ Nessun trade registrato ancora...")
        
        except Exception as e:
            print(f"❌ Errore database: {e}")
            print("   🔧 Ricreazione database...")
            import subprocess
            subprocess.run(['python3', 'fix_database_schema.py'])
        
        print("-" * 50)
        time.sleep(10)

if __name__ == "__main__":
    monitor_real_trades_fixed()

import sqlite3
import time
from datetime import datetime

def monitor_real_trades():
    print("🔍 Monitoraggio trade reali nel database...")
    
    while True:
        conn = sqlite3.connect('trading_performance.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT COUNT(*) as total_trades, 
               AVG(pnl_percent) as avg_pnl,
               SUM(CASE WHEN pnl_percent > 0 THEN 1 ELSE 0 END) as wins,
               SUM(CASE WHEN pnl_percent <= 0 THEN 1 ELSE 0 END) as losses
        FROM trade_performance
        ''')
        
        result = cursor.fetchone()
        total_trades, avg_pnl, wins, losses = result
        
        cursor.execute('SELECT symbol, action, quantity, entry_price, timestamp FROM trade_performance ORDER BY timestamp DESC LIMIT 5')
        recent_trades = cursor.fetchall()
        
        conn.close()
        
        print(f"\n📊 STATISTICHE REALI - {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Trade totali: {total_trades}")
        print(f"   P&L medio: {avg_pnl:.2f}%" if avg_pnl else "   P&L medio: 0%")
        print(f"   Win/Loss: {wins}/{losses}")
        
        if recent_trades:
            print("   Ultimi trade:")
            for trade in recent_trades:
                symbol, action, quantity, price, timestamp = trade
                print(f"     {action} {symbol} - {quantity:.6f} @ ${price:.2f}")
        else:
            print("   Nessun trade registrato ancora...")
        
        time.sleep(10)

if __name__ == "__main__":
    monitor_real_trades()

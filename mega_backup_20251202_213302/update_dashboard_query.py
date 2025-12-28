import sqlite3

def update_dashboard_queries():
    """Aggiorna le query della dashboard per lo schema corretto"""
    
    with open('quantum_dashboard_compatible.py', 'r') as f:
        content = f.read()
    
    # Aggiorna la query per usare le colonne corrette
    old_query = '''
            cursor.execute('''
                SELECT COUNT(*), AVG(pnl_percent),
                SUM(CASE WHEN pnl_percent > 0 THEN 1 ELSE 0 END),
                SUM(CASE WHEN pnl_percent <= 0 THEN 1 ELSE 0 END)
                FROM trade_performance
            ''')'''
    
    new_query = '''
            cursor.execute('''
                SELECT COUNT(*), AVG(pnl_percent),
                SUM(CASE WHEN pnl_percent > 0 THEN 1 ELSE 0 END),
                SUM(CASE WHEN pnl_percent <= 0 THEN 1 ELSE 0 END)
                FROM trade_performance
            ''')'''
    
    # Aggiorna la query dei dati settimanali
    old_weekly_query = '''
            cursor.execute('''
                SELECT DATE(timestamp), AVG(pnl_percent)
                FROM trade_performance 
                WHERE timestamp >= datetime('now', '-7 days')
                GROUP BY DATE(timestamp)
                ORDER BY DATE(timestamp)
            ''')'''
    
    new_weekly_query = '''
            cursor.execute('''
                SELECT DATE(timestamp), AVG(pnl_percent)
                FROM trade_performance 
                WHERE timestamp >= datetime('now', '-7 days')
                GROUP BY DATE(timestamp)
                ORDER BY DATE(timestamp)
            ''')'''
    
    content = content.replace(old_query, new_query)
    content = content.replace(old_weekly_query, new_weekly_query)
    
    with open('quantum_dashboard_compatible.py', 'w') as f:
        f.write(content)
    
    print("✅ Query dashboard aggiornate")

update_dashboard_queries()

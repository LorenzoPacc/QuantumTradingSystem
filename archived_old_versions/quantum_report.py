#!/usr/bin/env python3
"""
Quantum Trading Systems - Performance Reporter
"""

import json
import sqlite3
from datetime import datetime, timedelta
import argparse

def load_state(version):
    """Carica stato sistema"""
    try:
        if version == 'v2':
            with open('quantum_v2_state.json', 'r') as f:
                return json.load(f)
        elif version == 'v3':
            with open('quantum_v3_state.json', 'r') as f:
                return json.load(f)
    except FileNotFoundError:
        return None

def get_db_stats(version):
    """Ottieni statistiche dal database"""
    db_name = "quantum_v2_performance.db" if version == 'v2' else "quantum_v3_performance.db"
    
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        
        # Total trades
        c.execute("SELECT COUNT(*) FROM trades")
        total_trades = c.fetchone()[0]
        
        # Profitable trades
        c.execute('''SELECT COUNT(*) FROM trades 
                     WHERE action='SELL' AND reason LIKE '%P&L: +%' ''')
        profitable_trades = c.fetchone()[0]
        
        # Recent trades
        c.execute('''SELECT symbol, action, price, reason, timestamp 
                     FROM trades ORDER BY timestamp DESC LIMIT 5''')
        recent_trades = c.fetchall()
        
        conn.close()
        
        return {
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'win_rate': (profitable_trades / total_trades * 100) if total_trades > 0 else 0,
            'recent_trades': recent_trades
        }
    except sqlite3.Error:
        return None

def generate_report():
    """Genera report comparativo"""
    print("\n📊 QUANTUM TRADING SYSTEMS - PERFORMANCE REPORT")
    print("=" * 50)
    
    # V2.1 Report
    print("\n🤖 V2.1 LIVE SYSTEM:")
    v2_state = load_state('v2')
    if v2_state:
        cash = v2_state.get('cash_balance', 0)
        portfolio = v2_state.get('portfolio', {})
        positions = len(portfolio)
        total_value = cash + sum(pos.get('total_cost', 0) for pos in portfolio.values())
        roi = ((total_value - 200) / 200) * 100
        
        print(f"   💰 Total Value: ${total_value:.2f}")
        print(f"   📈 ROI: {roi:+.2f}%")
        print(f"   💵 Cash: ${cash:.2f}")
        print(f"   📊 Positions: {positions}")
        print(f"   🔄 Cycles: {v2_state.get('cycle_count', 0)}")
        
        v2_stats = get_db_stats('v2')
        if v2_stats:
            print(f"   📊 Trades: {v2_stats['total_trades']}")
            print(f"   ✅ Win Rate: {v2_stats['win_rate']:.1f}%")
    else:
        print("   ❌ No data available")
    
    # V3.0 Report  
    print("\n🤖 V3.0 MVP SYSTEM:")
    v3_state = load_state('v3')
    if v3_state:
        cash = v3_state.get('cash_balance', 0)
        portfolio = v3_state.get('portfolio', {})
        positions = len(portfolio)
        
        # Calculate current portfolio value
        portfolio_value = 0
        for symbol, pos in portfolio.items():
            portfolio_value += pos.get('total_cost', 0)
        
        total_value = cash + portfolio_value
        roi = ((total_value - 200) / 200) * 100
        
        print(f"   💰 Total Value: ${total_value:.2f}")
        print(f"   📈 ROI: {roi:+.2f}%") 
        print(f"   💵 Cash: ${cash:.2f}")
        print(f"   📊 Positions: {positions}")
        print(f"   🔄 Cycles: {v3_state.get('cycle_count', 0)}")
        print(f"   🎯 Portfolio Value: ${portfolio_value:.2f}")
        
        v3_stats = get_db_stats('v3')
        if v3_stats:
            print(f"   📊 Trades: {v3_stats['total_trades']}")
            print(f"   ✅ Win Rate: {v3_stats['win_rate']:.1f}%")
            
            if v3_stats['recent_trades']:
                print(f"\n   📈 Recent Trades:")
                for trade in v3_stats['recent_trades'][:3]:
                    symbol, action, price, reason, timestamp = trade
                    print(f"      {action} {symbol} @ ${price:.2f} - {reason[:30]}...")
    else:
        print("   ❌ No data available")
    
    print("\n" + "=" * 50)
    print("💡 Next report: python3 quantum_report.py")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Quantum Systems Reporter')
    parser.add_argument('--continuous', action='store_true', help='Continuous monitoring')
    args = parser.parse_args()
    
    if args.continuous:
        import time
        while True:
            generate_report()
            print("\n⏳ Next update in 300 seconds...\n")
            time.sleep(300)
    else:
        generate_report()

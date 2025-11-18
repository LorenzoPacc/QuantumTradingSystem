#!/usr/bin/env python3
"""
QUANTUM V3 - STATE RECOVERY CORRETTO
Usa lo schema reale del database: action invece di side
"""

import json
import sqlite3
import os
from datetime import datetime

def recover_portfolio_state():
    print("🔄 SISTEMA DI RECOVERY - SCHEMA CORRETTO")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('quantum_v2_performance.db')
        cursor = conn.cursor()
        
        # Query con schema corretto
        query = 'SELECT timestamp, symbol, action, price, quantity, total_value FROM trades ORDER BY timestamp'
        cursor.execute(query)
        trades = cursor.fetchall()
        
        print(f"📊 Analizzando {len(trades)} trade storici...")
        
        # Calcola stato reale
        initial_capital = 10000.0
        cash_balance = initial_capital
        portfolio = {}
        
        for trade in trades:
            timestamp, symbol, action, price, quantity, total_value = trade
            
            if action.upper() == 'BUY':
                # ACQUISTO
                cash_balance -= total_value
                portfolio[symbol] = {
                    'quantity': quantity,
                    'entry_price': price,
                    'invested_amount': total_value
                }
                print(f"   🟢 BUY {symbol}: ${total_value:.2f} @ ${price:.3f}")
                
            elif action.upper() == 'SELL':
                # VENDITA
                cash_balance += total_value
                if symbol in portfolio:
                    del portfolio[symbol]
                print(f"   🔴 SELL {symbol}: ${total_value:.2f} @ ${price:.3f}")
        
        # Calcola valore totale
        portfolio_value = cash_balance
        for symbol, position in portfolio.items():
            portfolio_value += position['invested_amount']
        
        print("=" * 50)
        print(f"💰 STATO REALE CALCOLATO:")
        print(f"   💵 Cash: ${cash_balance:.2f}")
        print(f"   📈 Posizioni attive: {len(portfolio)}")
        for symbol, pos in portfolio.items():
            print(f"      • {symbol}: ${pos['invested_amount']:.2f} ({pos['quantity']} units)")
        print(f"   💎 Valore totale: ${portfolio_value:.2f}")
        print(f"   📉 P&L Totale: ${portfolio_value - initial_capital:.2f}")
        
        # Crea stato recuperato
        recovered_state = {
            "portfolio_value": portfolio_value,
            "cash_balance": cash_balance,
            "portfolio": portfolio,
            "fear_greed_index": 45,
            "cycle_count": len(trades),
            "total_trades": len(trades),
            "daily_pnl": 0.0,
            "total_pnl": portfolio_value - initial_capital,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "V3_RECOVERED_CORRECT",
            "recovery_note": f"Recovered from {len(trades)} trades using correct schema"
        }
        
        # Backup file corrente
        if os.path.exists('quantum_v2_state.json'):
            os.rename('quantum_v2_state.json', f"backup_pre_recovery_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
        
        # Salva stato recuperato
        with open('quantum_v2_state.json', 'w') as f:
            json.dump(recovered_state, f, indent=2)
            
        print("✅ PORTAFOGLIO RECUPERATO CON SUCCESSO!")
        return recovered_state
        
    except Exception as e:
        print(f"❌ Errore recovery: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = recover_portfolio_state()
    if result:
        print(f"🎯 Recovery completato! Portafoglio: ${result['portfolio_value']:.2f}")
        print(f"📊 Dovrebbe essere circa $194 (come prima del crash)")
    else:
        print("💥 Recovery fallito")

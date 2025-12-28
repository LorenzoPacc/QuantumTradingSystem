#!/usr/bin/env python3
"""
QUANTUM V3 - STATE RECOVERY SYSTEM
Ripristina lo stato reale dal database dei trade
"""

import json
import sqlite3
import os
from datetime import datetime

def recover_portfolio_state():
    print("🔄 SISTEMA DI RECOVERY PORTAFOGLIO ATTIVATO")
    print("=" * 50)
    
    # Stato corrente (potenzialmente corrotto)
    current_state = {}
    if os.path.exists('quantum_v2_state.json'):
        try:
            with open('quantum_v2_state.json', 'r') as f:
                current_state = json.load(f)
            print(f"📁 Stato corrente: ${current_state.get('portfolio_value', 0):.2f}")
        except:
            print("❌ File state corrotto - Ricostruzione completa")
    
    # Calcola stato reale dal database
    initial_capital = 10000.0
    real_portfolio_value = initial_capital
    portfolio = {}
    cash_balance = initial_capital
    
    try:
        conn = sqlite3.connect('quantum_v2_performance.db')
        cursor = conn.cursor()
        
        # Recupera tutti i trade
        cursor.execute('SELECT timestamp, symbol, operation_type, quantity, price, invested_amount FROM trades ORDER BY timestamp')
        trades = cursor.fetchall()
        
        print(f"📊 Analizzando {len(trades)} trade storici...")
        
        # Mappa operation_type a side (BUY/SELL)
        type_to_side = {'LONG': 'BUY', 'CLOSE_LONG': 'SELL'}
        
        for trade in trades:
            timestamp, symbol, op_type, quantity, price, invested = trade
            side = type_to_side.get(op_type, op_type)
            
            if side == 'BUY':
                # Acquisto: riduci cash, aggiungi posizione
                cash_balance -= invested
                portfolio[symbol] = {
                    'quantity': quantity,
                    'entry_price': price,
                    'invested_amount': invested
                }
                print(f"   🟢 BUY {symbol}: ${invested:.2f} @ ${price:.3f}")
                
            elif side == 'SELL':
                # Vendita: aumenta cash, rimuovi posizione
                cash_balance += invested
                if symbol in portfolio:
                    del portfolio[symbol]
                print(f"   🔴 SELL {symbol}: ${invested:.2f} @ ${price:.3f}")
        
        # Calcola valore totale portafoglio
        real_portfolio_value = cash_balance
        for symbol, position in portfolio.items():
            real_portfolio_value += position['invested_amount']
            
        print("=" * 50)
        print(f"💰 STATO REALE CALCOLATO:")
        print(f"   💵 Cash: ${cash_balance:.2f}")
        print(f"   📈 Posizioni attive: {len(portfolio)}")
        for symbol, pos in portfolio.items():
            print(f"      • {symbol}: ${pos['invested_amount']:.2f}")
        print(f"   💎 Valore totale: ${real_portfolio_value:.2f}")
        print(f"   📉 P&L Totale: ${real_portfolio_value - initial_capital:.2f}")
        
        # Ricrea stato corretto
        recovered_state = {
            "portfolio_value": real_portfolio_value,
            "cash_balance": cash_balance,
            "portfolio": portfolio,
            "fear_greed_index": current_state.get('fear_greed_index', 45),
            "cycle_count": current_state.get('cycle_count', len(trades)),
            "total_trades": len(trades),
            "daily_pnl": current_state.get('daily_pnl', 0.0),
            "total_pnl": real_portfolio_value - initial_capital,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "V3_RECOVERED_STATE",
            "recovery_note": f"Recovered from {len(trades)} trades on {datetime.now()}"
        }
        
        # Backup del file corrotto
        if os.path.exists('quantum_v2_state.json'):
            os.rename('quantum_v2_state.json', f"backup_corrupted_state_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
        
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
    else:
        print("💥 Recovery fallito - Ripristino a $10,000")
        # Ripristino di emergenza
        emergency_state = {
            "portfolio_value": 10000.0,
            "cash_balance": 10000.0,
            "portfolio": {},
            "fear_greed_index": 45,
            "cycle_count": 0,
            "total_trades": 0,
            "daily_pnl": 0.0,
            "total_pnl": 0.0,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "V3_EMERGENCY_RECOVERY"
        }
        with open('quantum_v2_state.json', 'w') as f:
            json.dump(emergency_state, f, indent=2)
        print("✅ Ripristino emergenza a $10,000 completato")

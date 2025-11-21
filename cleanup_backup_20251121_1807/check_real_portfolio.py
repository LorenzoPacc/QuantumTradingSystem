#!/usr/bin/env python3
"""
💰 CONTROLLO PORTAFOGLIO REALE
Stessi dati della dashboard live
"""

from quantum_real_perfect import RealBinanceAPI

def check_real_portfolio():
    print('🎯 PORTAFOGLIO REALE (Dashboard Data)')
    print('====================================')
    
    # STESSI DATI della dashboard
    entries = {
        'BTCUSDT': 101727.24, 'ETHUSDT': 3384.81, 
        'SOLUSDT': 157.43, 'AVAXUSDT': 17.29, 
        'LINKUSDT': 15.33, 'DOTUSDT': 3.172
    }
    
    quantities = {
        'BTCUSDT': 0.000442359, 'ETHUSDT': 0.013294690,
        'SOLUSDT': 0.273550149, 'AVAXUSDT': 1.515618999, 
        'LINKUSDT': 1.040167935, 'DOTUSDT': 3.152585120
    }
    
    cash = 14.78
    initial_investment = 200.0
    
    api = RealBinanceAPI()
    total_value = cash
    
    print(f'💵 Cash: ${cash}')
    print('📈 Posizioni:')
    print('------------')
    
    for symbol in entries:
        current_price = api.get_real_price(symbol)
        if current_price:
            entry = entries[symbol]
            qty = quantities[symbol]
            value = qty * current_price
            pnl_pct = ((current_price - entry) / entry) * 100
            
            total_value += value
            
            print(f'🔸 {symbol}:')
            print(f'   Qty: {qty:.6f}')
            print(f'   Entry: ${entry:,.2f}')
            print(f'   Current: ${current_price:,.2f}')
            print(f'   Value: ${value:.2f}')
            print(f'   P&L: {pnl_pct:+.2f}%')
            print()
    
    profit = total_value - initial_investment
    profit_pct = (profit / initial_investment) * 100
    
    print('💎 RIEPILOGO:')
    print('------------')
    print(f'💰 Investito: ${initial_investment}')
    print(f'📊 Valore attuale: ${total_value:.2f}')
    print(f'🎯 Profitto: ${profit:+.2f} ({profit_pct:+.2f}%)')
    print(f'📈 Posizioni: {len(entries)}')
    print(f'💵 Cash: ${cash}')
    print()
    print('✅ TIPO: SPOT TRADING')
    print('   - Asset reali posseduti')
    print('   - Nessun leverage')
    print('   - Nessun futures')

if __name__ == "__main__":
    check_real_portfolio()

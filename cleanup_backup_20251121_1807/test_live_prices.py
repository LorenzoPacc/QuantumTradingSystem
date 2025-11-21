#!/usr/bin/env python3
"""
Test prezzi live da Binance
"""
import requests
import json
from datetime import datetime

def test_binance_prices():
    print("🧪 TEST PREZZI LIVE DA BINANCE")
    print("=" * 40)
    
    symbols = ['DOTUSDT', 'BTCUSDT', 'ETHUSDT']
    
    for symbol in symbols:
        try:
            url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                price = float(data['price'])
                print(f"✅ {symbol}: ${price:.3f}")
            else:
                print(f"❌ {symbol}: Errore API ({response.status_code})")
                
        except requests.exceptions.Timeout:
            print(f"❌ {symbol}: Timeout")
        except requests.exceptions.ConnectionError:
            print(f"❌ {symbol}: Errore connessione")
        except Exception as e:
            print(f"❌ {symbol}: Errore - {e}")

def check_current_portfolio():
    print("\n📊 ANALISI PORTAFOGLIO ATTUALE:")
    print("=" * 40)
    
    try:
        with open('quantum_v2_state.json', 'r') as f:
            data = json.load(f)
        
        cash = data['cash_balance']
        positions = data['portfolio']
        total_static = data['portfolio_value']
        
        print(f"💵 Cash: ${cash:.2f}")
        print(f"📈 Posizioni: {len(positions)}")
        
        # Calcola totale con prezzi live
        total_live = cash
        for sym, pos in positions.items():
            cost = pos['total_cost']
            quantity = pos['quantity']
            entry = pos['entry_price']
            
            # Ottieni prezzo live
            try:
                url = f'https://api.binance.com/api/v3/ticker/price?symbol={sym}'
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    current_price = float(response.json()['price'])
                    current_value = quantity * current_price
                    pnl_pct = ((current_price - entry) / entry) * 100
                    
                    print(f"   🟢 {sym}:")
                    print(f"      - Investito: ${cost:.2f}")
                    print(f"      - Entry: ${entry:.3f}")
                    print(f"      - Live: ${current_price:.3f}")
                    print(f"      - P&L: {pnl_pct:+.2f}%")
                    
                    total_live += current_value
                else:
                    print(f"   ⚠️  {sym}: Prezzo non disponibile")
                    total_live += cost
            except:
                print(f"   ⚠️  {sym}: Errore prezzo")
                total_live += cost
        
        pnl_live = ((total_live - 200) / 200) * 100
        pnl_static = ((total_static - 200) / 200) * 100
        
        print(f"\n💰 CONFRONTO:")
        print(f"   Statico: ${total_static:.2f} ({pnl_static:+.2f}%)")
        print(f"   Live: ${total_live:.2f} ({pnl_live:+.2f}%)")
        print(f"   Differenza: ${(total_live - total_static):+.2f}")
        
    except Exception as e:
        print(f"❌ Errore lettura file: {e}")

if __name__ == "__main__":
    test_binance_prices()
    check_current_portfolio()

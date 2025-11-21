#!/usr/bin/env python3
"""
SINCRONIZZAZIONE COMPLETA: Allinea DB con Binance
"""
import requests
import hmac
import hashlib
import time
import sqlite3
from datetime import datetime

api_key = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
api_secret = "yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"

print("🔄 SINCRONIZZAZIONE COMPLETA DATABASE")
print("="*60)

# 1. Ottieni balance reale da Binance
def get_binance_balance():
    timestamp = int(time.time() * 1000)
    query_string = f"timestamp={timestamp}"
    signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    
    url = f"https://testnet.binance.vision/api/v3/account?{query_string}&signature={signature}"
    headers = {"X-MBX-APIKEY": api_key}
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    balances = {
        'USDT': next((float(b['free']) for b in data['balances'] if b['asset'] == 'USDT'), 0),
        'ETH': next((float(b['free']) for b in data['balances'] if b['asset'] == 'ETH'), 0),
        'SOL': next((float(b['free']) for b in data['balances'] if b['asset'] == 'SOL'), 0),
    }
    return balances

# 2. Ottieni tutti i trade da Binance
def get_binance_trades(symbol):
    timestamp = int(time.time() * 1000)
    query_string = f"symbol={symbol}&timestamp={timestamp}"
    signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    
    url = f"https://testnet.binance.vision/api/v3/myTrades?{query_string}&signature={signature}"
    headers = {"X-MBX-APIKEY": api_key}
    
    response = requests.get(url, headers=headers)
    return response.json()

print("\n📡 STEP 1: Recupero dati da Binance...")

# Balance reali
real_balances = get_binance_balance()
print(f"\n💰 BALANCE REALI:")
print(f"   USDT: ${real_balances['USDT']:.2f}")
print(f"   ETH: {real_balances['ETH']:.4f}")
print(f"   SOL: {real_balances['SOL']:.4f}")

# Trade history completa
print(f"\n📊 TRADE HISTORY DA BINANCE:")
all_trades = {}
for symbol in ['ETHUSDT', 'SOLUSDT']:
    trades = get_binance_trades(symbol)
    all_trades[symbol] = trades
    print(f"   {symbol}: {len(trades)} trade totali")

# 3. Aggiorna database
print(f"\n💾 STEP 2: Aggiornamento database locale...")

conn = sqlite3.connect('quantum_final.db')
cursor = conn.cursor()

# Chiudi tutti i trade "OPEN" come "AUTO_CLOSED"
cursor.execute("UPDATE trades SET status='AUTO_CLOSED' WHERE status='OPEN'")
closed_trades = cursor.rowcount
print(f"   ✅ Chiusi {closed_trades} trade obsoleti")

# Inserisci balance aggiornato
cursor.execute(
    "INSERT INTO balance_history (balance, timestamp) VALUES (?, ?)",
    (real_balances['USDT'], datetime.now())
)
print(f"   ✅ Balance aggiornato a ${real_balances['USDT']:.2f}")

# Aggiungi i trade mancanti (le vendite manuali)
print(f"\n📥 STEP 3: Importazione trade mancanti...")

trades_imported = 0
for symbol, trades in all_trades.items():
    for trade in trades[-10:]:  # Ultimi 10 per symbol
        trade_id = trade['id']
        
        # Verifica se già nel DB
        cursor.execute("SELECT id FROM trades WHERE symbol=? AND timestamp=?", 
                      (symbol, datetime.fromtimestamp(trade['time']/1000)))
        
        if cursor.fetchone() is None:
            side = "BUY" if trade['isBuyer'] else "SELL"
            quantity = float(trade['qty'])
            price = float(trade['price'])
            
            cursor.execute('''
                INSERT INTO trades (symbol, side, quantity, entry_price, timestamp, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (symbol, side, quantity, price, datetime.fromtimestamp(trade['time']/1000), 'CLOSED'))
            
            trades_imported += 1
            print(f"   📥 Importato: {symbol} {side} {quantity} @ ${price}")

print(f"   ✅ Importati {trades_imported} trade mancanti")

conn.commit()
conn.close()

print("\n" + "="*60)
print("✅ SINCRONIZZAZIONE COMPLETATA!")
print(f"💰 Balance corrente: ${real_balances['USDT']:.2f}")
print(f"🎯 Sistema pronto per operare correttamente")

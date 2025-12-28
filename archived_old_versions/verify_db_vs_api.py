#!/usr/bin/env python3
import requests
import hmac
import hashlib
import time
import sqlite3

api_key = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
api_secret = "yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"

print("🔍 CONFRONTO DATABASE vs API BINANCE")
print("="*50)

# 1. Balance da API
timestamp = int(time.time() * 1000)
query_string = f"timestamp={timestamp}"
signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

url = f"https://testnet.binance.vision/api/v3/account?{query_string}&signature={signature}"
headers = {"X-MBX-APIKEY": api_key}

response = requests.get(url, headers=headers)
data = response.json()

usdt_api = next((float(b['free']) for b in data['balances'] if b['asset'] == 'USDT'), 0)
eth_api = next((float(b['free']) for b in data['balances'] if b['asset'] == 'ETH'), 0)
sol_api = next((float(b['free']) for b in data['balances'] if b['asset'] == 'SOL'), 0)

print(f"\n📡 BALANCE DA API BINANCE:")
print(f"   USDT: ${usdt_api:.2f}")
print(f"   ETH: {eth_api:.4f}")
print(f"   SOL: {sol_api:.4f}")

# 2. Balance da Database locale
try:
    conn = sqlite3.connect('quantum_final.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT balance FROM balance_history ORDER BY timestamp DESC LIMIT 1")
    db_balance = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) FROM trades WHERE status='OPEN'")
    open_trades = cursor.fetchone()[0]
    
    print(f"\n💾 DATI DA DATABASE LOCALE:")
    print(f"   Ultimo balance salvato: ${db_balance[0] if db_balance else 0:.2f}")
    print(f"   Trade aperti registrati: {open_trades}")
    
    # Mostra ultimi trade
    cursor.execute("SELECT symbol, side, quantity, entry_price, timestamp FROM trades ORDER BY timestamp DESC LIMIT 5")
    trades = cursor.fetchall()
    
    print(f"\n📊 ULTIMI 5 TRADE NEL DB:")
    for trade in trades:
        print(f"   {trade[0]} {trade[1]} {trade[2]} @ ${trade[3]} - {trade[4]}")
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ Errore database: {e}")

# 3. Trade history da Binance
print(f"\n📈 TRADE HISTORY REALE DA BINANCE:")
for symbol in ['ETHUSDT', 'SOLUSDT']:
    timestamp = int(time.time() * 1000)
    query_string = f"symbol={symbol}&timestamp={timestamp}"
    signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    
    url = f"https://testnet.binance.vision/api/v3/myTrades?{query_string}&signature={signature}"
    headers = {"X-MBX-APIKEY": api_key}
    
    response = requests.get(url, headers=headers)
    trades = response.json()
    
    print(f"\n   {symbol}: {len(trades)} trade totali")
    if len(trades) > 0:
        last_trade = trades[-1]
        side = "BUY" if last_trade['isBuyer'] else "SELL"
        print(f"   Ultimo: {side} {last_trade['qty']} @ ${last_trade['price']}")

print("\n" + "="*50)
print("🎯 ANALISI COMPLETATA")

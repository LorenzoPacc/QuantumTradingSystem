#!/usr/bin/env python3
"""
VERIFICA SINCRONIZZAZIONE DATABASE
"""
import sqlite3
import requests
import hmac
import hashlib
import time
from datetime import datetime

api_key = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
api_secret = "yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"

print("🔍 VERIFICA SINCRONIZZAZIONE")
print("="*50)

# 1. Balance da Binance
timestamp = int(time.time() * 1000)
query_string = f"timestamp={timestamp}"
signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

url = f"https://testnet.binance.vision/api/v3/account?{query_string}&signature={signature}"
headers = {"X-MBX-APIKEY": api_key}

response = requests.get(url, headers=headers)
data = response.json()
usdt_balance = next((float(b['free']) for b in data['balances'] if b['asset'] == 'USDT'), 0)

print(f"📡 BINANCE API: ${usdt_balance:.2f}")

# 2. Balance dal database
conn = sqlite3.connect('quantum_final.db')
cursor = conn.cursor()

cursor.execute("SELECT balance FROM balance_history ORDER BY timestamp DESC LIMIT 1")
db_balance = cursor.fetchone()[0] if cursor.fetchone() else 0

print(f"💾 DATABASE: ${db_balance:.2f}")

# 3. Trade nel database
cursor.execute("SELECT COUNT(*) FROM trades")
total_trades = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM trades WHERE status='OPEN'")
open_trades = cursor.fetchone()[0]

print(f"📊 TRADE NEL DB: {total_trades} totali, {open_trades} aperti")

# 4. Ultimi trade
cursor.execute("SELECT symbol, side, quantity, entry_price, timestamp FROM trades ORDER BY timestamp DESC LIMIT 5")
print(f"\n🕒 ULTIMI 5 TRADE:")
for trade in cursor.fetchall():
    print(f"   {trade[0]} {trade[1]} {trade[2]} @ ${trade[3]:.2f} - {trade[4]}")

conn.close()

# 5. Verifica sincronizzazione
if abs(usdt_balance - db_balance) < 1.0:
    print(f"\n✅ SINCRONIZZAZIONE PERFETTA! (Differenza: ${abs(usdt_balance - db_balance):.2f})")
else:
    print(f"\n❌ PROBLEMA SINCRONIZZAZIONE! (Differenza: ${abs(usdt_balance - db_balance):.2f})")

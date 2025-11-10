import requests

print("🔍 VERIFICA PREZZI REALI vs SIMULATI\n")

symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT', 'LINKUSDT', 'DOTUSDT']
entries = {
    'BTCUSDT': 101727.24,
    'ETHUSDT': 3384.81,
    'SOLUSDT': 157.43,
    'AVAXUSDT': 17.29,
    'LINKUSDT': 15.33,
    'DOTUSDT': 3.172
}

print("📊 PREZZI REALI ATTUALI:")
total_value_real = 0
costs = {
    'BTCUSDT': 45.00,
    'ETHUSDT': 45.00,
    'SOLUSDT': 43.07,
    'AVAXUSDT': 26.21,
    'LINKUSDT': 15.95,
    'DOTUSDT': 10.00
}

for symbol in symbols:
    r = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}')
    current = float(r.json()['price'])
    entry = entries[symbol]
    change = ((current - entry) / entry) * 100
    
    # Calcola valore attuale della posizione
    quantity = costs[symbol] / entry
    current_value = quantity * current
    pnl = current_value - costs[symbol]
    
    status = "🔴" if change < -4 else "🟡" if change < 0 else "🟢"
    print(f"{status} {symbol}: ${current:,.2f} ({change:+.2f}%) | Value: ${current_value:.2f} (PnL: ${pnl:+.2f})")
    
    total_value_real += current_value

print(f"\n💎 VALORE REALE PORTFOLIO: ${total_value_real:.2f}")
print(f"💵 + Cash: $14.78")
print(f"💰 TOTALE REALE: ${total_value_real + 14.78:.2f}")
print(f"📊 Performance REALE: ${total_value_real + 14.78 - 200:.2f} ({((total_value_real + 14.78 - 200) / 200 * 100):.2f}%)")

print(f"\n🚨 BOT MOSTRA: $185.52 (-7.2%)")
print(f"✅ REALTÀ SAREBBE: ${total_value_real + 14.78:.2f}")
print(f"❌ DIFFERENZA: ${185.52 - (total_value_real + 14.78):.2f}")

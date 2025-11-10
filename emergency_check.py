import requests
from quantum_ultimate_fixed import QuantumTraderUltimateFixed
import json

print("🚨 EMERGENCY CHECK - PREZZI REALI vs BOT\n")

# Carica portfolio bot
with open('portfolio_backup.json', 'r') as f:
    bot_data = json.load(f)

t = QuantumTraderUltimateFixed(200)
t.cash_balance = bot_data['cash_balance']
t.portfolio = bot_data['portfolio']

print("🤖 BOT STATUS:")
bot_value = t.get_portfolio_value()
print(f"   Portfolio: ${bot_value:.2f}")
print(f"   Cash: ${t.cash_balance:.2f}")
print(f"   Totale: ${bot_value + t.cash_balance:.2f}")

print("\n🔍 PREZZI REALI BINANCE:")
symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT', 'LINKUSDT', 'DOTUSDT']
entries = {
    'BTCUSDT': 101727.24, 'ETHUSDT': 3384.81, 'SOLUSDT': 157.43,
    'AVAXUSDT': 17.29, 'LINKUSDT': 15.33, 'DOTUSDT': 3.172
}
costs = {
    'BTCUSDT': 45.00, 'ETHUSDT': 45.00, 'SOLUSDT': 43.07,
    'AVAXUSDT': 26.21, 'LINKUSDT': 15.95, 'DOTUSDT': 10.00
}

total_real = 0
for symbol in symbols:
    # Prezzo reale
    r = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}')
    real_price = float(r.json()['price'])
    
    # Prezzo bot (simulato)
    bot_price = t.market_data.get_real_price(symbol)
    
    # Calcoli
    entry = entries[symbol]
    real_change = ((real_price - entry) / entry) * 100
    bot_change = ((bot_price - entry) / entry) * 100
    
    quantity = costs[symbol] / entry
    real_value = quantity * real_price
    
    total_real += real_value
    
    print(f"\n{symbol}:")
    print(f"   📊 Reale: ${real_price:,.2f} ({real_change:+.2f}%)")
    print(f"   🤖 Bot:   ${bot_price:,.2f} ({bot_change:+.2f}%)")
    print(f"   💰 Valore: ${real_value:.2f}")

print(f"\n🚨 DIFFERENZE CRITICHE:")
print(f"   💎 Valore REALE: ${total_real:.2f}")
print(f"   🤖 Valore BOT: ${bot_value:.2f}") 
print(f"   ❌ Differenza: ${total_real - bot_value:.2f}")

print(f"\n💰 TOTALE REALE: ${total_real + 14.78:.2f}")
print(f"📊 Performance REALE: {((total_real + 14.78 - 200) / 200 * 100):+.2f}%")
print(f"🤖 Performance BOT: {((bot_value + 14.78 - 200) / 200 * 100):+.2f}%")

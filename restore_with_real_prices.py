from quantum_real_perfect import QuantumTraderPerfect

print("🔄 RIPRISTINO PORTFOLIO CON PREZZI REALI\n")

trader = QuantumTraderPerfect(200)

# Ripristina posizioni
trader.portfolio = {
    'BTCUSDT': {'quantity': 0.000442359, 'entry_price': 101727.24},
    'ETHUSDT': {'quantity': 0.013294690, 'entry_price': 3384.81},
    'SOLUSDT': {'quantity': 0.273550149, 'entry_price': 157.43},
    'AVAXUSDT': {'quantity': 1.515618999, 'entry_price': 17.29},
    'LINKUSDT': {'quantity': 1.040167935, 'entry_price': 15.33},
    'DOTUSDT': {'quantity': 3.152585120, 'entry_price': 3.172}
}
trader.cash_balance = 14.78

print("✅ Portfolio ripristinato\n")

# Calcola valore REALE
real_value = trader.get_portfolio_value()
profit = real_value - 200
profit_pct = (profit / 200) * 100

print(f"💎 Valore REALE: ${real_value:.2f}")
print(f"📊 Profit REALE: ${profit:+.2f} ({profit_pct:+.2f}%)\n")

# Mostra posizioni con prezzi REALI
print("📈 POSIZIONI CON PREZZI REALI:")
for symbol, pos in trader.portfolio.items():
    price = trader.market_api.get_real_price(symbol)
    pnl = ((price - pos['entry_price']) / pos['entry_price']) * 100
    value = pos['quantity'] * price
    status = "🟢" if pnl >= 0 else "🔴"
    print(f"{status} {symbol}: ${value:.2f} ({pnl:+.2f}%)")

print("\n🎯 AVVIO BOT CON POSIZIONI REALI...")
trader.run_continuous_trading(cycles=100, delay=600)

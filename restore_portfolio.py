from quantum_ultimate_fixed import QuantumTraderUltimateFixed
import json

print("🔄 RICOSTRUZIONE PORTFOLIO REALE...")

# Crea trader
t = QuantumTraderUltimateFixed(200)

# Portfolio reale dai dati della dashboard
portfolio_reale = {
    'BTCUSDT': {
        'quantity': 0.00044235939164377207,
        'entry_price': 101727.24,
        'total_cost': 45.00
    },
    'ETHUSDT': {
        'quantity': 0.013294690100773752, 
        'entry_price': 3384.81,
        'total_cost': 45.00
    },
    'SOLUSDT': {
        'quantity': 0.27355014927269267,
        'entry_price': 157.43,
        'total_cost': 43.07
    },
    'AVAXUSDT': {
        'quantity': 1.5156189994216311,
        'entry_price': 17.29,
        'total_cost': 26.21
    },
    'LINKUSDT': {
        'quantity': 1.0401679351761253,
        'entry_price': 15.33,
        'total_cost': 15.95
    },
    'DOTUSDT': {
        'quantity': 3.152585119798234,
        'entry_price': 3.172,
        'total_cost': 10.00
    }
}

# Imposta portfolio e cash
t.portfolio = portfolio_reale
t.cash_balance = 14.78

print("✅ PORTFOLIO RICOSTRUITO!")
print(f"💰 Valore totale: ${t.get_portfolio_value():.2f}")
print(f"💸 Cash: ${t.cash_balance:.2f}")
print(f"📈 Posizioni: {len(t.portfolio)}")

# Salva stato per riuso
portfolio_data = {
    'cash_balance': t.cash_balance,
    'portfolio': t.portfolio,
    'cycle_count': 115  # Riprendi dal ciclo 115
}

with open('portfolio_backup.json', 'w') as f:
    json.dump(portfolio_data, f, indent=2)

print("💾 Backup salvato in portfolio_backup.json")

# Test stop loss
print("\n🔍 VERIFICA STOP LOSS:")
for symbol, pos in t.portfolio.items():
    price = t.market_data.get_real_price(symbol)
    pnl = ((price - pos['entry_price']) / pos['entry_price']) * 100
    status = '🔴 VENDERA' if pnl <= -4 else '🟡 OK' if pnl < 0 else '🟢 OK'
    print(f"   {status} {symbol}: {pnl:.2f}%")

# Test funzione stop loss
print(f"\n🧪 TEST STOP LOSS FUNCTION:")
result = t.check_and_execute_exits()
print(f"📊 Vendite eseguite: {result}")

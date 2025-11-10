import requests
from quantum_ultimate_fixed import QuantumTraderUltimateFixed
import json

print("🚨 INVESTIGAZIONE FINALE - BUG PREZZI FAKE\n")

# Carica stato bot
with open('portfolio_backup.json', 'r') as f:
    bot_data = json.load(f)

t = QuantumTraderUltimateFixed(200)
t.cash_balance = bot_data['cash_balance']
t.portfolio = bot_data['portfolio']

print("📊 CONFRONTO PREZZI REALI vs FAKE:\n")

symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT', 'LINKUSDT', 'DOTUSDT']
entries = {
    'BTCUSDT': 101727.24, 'ETHUSDT': 3384.81, 'SOLUSDT': 157.43,
    'AVAXUSDT': 17.29, 'LINKUSDT': 15.33, 'DOTUSDT': 3.172
}

fake_dump_detected = False

for symbol in symbols:
    # Prezzo reale Binance
    r = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}', timeout=5)
    real_price = float(r.json()['price'])
    
    # Prezzo fake del bot
    fake_price = t.market_data.get_real_price(symbol)
    
    entry = entries[symbol]
    real_pnl = ((real_price - entry) / entry) * 100
    fake_pnl = ((fake_price - entry) / entry) * 100
    
    # Verifica se fake price causa stop loss ingiustificato
    if real_pnl > -3 and fake_pnl <= -4:
        fake_dump_detected = True
        print(f"🚨 BUG RILEVATO: {symbol}")
        print(f"   📊 Reale: ${real_price:,.2f} ({real_pnl:+.2f}%) → NO STOP LOSS")
        print(f"   🤖 Fake:  ${fake_price:,.2f} ({fake_pnl:+.2f}%) → STOP LOSS ATTIVATO!")
    else:
        print(f"✅ {symbol}: Reale ${real_price:,.2f} ({real_pnl:+.2f}%) | Fake ${fake_price:,.2f} ({fake_pnl:+.2f}%)")

if fake_dump_detected:
    print(f"\n❌ PROBLEMA CONFERMATO: Il bot usa prezzi FAKE!")
    print(f"🎯 Mercato REALE: TUTTI gli asset sono POSITIVI o poco negativi")
    print(f"🤖 Bot FAKE: Alcuni asset mostrano dump fittizi")
    print(f"💰 Conseguenza: Stop loss triggerato INGIUSTAMENTE!")
else:
    print(f"\n✅ Nessun bug rilevato - prezzi allineati")

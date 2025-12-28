print("🔍 VERIFICA DETTAGLIATA PERDITA\n")

# Posizioni iniziali
positions_initial = {
    'BTCUSDT': {'cost': 45.00, 'entry': 101727.24},
    'ETHUSDT': {'cost': 45.00, 'entry': 3384.81},
    'SOLUSDT': {'cost': 43.07, 'entry': 157.43},
    'AVAXUSDT': {'cost': 26.21, 'entry': 17.29},
    'LINKUSDT': {'cost': 15.95, 'entry': 15.33},
    'DOTUSDT': {'cost': 10.00, 'entry': 3.172}
}

total_invested = sum(p['cost'] for p in positions_initial.values())
print(f"💰 Investito totale: ${total_invested:.2f}")
print(f"💵 Cash iniziale dopo acquisti: $14.78")
print(f"💎 Capitale totale: $200.00\n")

# Simula vendite a -4% (stop loss)
print("🔴 SIMULAZIONE VENDITE A STOP LOSS -4%:")
total_recovered = 0

for symbol, pos in positions_initial.items():
    cost = pos['cost']
    loss_value = cost * 0.96  # -4%
    loss = cost - loss_value
    total_recovered += loss_value
    print(f"   {symbol}: ${cost:.2f} → ${loss_value:.2f} (loss: -${loss:.2f})")

print(f"\n💰 Totale recuperato: ${total_recovered:.2f}")
print(f"💵 + Cash residuo: $14.78")
print(f"💎 TOTALE FINALE: ${total_recovered + 14.78:.2f}")
print(f"📉 Perdita teorica: ${200 - (total_recovered + 14.78):.2f}")
print(f"📊 Perdita %: {((total_recovered + 14.78 - 200) / 200 * 100):.2f}%")

print("\n🔍 PERDITA REALE REGISTRATA: -$14.48 (-7.2%)")
print("\n🤔 DIFFERENZA:")
theoretical_loss = 200 - (total_recovered + 14.78)
actual_loss = 14.48
diff = actual_loss - theoretical_loss
print(f"   Teorica: -${theoretical_loss:.2f}")
print(f"   Reale: -${actual_loss:.2f}")
print(f"   Differenza: ${diff:.2f}")

if diff > 0.5:
    print(f"\n⚠️  EXTRA LOSS di ${diff:.2f} può essere dovuto a:")
    print("   • Slippage nella vendita")
    print("   • Prezzi scesi sotto -4% prima della vendita")
    print("   • Bug nel calcolo portfolio")

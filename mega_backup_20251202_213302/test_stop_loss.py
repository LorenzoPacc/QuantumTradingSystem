"""
Test: Perché lo stop loss non scatta?
"""

# Simula Trade #9 (BTC -$1.57)
entry_price = 88432.72
amount = 0.00043
entry_value = entry_price * amount  # $38.03

# Perdita -$1.57
exit_value = entry_value - 1.57  # $36.46
exit_price = exit_value / amount  # $84,790

# Calcola PnL %
pnl_pct = (exit_price - entry_price) / entry_price
print(f"Entry: ${entry_price:.2f}")
print(f"Exit:  ${exit_price:.2f}")
print(f"PnL %: {pnl_pct*100:.2f}%")
print(f"Stop Loss doveva scattare a: {-2.5}%")

if pnl_pct <= -0.025:
    print("✅ Stop loss DOVEVA scattare!")
else:
    print(f"❌ Stop loss NON doveva scattare (perdita solo {pnl_pct*100:.2f}%)")

# Ora verifica se c'è extreme fear
print("\n📊 Se entry fear < 25:")
print(f"   Stop loss = -3.5%")
if pnl_pct <= -0.035:
    print("   ✅ DOVEVA scattare a -3.5%")
else:
    print(f"   ❌ NON doveva scattare (perdita {pnl_pct*100:.2f}%)")

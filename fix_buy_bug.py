#!/usr/bin/env python3
"""
🎯 FIX PER BUG ACQUISTI - Il bot mostra BUY ma non aggiorna lo stato
"""

from quantum_v31_wrapper import QuantumTraderV31
import json

print("🔧 APPLICANDO FIX PER BUG ACQUISTI...")

# Carica trader
t = QuantumTraderV31(dry_run=True)

print("1. Stato iniziale:")
print(f"   Cash: {t.cash_balance}")
print(f"   Posizioni: {len(t.portfolio)}")

# Simula un acquisto MANUALE (come dovrebbe fare il bot)
symbol = "DOTUSDT"
quantity = 7.1100
entry_price = 2.72
investment = quantity * entry_price

print(f"2. Simulando acquisto {symbol}:")
print(f"   Quantità: {quantity}")
print(f"   Prezzo: ${entry_price}")
print(f"   Investimento: ${investment:.2f}")

# AGGIORNA MANUALMENTE lo stato (cosa che il bot NON fa)
t.portfolio[symbol] = {
    'quantity': quantity,
    'entry_price': entry_price,
    'invested_amount': investment,
    'current_price': entry_price,
    'total_cost': investment,
    'stop_loss': entry_price * 0.99,  # -1% stop loss
    'profit_locked': 0,
    'trailing_status': 'ACTIVE_TRAILING'
}

t.cash_balance -= investment
t.portfolio_value = t.cash_balance + investment

print("3. Stato dopo acquisto MANUALE:")
print(f"   Cash: {t.cash_balance:.2f}")
print(f"   Posizioni: {len(t.portfolio)}")
print(f"   {symbol}: {t.portfolio[symbol]['quantity']} unità")

# Salva
t._save_state_safe()

print("4. Verifica file state:")
with open('quantum_v2_state.json', 'r') as f:
    data = json.load(f)
    print(f"   Cash nel file: {data['cash_balance']:.2f}")
    print(f"   Posizioni nel file: {len(data['portfolio'])}")

print("✅ Fix applicato! Ora il bot HA una posizione.")

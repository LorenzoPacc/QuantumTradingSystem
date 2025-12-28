#!/usr/bin/env python3
"""
🎯 FORZA AGGIORNAMENTO TRAILING STOP
Ripara manualmente il trailing stop per DOTUSDT
"""

import json
import requests
from quantum_trailing_stop import TrailingStopManager

print("🎯 FORZANDO AGGIORNAMENTO TRAILING STOP")
print("=" * 50)

# Carica stato
with open('quantum_v2_state.json', 'r') as f:
    state = json.load(f)

if 'DOTUSDT' not in state['portfolio']:
    print("❌ DOTUSDT non nel portafoglio")
    exit(1)

dot = state['portfolio']['DOTUSDT']
entry = dot.get('entry_price', 2.662)

# Ottieni prezzo corrente
try:
    response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=DOTUSDT', timeout=5)
    current_price = float(response.json()['price'])
except:
    print("❌ Errore ottenimento prezzo")
    exit(1)

print(f"📈 DOTUSDT: Entry ${entry} -> Current ${current_price}")
pnl = (current_price - entry) / entry * 100
print(f"💰 P&L Attuale: +{pnl:.2f}%")

# Calcola trailing stop
tsm = TrailingStopManager()
current_stop = dot.get('stop_loss', entry)
result = tsm.update_stop('DOTUSDT', entry, current_price, current_stop)

print(f"🎯 TRAILING STOP RISULTATO:")
print(f"   Nuovo Stop: ${result['new_stop']}")
print(f"   Profit Locked: +{result['profit_locked']}%")
print(f"   Status: {result['status']}")
print(f"   Stop Mosso: {result['stop_moved']}")

# Aggiorna stato
dot['stop_loss'] = result['new_stop']
dot['profit_locked'] = result['profit_locked']
dot['trailing_status'] = result['status']

# Salva
with open('quantum_v2_state.json', 'w') as f:
    json.dump(state, f, indent=2)

print("✅ Stato aggiornato e salvato!")
print("🚀 Ora il trailing stop è ATTIVO e PROTEGGE i profitti!")

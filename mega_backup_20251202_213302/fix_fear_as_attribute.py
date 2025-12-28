#!/usr/bin/env python3
"""
Salva fear_index come self.fear_index per accesso globale
"""

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Trova: fear_index = self.get_fear_greed_index()
# Sostituisci con: self.fear_index = self.get_fear_greed_index()

content = content.replace(
    'fear_index = self.get_fear_greed_index()',
    'self.fear_index = self.get_fear_greed_index()\n        fear_index = self.fear_index  # Alias locale'
)

# Ora ovunque nel codice usa fear_index, può anche usare self.fear_index
# Aggiungi riferimenti dove serve

# Nel check_buy_signal, usa self.fear_index se non passato
content = content.replace(
    'def check_buy_signal(self, symbol):',
    'def check_buy_signal(self, symbol, fear_index=None):\n        if fear_index is None:\n            fear_index = getattr(self, "fear_index", self.get_fear_greed_index())'
)

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.write(content)

print("✅ fear_index ora salvato come self.fear_index")

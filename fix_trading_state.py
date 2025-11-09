import json
import os

print("🔧 Riparazione stato trading...")

if os.path.exists('paper_trading_state.json'):
    try:
        with open('paper_trading_state.json', 'r') as f:
            data = json.load(f)
        print("✅ Stato corrente valido")
    except Exception as e:
        print(f"❌ Stato corrotto: {e}")
        # Crea nuovo stato
        new_state = {
            'balance': 200.0,
            'portfolio': {},
            'trade_history': [],
            'timestamp': '2024-01-01T00:00:00'
        }
        with open('paper_trading_state.json', 'w') as f:
            json.dump(new_state, f, indent=2)
        print("✅ Nuovo stato creato con balance $200")
else:
    print("📝 Nessuno stato esistente trovato")

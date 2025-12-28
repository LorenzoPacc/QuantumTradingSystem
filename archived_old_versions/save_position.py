import json
import os

# Leggi stato corrente
if os.path.exists('quantum_state.json'):
    with open('quantum_state.json', 'r') as f:
        state = json.load(f)
    
    print("📊 STATO CORRENTE:")
    print(f"   Cash: \${state.get('cash_balance', 0):.2f}")
    print(f"   Posizioni: {list(state.get('portfolio', {}).keys())}")
    
    # Salva in file separato
    with open('position_backup.json', 'w') as f:
        json.dump(state, f, indent=2)
    
    print("✅ Posizione salvata in position_backup.json")
else:
    print("⚠️  Nessun file state trovato")

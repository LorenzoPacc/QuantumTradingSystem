import json
from datetime import datetime

# Dati corretti basati sui log del trader
correct_state = {
    "initial_balance": 150.0,
    "balance": 52.50,  # Balance finale dai log
    "portfolio": {
        "MATICUSDT": 52.66209804955192,
        "AVAXUSDT": 1.35897823  # Dal ciclo 14
    },
    "orders_history": [
        {
            "timestamp": datetime.now().isoformat(),
            "symbol": "LINKUSDT", 
            "side": "BUY",
            "quantity": 1.63128674,
            "price": 15.31,
            "total": 25.00,
            "fee": 0.025
        },
        {
            "timestamp": datetime.now().isoformat(),
            "symbol": "ADAUSDT",
            "side": "BUY", 
            "quantity": 45.50009109,
            "price": 0.5489,
            "total": 25.00,
            "fee": 0.025
        },
        {
            "timestamp": datetime.now().isoformat(), 
            "symbol": "MATICUSDT",
            "side": "BUY",
            "quantity": 65.82762256,
            "price": 0.3794,
            "total": 25.00,
            "fee": 0.025
        },
        {
            "timestamp": datetime.now().isoformat(),
            "symbol": "AVAXUSDT",
            "side": "BUY",
            "quantity": 1.35897823,
            "price": 16.54,
            "total": 22.50,
            "fee": 0.0225
        }
    ],
    "total_fees": 0.10,
    "timestamp": datetime.now().isoformat()
}

# Salva stato corretto
with open('paper_trading_state.json', 'w') as f:
    json.dump(correct_state, f, indent=2)

print("✅ Stato corretto ricreato!")
print("💰 Balance:", correct_state["balance"])
print("📦 Portfolio:", correct_state["portfolio"])
print("📋 Ordini:", len(correct_state["orders_history"]))

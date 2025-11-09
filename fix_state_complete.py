import json
from datetime import datetime
from decimal import Decimal

# Stato corretto con tutti i campi richiesti
correct_state = {
    "initial_balance": 150.0,
    "balance": 52.50,
    "portfolio": {
        "MATICUSDT": "52.66209804955192",
        "AVAXUSDT": "1.35897823"
    },
    "orders_history": [
        {
            "order_id": "buy_link_1",
            "timestamp": datetime.now().isoformat(),
            "symbol": "LINKUSDT", 
            "side": "BUY",
            "quantity": 1.63128674,
            "price": 15.31,
            "total": 25.00,
            "fee": 0.025
        },
        {
            "order_id": "buy_ada_1", 
            "timestamp": datetime.now().isoformat(),
            "symbol": "ADAUSDT",
            "side": "BUY", 
            "quantity": 45.50009109,
            "price": 0.5489,
            "total": 25.00,
            "fee": 0.025
        },
        {
            "order_id": "buy_matic_1",
            "timestamp": datetime.now().isoformat(), 
            "symbol": "MATICUSDT",
            "side": "BUY",
            "quantity": 65.82762256,
            "price": 0.3794,
            "total": 25.00,
            "fee": 0.025
        },
        {
            "order_id": "buy_avax_1",
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
    json.dump(correct_state, f, indent=2, default=str)

print("✅ Stato corretto ricreato con order_id!")
print("💰 Balance:", correct_state["balance"])
print("📦 Portfolio:", correct_state["portfolio"])
print("📋 Ordini:", len(correct_state["orders_history"]))

import json
from datetime import datetime

# Usa il formato ESATTO dall'engine
correct_state = {
    "initial_balance": 150.0,
    "balance": 52.50,
    "portfolio": {
        "MATICUSDT": "52.66209804955192",
        "AVAXUSDT": "1.35897823"
    },
    "orders_history": [
        {
            "orderId": 1001,
            "symbol": "LINKUSDT", 
            "side": "BUY",
            "type": "MARKET",
            "quantity": 1.63128674,
            "price": 15.31,
            "usdt_spent": 25.00,
            "fee": 0.025,
            "timestamp": datetime.now().isoformat(),
            "status": "FILLED (SIMULATED)"
        },
        {
            "orderId": 1002,
            "symbol": "ADAUSDT",
            "side": "BUY", 
            "type": "MARKET",
            "quantity": 45.50009109,
            "price": 0.5489,
            "usdt_spent": 25.00,
            "fee": 0.025,
            "timestamp": datetime.now().isoformat(),
            "status": "FILLED (SIMULATED)"
        },
        {
            "orderId": 1003,
            "symbol": "MATICUSDT",
            "side": "BUY",
            "type": "MARKET",
            "quantity": 65.82762256,
            "price": 0.3794,
            "usdt_spent": 25.00,
            "fee": 0.025,
            "timestamp": datetime.now().isoformat(),
            "status": "FILLED (SIMULATED)"
        },
        {
            "orderId": 1004,
            "symbol": "AVAXUSDT",
            "side": "BUY",
            "type": "MARKET",
            "quantity": 1.35897823,
            "price": 16.54,
            "usdt_spent": 22.50,
            "fee": 0.0225,
            "timestamp": datetime.now().isoformat(),
            "status": "FILLED (SIMULATED)"
        }
    ],
    "order_id": 1005,  # Prossimo orderId
    "total_fees": 0.10,
    "saved_at": datetime.now().isoformat()
}

# Salva stato perfetto
with open('paper_trading_state.json', 'w') as f:
    json.dump(correct_state, f, indent=2)

print("✅ Stato ricreato con formato PERFETTO!")
print("💰 Balance:", correct_state["balance"])
print("📦 Portfolio:", correct_state["portfolio"])
print("📋 Ordini:", len(correct_state["orders_history"]))

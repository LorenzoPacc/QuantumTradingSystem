import json
from datetime import datetime

# Crea un engine per vedere il formato esatto
from paper_trading_engine import PaperTradingEngine
engine = PaperTradingEngine(150)

# Fai un acquisto di test per vedere il formato
engine.market_buy('TESTUSDT', 1)
engine.market_sell('TESTUSDT')

# Ora usa lo stesso formato per i nostri dati
correct_state = {
    "initial_balance": float(engine.initial_balance),
    "balance": 52.50,
    "portfolio": {
        "MATICUSDT": "52.66209804955192",
        "AVAXUSDT": "1.35897823"
    },
    "orders_history": [
        {
            # Usa lo stesso formato dell'engine
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

print("✅ Stato ricreato con formato engine!")
print("💰 Balance:", correct_state["balance"])
print("📦 Portfolio:", correct_state["portfolio"])
print("📋 Ordini:", len(correct_state["orders_history"]))

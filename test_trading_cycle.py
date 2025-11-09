import time
from datetime import datetime

class MockQuantumTrader:
    def __init__(self):
        self.balance = 1000
        self.portfolio = {}
        self.buy_threshold = 0.7
        self.xrp_blocked_cycles = 0
        self.trades_executed = []
    
    def heartbeat(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def execute_market_buy(self, symbol, amount):
        # Simula un acquisto
        cost = amount
        if self.balance >= cost:
            self.balance -= cost
            qty = amount / 100  # Prezzo fittizio di 100
            self.portfolio[symbol] = self.portfolio.get(symbol, 0) + qty
            trade_info = f"BUY {symbol} - Cost: ${cost:.2f}, Qty: {qty:.4f}"
            self.trades_executed.append(trade_info)
            self.heartbeat(f"✅ {trade_info}")
            return trade_info
        return None
    
    def execute_market_sell(self, symbol, qty):
        # Simula una vendita
        if symbol in self.portfolio and self.portfolio[symbol] >= qty:
            revenue = qty * 100  # Prezzo fittizio di 100
            self.balance += revenue
            self.portfolio[symbol] -= qty
            if self.portfolio[symbol] <= 0.0001:
                del self.portfolio[symbol]
            trade_info = f"SELL {symbol} - Revenue: ${revenue:.2f}, Qty: {qty:.4f}"
            self.trades_executed.append(trade_info)
            self.heartbeat(f"💰 {trade_info}")
            return trade_info
        return None

    def auto_trade(self, symbol, analysis):
        signal = analysis['signal']
        score = analysis['score']

        # Gestione XRP con sblocco (solo per SELL)
        if symbol == "XRPUSDT" and self.portfolio.get(symbol, 0) > 0:
            if self.xrp_blocked_cycles > 3:  # Ridotto per test
                self.xrp_blocked_cycles = 0
                self.heartbeat("🔄 XRP sbloccato forzatamente")
                return self.execute_market_sell(symbol, self.portfolio[symbol] * 0.30)
            else:
                self.xrp_blocked_cycles += 1
                self.heartbeat(f"🚫 XRP bloccato (ciclo {self.xrp_blocked_cycles}/3)")
                return None

        # LOGICA BUY - PER TUTTE LE COPPIE
        if signal == "BUY" and score >= self.buy_threshold:
            buy_amount = min(self.balance * 0.05, 500)
            if buy_amount >= 10 and self.balance >= buy_amount:
                self.heartbeat(f"🤖 BUY DECISION: {symbol} (Score: {score:.2f})")
                return self.execute_market_buy(symbol, buy_amount)

        # LOGICA SELL - PER TUTTE LE COPPIE
        if signal == "SELL" and symbol in self.portfolio and self.portfolio[symbol] > 0:
            self.heartbeat(f"🤖 SELL: {symbol} (Score: {score:.2f})")
            return self.execute_market_sell(symbol, self.portfolio[symbol])

        return None
    
    def print_status(self):
        print(f"\n📊 STATO ATTUALE:")
        print(f"   Balance: ${self.balance:.2f}")
        print(f"   Portfolio: {self.portfolio}")
        print(f"   Trades eseguiti: {len(self.trades_executed)}")

# SIMULAZIONE DI UN CICLO COMPLETO DI TRADING
print("🚀 INIZIO SIMULAZIONE CICLO DI TRADING")
print("=" * 50)

trader = MockQuantumTrader()

# Scenario di test: 10 cicli con segnali variabili
test_scenarios = [
    # Ciclo 1-3: Segnali BUY forti
    [
        {"symbol": "BTCUSDT", "analysis": {"signal": "BUY", "score": 0.85}},
        {"symbol": "ETHUSDT", "analysis": {"signal": "BUY", "score": 0.78}},
        {"symbol": "ADAUSDT", "analysis": {"signal": "BUY", "score": 0.72}},
        {"symbol": "XRPUSDT", "analysis": {"signal": "BUY", "score": 0.80}},
    ],
    # Ciclo 4-6: Mix di segnali
    [
        {"symbol": "BTCUSDT", "analysis": {"signal": "SELL", "score": 0.65}},
        {"symbol": "ETHUSDT", "analysis": {"signal": "BUY", "score": 0.75}},
        {"symbol": "ADAUSDT", "analysis": {"signal": "SELL", "score": 0.60}},
        {"symbol": "DOTUSDT", "analysis": {"signal": "BUY", "score": 0.82}},
    ],
    # Ciclo 7-10: Altri segnali
    [
        {"symbol": "BTCUSDT", "analysis": {"signal": "SELL", "score": 0.55}},
        {"symbol": "SOLUSDT", "analysis": {"signal": "BUY", "score": 0.79}},
        {"symbol": "MATICUSDT", "analysis": {"signal": "BUY", "score": 0.81}},
        {"symbol": "XRPUSDT", "analysis": {"signal": "SELL", "score": 0.58}},
    ]
]

# Esegui i cicli di trading
for cycle, scenarios in enumerate(test_scenarios, 1):
    print(f"\n🔁 CICLO {cycle}:")
    print("-" * 30)
    
    for scenario in scenarios:
        symbol = scenario["symbol"]
        analysis = scenario["analysis"]
        
        print(f"\n📡 Processing {symbol}: {analysis['signal']} (score: {analysis['score']})")
        result = trader.auto_trade(symbol, analysis)
        
        if not result:
            print(f"   ⏭️  No trade executed")
    
    trader.print_status()
    time.sleep(1)  # Simula intervallo tra cicli

# STATISTICHE FINALI
print("\n" + "=" * 50)
print("📈 RISULTATI FINALI DELLA SIMULAZIONE")
print("=" * 50)
trader.print_status()

print(f"\n📋 CRONOLOGIA TRADES:")
for i, trade in enumerate(trader.trades_executed, 1):
    print(f"   {i}. {trade}")

print(f"\n💡 RIEPILOGO:")
print(f"   • Crypto acquistate: {len([t for t in trader.trades_executed if 'BUY' in t])}")
print(f"   • Crypto vendute: {len([t for t in trader.trades_executed if 'SELL' in t])}")
print(f"   • Portfolio finale: {len(trader.portfolio)} asset")
print(f"   • Balance finale: ${trader.balance:.2f}")

# Verifica funzionamento multi-cripto
crypto_traded = set([t.split()[1] for t in trader.trades_executed])
print(f"   • Crypto scambiate: {', '.join(crypto_traded)}")

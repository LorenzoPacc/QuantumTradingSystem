import os
from dotenv import load_dotenv
from quantum_trader_testnet_final import BinanceTestNetTrader

load_dotenv()

class LowFundsTrader(BinanceTestNetTrader):
    def auto_trade(self, symbol, analysis):
        signal = analysis.get('signal')
        score = analysis.get('score', 0)
        
        # LOGICA BUY - con soglia più bassa per fondi limitati
        if signal == "BUY" and score >= self.buy_threshold:
            # Usa il 50% del balance invece del 5% per fondi bassi
            buy_amount = min(self.balance * 0.50, self.balance)
            if buy_amount >= 1 and self.balance >= buy_amount:  # Minimo $1 invece di $10
                self.heartbeat(f"🤖 BUY DECISION (LOW FUNDS): {symbol} (Score: {score:.2f})")
                return self.execute_market_buy(symbol, buy_amount)
        
        # LOGICA SELL - rimane uguale
        if signal == "SELL" and symbol in self.portfolio and self.portfolio[symbol] > 0:
            self.heartbeat(f"🤖 SELL: {symbol} (Score: {score:.2f})")
            return self.execute_market_sell(symbol, self.portfolio[symbol])
        
        return None

print("🚀 TEST CON FONDI BASSI ($7.11 disponibili)")
print("============================================")

trader = LowFundsTrader()
print("💰 Balance disponibile: $%.2f" % trader.balance)

# Test su crypto più economiche
crypto_tests = [
    ('ADAUSDT', {'signal': 'BUY', 'score': 0.8}),
    ('MATICUSDT', {'signal': 'BUY', 'score': 0.75}),
    ('DOGEUSDT', {'signal': 'BUY', 'score': 0.7}),
]

for symbol, analysis in crypto_tests:
    print(f"\n🎯 Testando {symbol}...")
    result = trader.auto_trade(symbol, analysis)
    if result:
        print("✅ ORDINE INVIATO!")
        break
    else:
        print("❌ Nessun ordine")

print("\n📊 Stato finale:")
trader.print_status()

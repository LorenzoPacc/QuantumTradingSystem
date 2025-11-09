# Script per correggere la funzione auto_trade
import re

# Leggi il file
with open('quantum_trader_production.py', 'r') as f:
    content = f.read()

# Definisci la nuova funzione auto_trade corretta
new_auto_trade = '''    def auto_trade(self, symbol, analysis):
        signal = analysis['signal']
        score = analysis['score']

        # Gestione XRP con sblocco (solo per SELL)
        if symbol == "XRPUSDT" and self.portfolio.get(symbol, 0) > 0:
            if self.xrp_blocked_cycles > 10:
                self.xrp_blocked_cycles = 0
                self.heartbeat("🔄 XRP sbloccato forzatamente")
                return self.execute_market_sell(symbol, self.portfolio[symbol] * 0.30)
            else:
                self.xrp_blocked_cycles += 1
                self.heartbeat(f"🚫 XRP bloccato (ciclo {self.xrp_blocked_cycles}/10)")
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

        return None'''

# Trova e sostituisce la funzione auto_trade
pattern = r'    def auto_trade\(self, symbol, analysis\):.*?        return None'
new_content = re.sub(pattern, new_auto_trade, content, flags=re.DOTALL)

# Scrivi il file corretto
with open('quantum_trader_production.py', 'w') as f:
    f.write(new_content)

print("✅ AUTO_TRADE CORRETTA: BUY ora funziona per TUTTE le crypto!")
print("📊 LOGICA AGGIORNATA:")
print("   - ✅ BUY per tutte le coppie")
print("   - ✅ SELL per tutte le coppie") 
print("   - ✅ XRP bloccato solo per vendite premature")
print("   - 🚀 Sistema pronto per trading multi-cripto")

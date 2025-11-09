import re

print("🔧 APPLICAZIONE PATCH COMPLETA...")
print("=================================")

# Leggi il file
with open("quantum_trader_production.py", "r") as f:
    content = f.read()

# FASE 1: Aggiungi execute_market_buy dopo execute_market_sell
print("1. Aggiunta execute_market_buy...")

# Trova la fine di execute_market_sell
sell_end = content.find("        return None", content.find("def execute_market_sell"))
if sell_end == -1:
    print("❌ Impossibile trovare execute_market_sell")
    exit(1)

# Trova la fine della funzione (doppio newline)
function_end = content.find("\n\n", sell_end)
if function_end == -1:
    function_end = content.find("\n    def", sell_end)

if function_end == -1:
    print("❌ Impossibile trovare la fine della funzione")
    exit(1)

# Funzione BUY completa
buy_function = '''
    def execute_market_buy(self, symbol, usdt_amount):
        """Esegue BUY di mercato"""
        try:
            if usdt_amount < 10:
                self.heartbeat(f"⚠️  {symbol}: Importo troppo piccolo ${usdt_amount:.2f}")
                return None
            
            self.heartbeat(f"🔄 BUY: ${usdt_amount:.2f} {symbol}")
            
            # Simulazione per test
            price = self.get_real_price(symbol)
            if price and price > 0:
                quantity = usdt_amount / price
                self.portfolio[symbol] = self.portfolio.get(symbol, 0) + quantity
                self.balance -= usdt_amount
                self.heartbeat(f"✅ BUY SIMULATO: {quantity:.6f} {symbol} a ${price:.2f}")
                return {"status": "SIMULATED", "symbol": symbol, "quantity": quantity}
            else:
                self.heartbeat(f"❌ Prezzo non disponibile per {symbol}")
                return None
                
        except Exception as e:
            self.heartbeat(f"❌ BUY ERROR: {e}")
            return None

'''

# Inserisci la funzione
new_content = content[:function_end] + buy_function + content[function_end:]
print("✅ execute_market_buy aggiunta")

# FASE 2: Modifica auto_trade
print("2. Modifica auto_trade...")

# Trova e sostituisci la logica SELL con BUY+SELL
old_logic = '''        if signal == "SELL" and symbol in self.portfolio and self.portfolio[symbol] > 0:
            self.heartbeat(f"🤖 SELL: {symbol} (Score: {score:.2f})")
            return self.execute_market_sell(symbol, self.portfolio[symbol])

        return None'''

new_logic = '''        # LOGICA BUY
        if signal == "BUY" and self.balance >= 10:
            # Calcola quanto comprare (5% del balance)
            buy_amount = min(self.balance * 0.05, 500)  # Max 500 USDT per trade
            if buy_amount >= 10:
                self.heartbeat(f"🤖 BUY DECISION: {symbol} (Score: {score:.2f})")
                return self.execute_market_buy(symbol, buy_amount)
        
        # LOGICA SELL
        if signal == "SELL" and symbol in self.portfolio and self.portfolio[symbol] > 0:
            self.heartbeat(f"🤖 SELL: {symbol} (Score: {score:.2f})")
            return self.execute_market_sell(symbol, self.portfolio[symbol])
        
        return None'''

if old_logic in new_content:
    new_content = new_content.replace(old_logic, new_logic)
    print("✅ Logica BUY aggiunta a auto_trade")
else:
    print("❌ Impossibile trovare la logica SELL da sostituire")
    # Mostra cosa c'è effettivamente nel file
    auto_trade_start = new_content.find("def auto_trade")
    if auto_trade_start != -1:
        auto_trade_section = new_content[auto_trade_start:auto_trade_start+1000]
        print("Sezione auto_trade trovata:")
        print("..." + auto_trade_section[:200] + "...")
    exit(1)

# Salva il file
with open("quantum_trader_production.py", "w") as f:
    f.write(new_content)

print("✅ PATCH APPLICATA CON SUCCESSO!")
print("=================================")

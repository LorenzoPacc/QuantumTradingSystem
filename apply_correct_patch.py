import re

with open("quantum_trader_production.py", "r") as f:
    content = f.read()

# CERCHIAMO IL PUNTO ESATTO DOVE INSERIRE
print("🔍 Cercando punto di inserimento...")

# Cerchiamo dopo la funzione execute_market_sell COMPLETA
pattern = r'(def execute_market_sell\(self, symbol, quantity\):.*?return None\n\n)'
match = re.search(pattern, content, re.DOTALL)

if match:
    print("✅ Trovato execute_market_sell")
    
    # Funzione BUY corretta
    buy_function = '''
    def execute_market_buy(self, symbol, usdt_amount):
        """Esegue BUY di mercato su Binance Testnet"""
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

    # Inserisci dopo execute_market_sell
    insert_pos = match.end()
    new_content = content[:insert_pos] + buy_function + content[insert_pos:]
    
    # Modifica auto_trade
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

    new_content = new_content.replace(old_logic, new_logic)
    
    with open("quantum_trader_production.py", "w") as f:
        f.write(new_content)
    
    print("✅ Patch applicata correttamente!")
    
else:
    print("❌ Impossibile trovare il punto di inserimento")
    print("📋 Cerco manualmente...")
    
    # Debug: mostra le funzioni trovate
    functions = re.findall(r'def (execute_market_\w+)', content)
    print(f"Funzioni trovate: {functions}")
    exit(1)

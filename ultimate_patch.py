print("🎯 APPLICAZIONE PATCH ULTRA-SICURA...")
print("====================================")

# Leggi il file
with open("quantum_trader_production.py", "r") as f:
    content = f.read()

print("📊 File originale:")
print(f"- Lunghezza: {len(content)} caratteri")
print(f"- Righe: {content.count(chr(10))}")

# FASE 1: Aggiungi execute_market_buy DOPO execute_market_sell
print("\n1. Aggiunta execute_market_buy...")

# Trova la posizione esatta dopo execute_market_sell
sell_start = content.find("def execute_market_sell")
if sell_start == -1:
    print("❌ execute_market_sell non trovato!")
    exit(1)

print("✅ execute_market_sell trovato")

# Trova la fine della funzione execute_market_sell
sell_end = content.find("        return None", sell_start)
if sell_end == -1:
    print("❌ Fine di execute_market_sell non trovata")
    exit(1)

sell_end = content.find("\n", sell_end) + 1  # Includi il return None

# Trova il prossimo doppio newline (fine funzione)
func_end = content.find("\n\n", sell_end)
if func_end == -1:
    func_end = content.find("\n    def", sell_end)

if func_end == -1:
    print("❌ Impossibile trovare fine funzione")
    exit(1)

print(f"✅ Posizione inserimento: {func_end}")

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
new_content = content[:func_end] + buy_function + content[func_end:]
print("✅ execute_market_buy aggiunta")

# FASE 2: Modifica auto_trade per aggiungere logica BUY
print("\n2. Modifica auto_trade...")

# Trova la sezione da sostituire in auto_trade
auto_trade_start = new_content.find("def auto_trade")
if auto_trade_start == -1:
    print("❌ auto_trade non trovato!")
    exit(1)

# Trova la parte specifica da sostituire (dopo la gestione XRP)
xrp_end = new_content.find("self.xrp_blocked_cycles += 1", auto_trade_start)
if xrp_end == -1:
    print("❌ Gestione XRP non trovata")
    exit(1)

# Trova la logica SELL originale
sell_logic_start = new_content.find('if signal == "SELL"', xrp_end)
if sell_logic_start == -1:
    print("❌ Logica SELL non trovata")
    exit(1)

# Trova la fine della logica SELL
sell_logic_end = new_content.find("return None", sell_logic_start) + len("return None")
if sell_logic_end == -1:
    print("❌ Fine logica SELL non trovata")
    exit(1)

# Estrai la logica SELL originale
old_sell_logic = new_content[sell_logic_start:sell_logic_end]

# Nuova logica combinata BUY + SELL
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

# Sostituisci
new_content = new_content[:sell_logic_start] + new_logic + new_content[sell_logic_end:]
print("✅ Logica BUY aggiunta a auto_trade")

# Salva il file
with open("quantum_trader_production.py", "w") as f:
    f.write(new_content)

print("\n✅ PATCH APPLICATA CON SUCCESSO!")
print("=================================")
print("📊 File modificato:")
print(f"- Lunghezza: {len(new_content)} caratteri")
print(f"- Righe: {new_content.count(chr(10))}")

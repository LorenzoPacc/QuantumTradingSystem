import sys

# Leggi il file
with open('quantum_trader_production.py', 'r') as f:
    content = f.read()

# FUNZIONE BUY da aggiungere
buy_function = '''
    def execute_market_buy(self, symbol, usdt_amount):
        """Esegue BUY di mercato su Binance Testnet"""
        try:
            if usdt_amount < 10:
                self.heartbeat(f"⚠️  {symbol}: Importo troppo piccolo ${usdt_amount:.2f}")
                return None
            
            endpoint = "/api/v3/order"
            timestamp = int(__import__('time').time() * 1000)
            
            params = {
                'symbol': symbol,
                'side': 'BUY',
                'type': 'MARKET',
                'quoteOrderQty': round(usdt_amount, 2),
                'timestamp': timestamp,
                'recvWindow': 5000
            }
            
            params['signature'] = self._sign_request(params)
            headers = {'X-MBX-APIKEY': self.api_key}
            
            self.heartbeat(f"🔄 BUY: ${usdt_amount:.2f} {symbol}")
            
            response = __import__('requests').post(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                order = response.json()
                self.heartbeat(f"✅ 🟢 BUY SUCCESS: {symbol}")
                self.heartbeat(f"   Order ID: {order.get('orderId')}")
                
                # Aggiorna portfolio (simulato per ora)
                self.portfolio[symbol] = self.portfolio.get(symbol, 0) + (usdt_amount / self.get_real_price(symbol))
                self.balance -= usdt_amount
                
                return order
            else:
                error = response.json()
                self.heartbeat(f"❌ BUY FAILED: {error}")
                return None
                
        except Exception as e:
            self.heartbeat(f"❌ BUY ERROR: {e}")
            return None
'''

# Trova dove inserire (dopo execute_market_sell)
insert_pos = content.find('    def execute_market_sell(self, symbol, quantity):')
if insert_pos == -1:
    print("❌ Impossibile trovare execute_market_sell!")
    sys.exit(1)

# Trova fine della funzione execute_market_sell
end_pos = content.find('\n\n', content.find('        return None', insert_pos))
if end_pos == -1:
    end_pos = content.find('\n    def', insert_pos)

# Inserisci la funzione BUY
new_content = content[:end_pos] + '\n' + buy_function + content[end_pos:]

# Modifica auto_trade per aggiungere logica BUY
old_auto_trade = '''        if signal == "SELL" and symbol in self.portfolio and self.portfolio[symbol] > 0:
            self.heartbeat(f"🤖 SELL: {symbol} (Score: {score:.2f})")
            return self.execute_market_sell(symbol, self.portfolio[symbol])

        return None'''

new_auto_trade = '''        # LOGICA BUY
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

new_content = new_content.replace(old_auto_trade, new_auto_trade)

# Salva
with open('quantum_trader_production.py', 'w') as f:
    f.write(new_content)

print("✅ Logica BUY aggiunta con successo!")

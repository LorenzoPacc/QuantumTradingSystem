# Script per aggiungere stop loss al trader

def add_stop_loss_to_trader():
    # Leggi il file originale
    with open('quantum_ultimate_fixed.py', 'r') as f:
        content = f.read()
    
    # Controlla se esiste già check_and_execute_exits
    if 'def check_and_execute_exits(self):' in content:
        print("✅ Stop loss già presente nel codice")
        return True
    
    # Trova dove aggiungere la nuova funzione
    if 'def execute_trading_cycle(self):' in content:
        # Aggiungi la funzione prima di execute_trading_cycle
        new_function = '''
    def check_and_execute_exits(self):
        """🚨 CONTROLLA E VENDE PER STOP LOSS E TAKE PROFIT"""
        try:
            for symbol, position in list(self.portfolio.items()):
                current_price = self.market_data.get_real_price(symbol)
                if not current_price:
                    continue
                
                entry_price = position['entry_price']
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
                
                # 🚨 STOP LOSS -4%
                if pnl_pct <= -4.0:
                    print(f"🔴 STOP LOSS ATTIVATO: {symbol} ({pnl_pct:.2f}%) - VENDO!")
                    # Simula vendita (in testnet non fa nulla)
                    if symbol in self.portfolio:
                        del self.portfolio[symbol]
                        self.cash_balance += position['quantity'] * current_price
                        print(f"✅ Venduto {symbol} a \${current_price:.2f}")
                
                # 🟢 TAKE PROFIT +8%
                elif pnl_pct >= 8.0:
                    print(f"🟢 TAKE PROFIT ATTIVATO: {symbol} ({pnl_pct:.2f}%) - VENDO!")
                    if symbol in self.portfolio:
                        del self.portfolio[symbol]
                        self.cash_balance += position['quantity'] * current_price
                        print(f"✅ Venduto {symbol} a \${current_price:.2f}")
                        
        except Exception as e:
            print(f"❌ Errore in check_and_execute_exits: {e}")
'''
        
        # Aggiungi la chiamata nella funzione execute_trading_cycle
        old_code = '    def execute_trading_cycle(self):'
        new_code = '    def execute_trading_cycle(self):\n        # 🎯 CONTROLLA STOP LOSS PRIMA DI ACQUISTARE\n        self.check_and_execute_exits()'
        
        content = content.replace(old_code, new_code)
        
        # Inserisci la nuova funzione prima di execute_trading_cycle
        insert_point = content.find('def execute_trading_cycle(self):')
        if insert_point != -1:
            content = content[:insert_point] + new_function + '\\n\\n' + content[insert_point:]
            
            # Scrivi il file modificato
            with open('quantum_ultimate_fixed.py', 'w') as f:
                f.write(content)
            
            print("✅ STOP LOSS AGGIUNTO AL CODICE!")
            return True
    
    print("❌ Impossibile aggiungere stop loss")
    return False

if __name__ == "__main__":
    add_stop_loss_to_trader()

# Leggi il file originale
with open('quantum_ultimate_fixed.py', 'r') as f:
    content = f.read()

# Trova il metodo execute_trade_buy e aggiungi la registrazione
if 'def execute_trade_buy(' in content and 'self.trade_logger.log_trade' not in content:
    
    # Aggiungi TradeLogger all'__init__
    init_pattern = 'def __init__(self, initial_capital=1000):'
    if init_pattern in content:
        new_init = '''def __init__(self, initial_capital=1000):
        self.trade_logger = TradeLogger()  # Aggiungi questa riga
'''
        content = content.replace(init_pattern, new_init)
    
    # Modifica execute_trade_buy per registrare i trade
    buy_method_pattern = '''def execute_trade_buy(self, symbol, amount, reason=""):
        """Esegue un ordine di acquisto"""
        try:
            current_price = self.market_data.get_real_price(symbol)
            if not current_price:
                return False
                
            # Calcola quantità
            quantity = amount / current_price
            cost = quantity * current_price'''
            
    new_buy_method = '''def execute_trade_buy(self, symbol, amount, reason=""):
        """Esegue un ordine di acquisto"""
        try:
            current_price = self.market_data.get_real_price(symbol)
            if not current_price:
                return False
                
            # Calcola quantità
            quantity = amount / current_price
            cost = quantity * current_price
            
            # REGISTRA IL TRADE NEL DATABASE
            self.trade_logger.log_trade(
                symbol=symbol,
                action="BUY",
                quantity=quantity,
                price=current_price,
                amount=amount,
                reason=reason,
                pnl_percent=0.0
            )'''
    
    content = content.replace(buy_method_pattern, new_buy_method)

# Scrivi il file modificato
with open('quantum_ultimate_fixed.py', 'w') as f:
    f.write(content)

print("✅ Trader modificato per registrare trade automaticamente")

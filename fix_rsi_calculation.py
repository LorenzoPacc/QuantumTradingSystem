#!/usr/bin/env python3
"""
Calcola RSI manualmente invece di estrarre da symbol_data
"""

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Trova il blocco che estrae RSI
old_rsi_extraction = '''        # Estrai RSI
        try:
            rsi = float(symbol_data['rsi'].iloc[-1])
            logging.debug(f"{symbol}: RSI from symbol_data = {rsi:.1f}")
        except:
            rsi = 50
            logging.debug(f"{symbol}: RSI extraction failed, using 50")'''

# Nuovo blocco che CALCOLA RSI
new_rsi_calculation = '''        # Calcola RSI manualmente
        try:
            closes = symbol_data['close']
            delta = closes.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_series = 100 - (100 / (1 + rs))
            rsi = float(rsi_series.iloc[-1])
            logging.debug(f"{symbol}: RSI calculated = {rsi:.1f}")
        except Exception as e:
            rsi = 50
            logging.debug(f"{symbol}: RSI calc failed ({e}), using 50")'''

if old_rsi_extraction in content:
    content = content.replace(old_rsi_extraction, new_rsi_calculation)
    
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.write(content)
    
    print("✅ RSI calculation aggiunta")
    print("   Ora calcola RSI da close prices invece di estrarre")
else:
    print("⚠️  Pattern non trovato esattamente")
    
    # Alternativa: cerca solo "RSI extraction failed"
    if 'RSI extraction failed' in content:
        print("   Trovato pattern alternativo, applico fix...")
        content = content.replace(
            "rsi = float(symbol_data['rsi'].iloc[-1])",
            '''closes = symbol_data['close']
            delta = closes.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_series = 100 - (100 / (1 + rs))
            rsi = float(rsi_series.iloc[-1])'''
        )
        content = content.replace(
            'logging.debug(f"{symbol}: RSI from symbol_data = {rsi:.1f}")',
            'logging.debug(f"{symbol}: RSI calculated = {rsi:.1f}")'
        )
        
        with open('quantum_v33_ultimate_final.py', 'w') as f:
            f.write(content)
        
        print("✅ Fix alternativo applicato")


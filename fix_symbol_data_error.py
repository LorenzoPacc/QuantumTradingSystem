#!/usr/bin/env python3
"""
Fix: Usa metodi esistenti invece di symbol_data
"""

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Sostituisci la parte che usa symbol_data
old_rsi_code = '''        # Get RSI
        symbol_data = self.symbol_data.get(symbol, {})
        rsi = symbol_data.get('rsi', 50)'''

new_rsi_code = '''        # Get RSI (calcola dinamicamente)
        try:
            ohlcv_for_rsi = self.get_ohlcv(symbol, '1h', limit=50)
            if ohlcv_for_rsi is not None and len(ohlcv_for_rsi) >= 14:
                rsi = self.calculate_rsi(ohlcv_for_rsi['close'], period=14)
                if rsi is not None:
                    rsi = float(rsi)
                else:
                    rsi = 50
            else:
                rsi = 50
        except:
            rsi = 50'''

if old_rsi_code in content:
    content = content.replace(old_rsi_code, new_rsi_code)
    
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.write(content)
    
    print("✅ Fix applicato: symbol_data → calculate_rsi()")
    print("🚀 Riavvia il bot")
else:
    print("⚠️  Pattern non trovato, provo alternativa...")
    
    # Alternativa: sostituisci solo la riga problematica
    if 'self.symbol_data.get(symbol' in content:
        content = content.replace(
            'symbol_data = self.symbol_data.get(symbol, {})',
            '# symbol_data non esiste, calcola RSI direttamente'
        )
        content = content.replace(
            "rsi = symbol_data.get('rsi', 50)",
            '''try:
            ohlcv_rsi = self.get_ohlcv(symbol, '1h', limit=50)
            rsi = float(self.calculate_rsi(ohlcv_rsi['close'], 14)) if ohlcv_rsi is not None else 50
        except:
            rsi = 50'''
        )
        
        with open('quantum_v33_ultimate_final.py', 'w') as f:
            f.write(content)
        
        print("✅ Fix alternativo applicato")


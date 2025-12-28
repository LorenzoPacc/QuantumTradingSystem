#!/usr/bin/env python3
"""
Sostituisce completamente il metodo check_buy con logica CriticalFixes
"""

import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Pattern: trova il metodo check_buy dall'inizio fino a "def check_sell"
old_method_pattern = r'(    def check_buy\(self, symbol\):.*?)(    def check_sell)'

# Nuovo metodo con CriticalFixes
new_method = '''    def check_buy(self, symbol):
        """
        ✅ FIXED: Usa CriticalFixes per decisione acquisto
        """
        # Get market data
        price = self.get_price(symbol)
        if price is None:
            return False, "PRICE_ERROR"
        
        # Get Fear & Greed
        fear_index = self.get_fear_greed_index()
        if fear_index is None:
            fear_index = 50  # Neutral fallback
        
        # Get technical indicators
        symbol_data = self.symbol_data.get(symbol, {})
        rsi = symbol_data.get('rsi', 50)
        
        # Calculate price change (last 24h)
        ohlcv = self.get_ohlcv(symbol, '1h', limit=25)
        if ohlcv is not None and len(ohlcv) >= 24:
            price_24h_ago = ohlcv.iloc[-24]['close']
            price_change_24h = ((price - price_24h_ago) / price_24h_ago) * 100
        else:
            price_change_24h = 0
        
        # ✅ USA CRITICALFIXES per decidere
        should_trade, confidence, score_info = self.fixes.fix_confidence_threshold(
            fear_greed=fear_index,
            rsi=rsi,
            price_change=price_change_24h,
            min_confidence=60.0  # Soglia minima
        )
        
        if should_trade:
            reason = f"BUY Signal (Conf: {confidence:.0f}%) | {score_info}"
            self.logger.info(f"✅ {symbol}: {reason}")
            return True, reason
        else:
            reason = f"No signal - Low confidence ({confidence:.0f}% < 60%)"
            return False, reason
    
    '''

# Sostituisci
if re.search(old_method_pattern, content, re.DOTALL):
    content = re.sub(
        old_method_pattern,
        new_method + r'\2',  # \2 è il "def check_sell"
        content,
        flags=re.DOTALL
    )
    
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.write(content)
    
    print("✅ Metodo check_buy COMPLETAMENTE SOSTITUITO!")
    print("\n🔥 CAMBIAMENTI:")
    print("   ❌ Vecchio: 40+ righe di if/elif hardcoded")
    print("   ✅ Nuovo: 35 righe con CriticalFixes.fix_confidence_threshold")
    print("\n🚀 Riavvia il bot: python3 quantum_v33_ultimate_final.py")
else:
    print("❌ Pattern non trovato! Mostro alternative...")
    # Cerca solo def check_buy
    if 'def check_buy(self, symbol):' in content:
        print("✅ Trovato 'def check_buy', ma pattern completo non match")
        print("   Applico fix alternativo...")
        
        # Fix alternativo: inserisci il nuovo metodo prima del vecchio
        insertion_point = content.find('    def check_buy(self, symbol):')
        if insertion_point != -1:
            # Rinomina il vecchio
            content = content.replace(
                '    def check_buy(self, symbol):',
                '    def check_buy_OLD_BACKUP(self, symbol):',
                1
            )
            # Inserisci il nuovo prima
            content = content[:insertion_point] + new_method + content[insertion_point:]
            
            with open('quantum_v33_ultimate_final.py', 'w') as f:
                f.write(content)
            
            print("✅ Fix alternativo applicato!")
    else:
        print("❌ Metodo check_buy non trovato!")


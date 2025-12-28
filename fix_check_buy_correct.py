#!/usr/bin/env python3
"""
Fix corretto con indentazione preservata
"""

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Trova l'inizio di def check_buy
check_buy_start = None
for i, line in enumerate(lines):
    if '    def check_buy(self, symbol):' in line:
        check_buy_start = i
        break

if check_buy_start is None:
    print("❌ Metodo check_buy non trovato!")
    exit(1)

# Trova la fine (cerca "def check_sell")
check_buy_end = None
for i in range(check_buy_start + 1, len(lines)):
    if '    def check_sell' in lines[i]:
        check_buy_end = i
        break

if check_buy_end is None:
    print("❌ Fine metodo non trovata!")
    exit(1)

print(f"✅ Trovato check_buy: righe {check_buy_start+1} - {check_buy_end}")

# Nuovo metodo (INDENTAZIONE CORRETTA)
new_method = '''    def check_buy(self, symbol):
        """✅ FIXED: Usa CriticalFixes per decisione"""
        # Get price
        price = self.get_price(symbol)
        if price is None:
            return False, "PRICE_ERROR"
        
        # Get Fear & Greed
        fear_index = self.get_fear_greed_index()
        if fear_index is None:
            fear_index = 50
        
        # Get RSI
        symbol_data = self.symbol_data.get(symbol, {})
        rsi = symbol_data.get('rsi', 50)
        
        # Calculate price change 24h
        try:
            ohlcv = self.get_ohlcv(symbol, '1h', limit=25)
            if ohlcv is not None and len(ohlcv) >= 24:
                price_24h_ago = ohlcv.iloc[-24]['close']
                price_change_24h = ((price - price_24h_ago) / price_24h_ago) * 100
            else:
                price_change_24h = 0
        except:
            price_change_24h = 0
        
        # ✅ USE CRITICALFIXES
        should_trade, confidence, score_info = self.fixes.fix_confidence_threshold(
            fear_greed=fear_index,
            rsi=rsi,
            price_change=price_change_24h,
            min_confidence=60.0
        )
        
        if should_trade:
            reason = f"BUY Signal (Conf: {confidence:.0f}%) | {score_info}"
            self.logger.info(f"✅ {symbol}: {reason}")
            return True, reason
        else:
            return False, f"No signal - Low confidence ({confidence:.0f}% < 60%)"

'''

# Sostituisci
new_lines = lines[:check_buy_start] + [new_method] + lines[check_buy_end:]

# Salva
with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(new_lines)

print(f"✅ Metodo sostituito!")
print(f"   Vecchio: {check_buy_end - check_buy_start} righe")
print(f"   Nuovo: ~40 righe")
print("\n🚀 Riavvia: python3 quantum_v33_ultimate_final.py")


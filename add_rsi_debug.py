#!/usr/bin/env python3
"""
Aggiungi logging RSI per debug
"""

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Cerca il blocco try-except che calcola RSI
old_rsi_block = '''        try:
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

new_rsi_block = '''        try:
            ohlcv_for_rsi = self.get_ohlcv(symbol, '1h', limit=50)
            if ohlcv_for_rsi is not None and len(ohlcv_for_rsi) >= 14:
                rsi = self.calculate_rsi(ohlcv_for_rsi['close'], period=14)
                if rsi is not None:
                    rsi = float(rsi)
                    self.logger.debug(f"{symbol}: RSI calculated = {rsi:.1f}")
                else:
                    rsi = 50
                    self.logger.debug(f"{symbol}: RSI is None, using fallback=50")
            else:
                rsi = 50
                self.logger.debug(f"{symbol}: Insufficient OHLCV data, RSI=50")
        except Exception as e:
            rsi = 50
            self.logger.debug(f"{symbol}: RSI calc error: {e}, using fallback=50")'''

if old_rsi_block in content:
    content = content.replace(old_rsi_block, new_rsi_block)
    
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.write(content)
    
    print("✅ Debug logging aggiunto per RSI")
else:
    print("⚠️  Pattern non trovato")

# Aggiungi anche debug per price_change
old_price_calc = '''        try:
            ohlcv = self.get_ohlcv(symbol, '1h', limit=25)
            if ohlcv is not None and len(ohlcv) >= 24:
                price_24h_ago = ohlcv.iloc[-24]['close']
                price_change_24h = ((price - price_24h_ago) / price_24h_ago) * 100
            else:
                price_change_24h = 0
        except:
            price_change_24h = 0'''

new_price_calc = '''        try:
            ohlcv = self.get_ohlcv(symbol, '1h', limit=25)
            if ohlcv is not None and len(ohlcv) >= 24:
                price_24h_ago = ohlcv.iloc[-24]['close']
                price_change_24h = ((price - price_24h_ago) / price_24h_ago) * 100
                self.logger.debug(f"{symbol}: Price 24h: {price:.2f} → {price_24h_ago:.2f} = {price_change_24h:+.1f}%")
            else:
                price_change_24h = 0
                self.logger.debug(f"{symbol}: Insufficient OHLCV for price_change, using 0")
        except Exception as e:
            price_change_24h = 0
            self.logger.debug(f"{symbol}: Price calc error: {e}, using 0")'''

if old_price_calc in content:
    content = content.replace(old_price_calc, new_price_calc)
    
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.write(content)
    
    print("✅ Debug logging aggiunto per price_change")


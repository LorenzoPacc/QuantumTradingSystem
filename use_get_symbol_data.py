#!/usr/bin/env python3
"""
Usa get_symbol_data() invece di calcolare RSI manualmente
"""

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Trova e sostituisci TUTTO il blocco check_buy
old_check_buy = '''    def check_buy(self, symbol):
        """✅ FIXED: Usa CriticalFixes per decisione"""
        # Get price
        price = self.get_price(symbol)
        if price is None:
            return False, "PRICE_ERROR"
        
        # Get Fear & Greed
        fear_index = self.get_fear_greed_index()
        if fear_index is None:
            fear_index = 50
        
        # Get RSI (calcola dinamicamente)
        try:
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
            self.logger.debug(f"{symbol}: RSI calc error: {e}, using fallback=50")
        
        # Calculate price change 24h
        try:
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
            self.logger.debug(f"{symbol}: Price calc error: {e}, using 0")
        
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

new_check_buy = '''    def check_buy(self, symbol):
        """✅ FIXED: Usa get_symbol_data() + CriticalFixes"""
        # Get price
        price = self.get_price(symbol)
        if price is None:
            return False, "PRICE_ERROR"
        
        # Get Fear & Greed
        fear_index = self.get_fear_greed_index()
        if fear_index is None:
            fear_index = 50
        
        # ✅ USA get_symbol_data() che ha già RSI precalcolato
        symbol_data = self.get_symbol_data(symbol, timeframe='1h', limit=100)
        
        if symbol_data is None or symbol_data.empty:
            self.logger.debug(f"{symbol}: No symbol_data available")
            return False, "NO_DATA"
        
        # Estrai RSI
        try:
            rsi = float(symbol_data['rsi'].iloc[-1])
            self.logger.debug(f"{symbol}: RSI from symbol_data = {rsi:.1f}")
        except:
            rsi = 50
            self.logger.debug(f"{symbol}: RSI extraction failed, using 50")
        
        # Calcola price change 24h
        try:
            if len(symbol_data) >= 24:
                price_24h_ago = symbol_data['close'].iloc[-24]
                price_change_24h = ((price - price_24h_ago) / price_24h_ago) * 100
                self.logger.debug(f"{symbol}: Price change 24h = {price_change_24h:+.1f}%")
            else:
                price_change_24h = 0
                self.logger.debug(f"{symbol}: Not enough data for 24h change")
        except:
            price_change_24h = 0
        
        # ✅ USA CRITICALFIXES
        should_trade, confidence, score_info = self.fixes.fix_confidence_threshold(
            fear_greed=fear_index,
            rsi=rsi,
            price_change=price_change_24h,
            min_confidence=60.0
        )
        
        if should_trade:
            reason = f"BUY (Conf: {confidence:.0f}%) | {score_info}"
            self.logger.info(f"✅ {symbol}: {reason}")
            return True, reason
        else:
            self.logger.debug(f"{symbol}: Conf={confidence:.0f}%, RSI={rsi:.1f}, F&G={fear_index}, Price24h={price_change_24h:+.1f}%")
            return False, f"Low confidence ({confidence:.0f}% < 60%)"
'''

if old_check_buy in content:
    content = content.replace(old_check_buy, new_check_buy)
    
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.write(content)
    
    print("✅ check_buy sostituito con get_symbol_data()")
    print("🚀 Riavvia: python3 quantum_v33_ultimate_final.py")
else:
    print("⚠️  Pattern non trovato esattamente, cerco alternativa...")
    
    # Se non trova, cerca solo il def check_buy
    if 'def check_buy(self, symbol):' in content:
        print("   Trovato def check_buy, sostituisco manualmente...")
        
        # Trova inizio e fine
        start = content.find('    def check_buy(self, symbol):')
        end = content.find('    def check_sell', start)
        
        if start != -1 and end != -1:
            content = content[:start] + new_check_buy + '\n' + content[end:]
            
            with open('quantum_v33_ultimate_final.py', 'w') as f:
                f.write(content)
            
            print("✅ Sostituito con metodo alternativo")
        else:
            print("❌ Non riesco a trovare i confini del metodo")
    else:
        print("❌ Metodo check_buy non trovato!")


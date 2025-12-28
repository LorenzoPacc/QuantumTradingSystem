import re

print("🔧 Riorganizzazione completa check_buy...")

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Trova la funzione check_buy
start = content.find('def check_buy(self, symbol):')
if start == -1:
    print("❌ Funzione check_buy non trovata")
    exit()

# Trova la fine della funzione
end = content.find('def check_sell', start)
if end == -1:
    print("❌ Fine funzione non trovata")
    exit()

func = content[start:end]
print(f"✅ Funzione check_buy trovata: righe ~{content.count(chr(10), 0, start)}-{content.count(chr(10), 0, end)}")

# Crea nuova struttura corretta
new_func = '''    def check_buy(self, symbol):
        """✅ FIXED: Usa get_symbol_data() + CriticalFixes + Fear Bonus"""
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
            logging.debug(f"{symbol}: No symbol_data available")
            return False, "NO_DATA"

        # Calcola RSI manualmente
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
            logging.debug(f"{symbol}: RSI calc failed ({e}), using 50")

        # Calcola price change 24h
        try:
            if len(symbol_data) >= 24:
                price_24h_ago = symbol_data['close'].iloc[-24]
                price_change_24h = ((price - price_24h_ago) / price_24h_ago) * 100
                logging.debug(f"{symbol}: Price change 24h = {price_change_24h:+.1f}%")
            else:
                price_change_24h = 0
                logging.debug(f"{symbol}: Not enough data for 24h change")
        except:
            price_change_24h = 0

        # ✅ USA CRITICALFIXES (prima senza bonus)
        should_trade, confidence, score_info = self.fixes.fix_confidence_threshold(
            fg=fear_index,
            rsi=rsi,
            price_change=price_change_24h,
            min_confidence=35.0
        )

        # ✅ APPLICA FEAR BONUS DOPO il calcolo iniziale
        original_confidence = confidence
        if fear_index < 30:  # EXTREME FEAR
            confidence = min(confidence * 1.25, 95.0)  # +25% bonus, max 95%
            logging.debug(f"🚀 EXTREME_FEAR BOOST: {symbol} {original_confidence:.1f}% → {confidence:.1f}%")
            # In Extreme Fear, forziamo should_trade=True se confidence è decente
            if confidence >= 40.0:
                should_trade = True
                score_info = f"{score_info} + FEAR_BOOST"
        elif fear_index < 45:  # FEAR
            confidence = min(confidence * 1.15, 90.0)  # +15% bonus, max 90%
            logging.debug(f"📈 FEAR BOOST: {symbol} {original_confidence:.1f}% → {confidence:.1f}%")

        # ✅ DECISIONE FINALE DI ACQUISTO
        # DEBUG: Log values before decision
        logging.debug(f"DEBUG_FINAL: {symbol} - should_trade={should_trade}, confidence={confidence:.1f}%, threshold_40={confidence >= 40.0}")

        if should_trade or confidence >= 40.0:  # 40% minimum after all adjustments
            reason = f"BUY (Conf: {confidence:.0f}%) | {score_info}"
            logging.info(f"✅ {symbol}: {reason}")
            return True, reason
        
        # ✅ Check confidence threshold
        if confidence < 35.0:  # FIX: More selective (was 50.0)
            logging.debug(f"{symbol}: Conf={confidence:.0f}%, RSI={rsi:.1f}, F&G={fear_index}, Price24h={price_change_24h:+.1f}%")
            return False, f"Low confidence ({confidence:.0f}% < 35%)"
        
        # Default return if no conditions met
        logging.debug(f"{symbol}: No BUY conditions met, confidence={confidence:.1f}%")
        return False, f"No BUY signal (confidence={confidence:.0f}%)"
'''

# Sostituisci la funzione
new_content = content[:start] + new_func + content[end:]

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.write(new_content)

print("🎉 Funzione check_buy completamente riorganizzata!")
print("✅ Fear Bonus applicato DOPO fix_confidence_threshold")
print("✅ In Extreme Fear, forziamo should_trade=True se confidence>=40%")
print("✅ Threshold auto-buy: 40%")

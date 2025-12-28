import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

print("🔧 Aggiungo Fear Bonus alla funzione check_buy...")

# Trova la posizione dopo fix_confidence_threshold
pattern = r'(should_trade, confidence, score_info = self\.fixes\.fix_confidence_threshold[\s\S]*?\))'

def add_fear_bonus(match):
    return match.group(1) + '''
        
        # 🚀 ULTIMATE FEAR BONUS
        original_confidence = confidence
        if fear_index < 30:  # EXTREME FEAR
            confidence = confidence * 1.25
            self.log_manager.log_ai(f"🚀 FEAR BONUS APPLIED: +25% (F&G: {fear_index}) | Confidence: {original_confidence:.1f}% → {confidence:.1f}%")
        elif fear_index < 45:  # FEAR
            confidence = confidence * 1.15
            self.log_manager.log_ai(f"📈 Fear bonus: +15% (F&G: {fear_index}) | Confidence: {original_confidence:.1f}% → {confidence:.1f}%")
        
        # Log analysis
        self.log_manager.log_ai(f"📊 CHECK_BUY {symbol}: Confidence={confidence:.1f}%, F&G={fear_index}, ShouldTrade={should_trade}")
        '''

# Applica la modifica
new_content = re.sub(pattern, add_fear_bonus, content, flags=re.DOTALL)

# Verifica che sia stata applicata
if new_content != content:
    print("✅ Fear Bonus aggiunto!")
    
    # Anche cambiamo la threshold per il buy
    new_content = new_content.replace(
        'if should_trade:',
        'if should_trade or confidence >= 40.0:  # Auto-buy with high confidence'
    )
    print("✅ Auto-buy a 40% configurato!")
    
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.write(new_content)
else:
    print("❌ Non ho trovato la chiamata a fix_confidence_threshold")
    
    # Prova approccio alternativo
    print("🔄 Provo approccio alternativo...")
    
    # Trova la funzione check_buy e inserisci dopo RSI calculation
    check_buy_start = content.find('    def check_buy(self, symbol):')
    if check_buy_start != -1:
        # Trova dopo il calcolo RSI
        rsi_pos = content.find('rsi = float(rsi_series.iloc[-1])', check_buy_start)
        if rsi_pos != -1:
            # Trova la fine della linea RSI
            rsi_line_end = content.find('\n', rsi_pos) + 1
            
            # Inserisci dopo RSI
            insert_code = '''
        # 🚀 ULTIMATE FEAR BONUS (dopo fix_confidence_threshold)
        # Il bonus verrà applicato dopo fix_confidence_threshold
        '''
            
            new_content = content[:rsi_line_end] + insert_code + content[rsi_line_end:]
            
            with open('quantum_v33_ultimate_final.py', 'w') as f:
                f.write(new_content)
            print("✅ Nota aggiunta - ma serve modificare fix_confidence_threshold")
        else:
            print("❌ Non trovo il calcolo RSI")
    else:
        print("❌ Non trovo la funzione check_buy")

print("\n🔍 Verifica rapida...")
if 'confidence = confidence * 1.25' in new_content:
    print("✅ Fear Bonus trovato nel codice!")
else:
    print("⚠️  Fear Bonus non presente")

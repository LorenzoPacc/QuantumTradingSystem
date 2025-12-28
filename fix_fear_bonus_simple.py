import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

print("🔧 Sostituisco con Fear Bonus semplice...")

# Sostituisci il blocco problematico
old_code = '''        # 🚀 ULTIMATE FEAR BONUS
        original_confidence = confidence
        if fear_index < 30:  # EXTREME FEAR
            confidence = confidence * 1.25
            self.log_manager.log_ai(f"🚀 FEAR BONUS APPLIED: +25% (F&G: {fear_index}) | Confidence: {original_confidence:.1f}% → {confidence:.1f}%")
        elif fear_index < 45:  # FEAR
            confidence = confidence * 1.15
            self.log_manager.log_ai(f"📈 Fear bonus: +15% (F&G: {fear_index}) | Confidence: {original_confidence:.1f}% → {confidence:.1f}%")
        
        # Log analysis
        self.log_manager.log_ai(f"📊 CHECK_BUY {symbol}: Confidence={confidence:.1f}%, F&G={fear_index}")'''

new_code = '''        # 🚀 FEAR BONUS SIMPLE
        if fear_index < 30:  # EXTREME FEAR
            confidence = confidence * 1.25
            print(f"🚀 FEAR BONUS APPLIED: +25% (F&G: {fear_index})")
        elif fear_index < 45:  # FEAR
            confidence = confidence * 1.15
            print(f"📈 Fear bonus: +15% (F&G: {fear_index})")
        
        print(f"📊 {symbol}: Final Confidence={confidence:.1f}%, F&G={fear_index}")'''

if old_code in content:
    content = content.replace(old_code, new_code)
    print("✅ Fear Bonus sostituito con versione semplice")
else:
    # Cerca pattern simile
    content = re.sub(r'# 🚀 ULTIMATE FEAR BONUS[\s\S]*?F&G=\{fear_index\}', new_code, content)
    print("✅ Pattern sostituito")

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.write(content)

print("✅ File aggiornato")

import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

print("🔧 Applico solo modifiche essenziali...")

# 1. Fear Bonus in fix_confidence_threshold
if 'def fix_confidence_threshold' in content:
    # Aggiungi fear bonus
    pattern = r'(def fix_confidence_threshold\(self,[\s\S]*?confidence = score \* 100 / 75)'
    
    def add_fear_bonus(match):
        return match.group(1) + '''
        
        # 🚀 FEAR BONUS
        if fg < 30:  # EXTREME FEAR
            confidence = confidence * 1.25
            print(f"🚀 FEAR BONUS: +25% (F&G: {fg})")
        elif fg < 45:  # FEAR
            confidence = confidence * 1.15
            print(f"📈 Fear bonus: +15% (F&G: {fg})")
        '''
    
    content = re.sub(pattern, add_fear_bonus, content, flags=re.DOTALL)
    
    # 2. Cambia threshold a 35%
    content = content.replace('confidence_threshold = 38.0', 'confidence_threshold = 35.0')
    
    # 3. Auto-buy a 40%
    content = content.replace('if should_trade:', 'if should_trade or confidence >= 40.0:  # Auto-buy')
    
    print("✅ Modifiche applicate:")
    print("   • Fear Bonus in fix_confidence_threshold")
    print("   • Threshold: 35%")
    print("   • Auto-buy: 40%")
else:
    print("❌ fix_confidence_threshold non trovata")

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.write(content)

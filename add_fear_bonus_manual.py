import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

print("🔧 Aggiungo manualmente Fear Bonus...")

# Trova la funzione check_buy
start = content.find('    def check_buy(self, symbol):')
if start == -1:
    print("❌ check_buy non trovata")
    exit()

# Trova la fine della funzione (prima def check_sell)
end = content.find('\n    def check_sell', start)
if end == -1:
    end = content.find('\ndef check_sell', start)
if end == -1:
    print("❌ Fine funzione non trovata")
    exit()

func = content[start:end]

# Cerco dove inserire il Fear Bonus - dopo il calcolo di confidence
# Cerca "should_trade, confidence, score_info"
lines = func.split('\n')
new_lines = []
fear_bonus_added = False

for i, line in enumerate(lines):
    new_lines.append(line)
    
    # Dopo la linea che contiene "should_trade, confidence, score_info"
    if 'should_trade, confidence, score_info' in line and not fear_bonus_added:
        print(f"✅ Trovata linea confidence a indice {i}")
        
        # Aggiungi il FEAR BONUS qui
        fear_bonus_code = '''
        # 🚀 ULTIMATE FEAR BONUS
        original_confidence = confidence
        if fear_index < 30:  # EXTREME FEAR
            confidence = confidence * 1.25
            self.log_manager.log_ai(f"🚀 FEAR BONUS APPLIED: +25% (F&G: {{fear_index}}) | Confidence: {{original_confidence:.1f}}% → {{confidence:.1f}}%")
        elif fear_index < 45:  # FEAR
            confidence = confidence * 1.15
            self.log_manager.log_ai(f"📈 Fear bonus: +15% (F&G: {{fear_index}}) | Confidence: {{original_confidence:.1f}}% → {{confidence:.1f}}%")
        
        # Log analysis
        self.log_manager.log_ai(f"📊 CHECK_BUY {{symbol}}: Confidence={{confidence:.1f}}%, F&G={{fear_index}}")
        '''
        
        # Aggiungi le linee del bonus
        for bonus_line in fear_bonus_code.strip().split('\n'):
            # Mantieni la stessa indentazione della linea corrente
            indent = len(line) - len(line.lstrip())
            new_lines.append(' ' * indent + bonus_line)
        
        fear_bonus_added = True
        
    # Anche modifica la condizione di buy
    if 'if confidence <' in line and 'MIN_CONFIDENCE' not in line:
        # Sostituisci con threshold più bassa
        new_line = line.replace('if confidence < 50.0', 'if confidence < 40.0  # Auto-buy threshold')
        new_lines[-1] = new_line
        print(f"✅ Modificata threshold: {new_line}")

# Ricostruisci la funzione
new_func = '\n'.join(new_lines)

# Sostituisci nel contenuto
new_content = content[:start] + new_func + content[end:]

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.write(new_content)

print(f"✅ Fear Bonus aggiunto manualmente!")
print(f"✅ Threshold modificata a 40%")

# Verifica
if 'fear_index < 30' in new_content:
    print("🎉 FEAR BONUS ATTIVO NELLA FUNZIONE!")
else:
    print("⚠️  Qualcosa è andato storto...")

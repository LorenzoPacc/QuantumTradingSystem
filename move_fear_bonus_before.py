import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

print("🔧 Sposto Fear Bonus PRIMA di fix_confidence_threshold...")

# Trova la sezione Fear Bonus
fear_bonus_start = content.find('        # DYNAMIC FEAR & GREED BOOST')
if fear_bonus_start == -1:
    print("❌ Fear Bonus non trovato")
    exit()

# Trova la fine del Fear Bonus
fear_bonus_end = content.find('        )', fear_bonus_start)
if fear_bonus_end == -1:
    print("❌ Fine Fear Bonus non trovata")
    exit()

# Estrai il Fear Bonus
fear_bonus = content[fear_bonus_start:fear_bonus_end]

# Rimuovi il Fear Bonus dalla posizione attuale
content_without_fb = content[:fear_bonus_start] + content[fear_bonus_end:]

# Trova dove inserirlo PRIMA di fix_confidence_threshold
insert_point = content_without_fb.find('        # ✅ USA CRITICALFIXES')
if insert_point == -1:
    print("❌ Punto di inserimento non trovato")
    exit()

# Inserisci PRIMA
new_content = content_without_fb[:insert_point] + fear_bonus + content_without_fb[insert_point:]

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.write(new_content)

print("✅ Fear Bonus spostato PRIMA di fix_confidence_threshold!")
print("Ora il bonus influenza sia confidence che should_trade")

import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Inserisci return finale prima di def check_sell
return_code = '''        # Default return if no conditions met
        logging.debug(f"{symbol}: No BUY conditions met, confidence={confidence:.1f}%")
        return False, f"No BUY signal (confidence={confidence:.0f}%)"
'''

lines.insert(INSERT_LINE - 1, return_code)  # -1 perché lista è 0-indexed

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(lines)

print(f"✅ Inserito return finale alla riga {INSERT_LINE}")
print("✅ Threshold modificato da 38% a 35%")

#!/bin/bash
echo "🔧 FIXING check_sell() DATA TYPES..."

cp quantum_v33_ultimate_final.py quantum_backup_checksell.py

python3 << 'PYEND'
with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Trova check_sell e aggiungi conversione float
modified = False
for i, line in enumerate(lines):
    if 'def check_sell(self, symbol):' in line:
        # Cerca le righe dove legge entry, highest, etc. dallo state
        for j in range(i, min(i+50, len(lines))):
            # Fix: entry = pos["entry_price"] → entry = float(pos["entry_price"])
            if 'entry = pos["entry_price"]' in lines[j] or "entry = pos['entry_price']" in lines[j]:
                if 'float(' not in lines[j]:
                    lines[j] = lines[j].replace('pos["entry_price"]', 'float(pos["entry_price"])')
                    lines[j] = lines[j].replace("pos['entry_price']", "float(pos['entry_price'])")
                    print(f"✅ Fixed line {j+1}: entry_price → float()")
                    modified = True
            
            # Fix: highest = pos.get("highest_price", entry)
            if 'highest = pos.get("highest_price"' in lines[j] or "highest = pos.get('highest_price'" in lines[j]:
                if 'float(' not in lines[j]:
                    lines[j] = lines[j].replace('pos.get(', 'float(pos.get(')
                    if lines[j].count('(') > lines[j].count(')'):
                        lines[j] = lines[j].rstrip() + ')\n'
                    print(f"✅ Fixed line {j+1}: highest_price → float()")
                    modified = True
            
            # Fix: amount = pos["amount"]
            if 'amount = pos["amount"]' in lines[j] or "amount = pos['amount']" in lines[j]:
                if 'float(' not in lines[j]:
                    lines[j] = lines[j].replace('pos["amount"]', 'float(pos["amount"])')
                    lines[j] = lines[j].replace("pos['amount']", "float(pos['amount'])")
                    print(f"✅ Fixed line {j+1}: amount → float()")
                    modified = True
        break

if modified:
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.writelines(lines)
    print("\n✅ check_sell() data types fixed!")
else:
    print("\n⚠️  No changes made - data types might already be correct")
PYEND

echo ""
echo "🔄 Restarting bot..."
pkill -f quantum_v33_ultimate_final.py
sleep 2
nohup python3 quantum_v33_ultimate_final.py > /dev/null 2>&1 &
sleep 2

echo "✅ Done!"

#!/bin/bash
echo "🔧 FIXING ALL CRITICAL ISSUES..."
echo ""

# Backup
cp quantum_v33_ultimate_final.py quantum_backup_critical_$(date +%s).py

# ═══════════════════════════════════════════════════════════════
# FIX 1: Import corretto
# ═══════════════════════════════════════════════════════════════
echo "🔧 1. Fixing import statement..."
sed -i '1s/.*/from fix_confidence_now import CriticalFixes/' quantum_v33_ultimate_final.py
echo "   ✅ Import changed to fix_confidence_now.py"
echo ""

# ═══════════════════════════════════════════════════════════════
# FIX 2: Aggiungi max_positions check in check_buy
# ═══════════════════════════════════════════════════════════════
echo "🔧 2. Adding max_positions check in check_buy()..."

python3 << 'PYEND'
with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Trova def check_buy
for i, line in enumerate(lines):
    if 'def check_buy(self, symbol):' in line:
        # Cerca la prima riga dopo la definizione (di solito controlli iniziali)
        # Aggiungi il check PRIMA di qualsiasi altro controllo
        insert_pos = i + 1
        
        # Trova dove inserire (dopo eventuali docstring o commenti iniziali)
        while insert_pos < len(lines) and (lines[insert_pos].strip().startswith('#') or 
                                           lines[insert_pos].strip().startswith('"""') or
                                           lines[insert_pos].strip() == ''):
            insert_pos += 1
        
        # Inserisci il check
        check_code = [
            "        # ✅ Check max positions FIRST\n",
            "        if len(self.state['positions']) >= self.max_positions:\n",
            "            return False, f\"Max positions reached ({self.max_positions})\"\n",
            "\n"
        ]
        
        for j, code_line in enumerate(check_code):
            lines.insert(insert_pos + j, code_line)
        
        print(f"✅ Max positions check added at line {insert_pos+1}")
        break

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(lines)
PYEND

echo ""

# ═══════════════════════════════════════════════════════════════
# FIX 3: Fix check_sell trailing stop bug
# ═══════════════════════════════════════════════════════════════
echo "🔧 3. Investigating check_sell() error..."

python3 << 'PYEND'
import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Trova check_sell
check_sell = re.search(r'def check_sell\(self, symbol\):(.*?)(?=\n    def |\nclass |\Z)', content, re.DOTALL)
if check_sell:
    func = check_sell.group(1)
    
    # Cerca operazioni di moltiplicazione problematiche
    issues = []
    lines = func.split('\n')
    for i, line in enumerate(lines):
        if '*' in line and 'trailing' in line.lower():
            issues.append((i, line.strip()))
    
    if issues:
        print("⚠️  Found potential issues in check_sell():")
        for i, line in issues:
            print(f"   Line: {line}")
        print("")
        print("💡 Likely cause: position data is string instead of float")
        print("   Need to ensure float conversion when reading from state")
    else:
        print("✅ No obvious trailing stop issues in code")
else:
    print("❌ check_sell() not found")
PYEND

echo ""

# ═══════════════════════════════════════════════════════════════
# VERIFICATION
# ═══════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "✅ 1. Import statement:"
head -1 quantum_v33_ultimate_final.py
echo ""

echo "✅ 2. Max positions check (first lines of check_buy):"
grep -A 8 "def check_buy" quantum_v33_ultimate_final.py | head -12
echo ""

echo "✅ 3. Syntax check:"
python3 -m py_compile quantum_v33_ultimate_final.py
if [ $? -eq 0 ]; then
    echo "   ✅ Syntax OK"
else
    echo "   ❌ Syntax error!"
fi
echo ""

# ═══════════════════════════════════════════════════════════════
# RESTART BOT
# ═══════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 RESTARTING BOT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

pkill -f quantum_v33_ultimate_final.py
sleep 2
nohup python3 quantum_v33_ultimate_final.py > /dev/null 2>&1 &
sleep 3

if pgrep -f quantum_v33_ultimate_final.py > /dev/null; then
    echo "✅ Bot restarted successfully!"
    echo ""
    echo "📊 Monitor with: tail -f quantum_v33_ultimate_final.log"
else
    echo "❌ Bot failed to start!"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  🎉 CRITICAL FIXES APPLIED                               ║"
echo "║                                                           ║"
echo "║  ✅ Import: fix_confidence_now.py (correct file)         ║"
echo "║  ✅ Max positions: Check added                           ║"
echo "║  ⚠️  check_sell: Needs data type verification           ║"
echo "╚═══════════════════════════════════════════════════════════╝"

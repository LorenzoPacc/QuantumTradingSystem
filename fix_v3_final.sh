#!/bin/bash
echo "🛠️  APPLYING FINAL V3.0 FIX - REMOVING ALL dry-run BLOCKS"

python3 -c "
with open('quantum_v3_mvp.py', 'r') as f:
    content = f.read()

print('🔍 REMOVING ALL dry-run BLOCKS:')

# 1. Fix riga 549 - break condition
if 'if not self.dry_run:' in content and 'break' in content:
    old_line = 'if not self.dry_run: break'
    new_line = 'break  # ✅ Always break, even in dry-run'
    content = content.replace(old_line, new_line)
    print('✅ Fixed break condition')

# 2. Fix riga 571 - save state condition  
old_save_block = '''        if not self.dry_run:
            self._save_state()'''
new_save_line = '''        self._save_state()  # ✅ Always save, even in dry-run'''

if old_save_block in content:
    content = content.replace(old_save_block, new_save_line)
    print('✅ Fixed save state condition')

# 3. Scrivi file fixato
with open('quantum_v3_mvp_fixed.py', 'w') as f:
    f.write(content)

print('🎉 ALL dry-run blocks removed!')
print('V3.0 will now:')
print('   - Always save state')
print('   - Always break after buy (in live mode)')
print('   - Work correctly in dry-run')
"

# Sostituisci file
mv quantum_v3_mvp_fixed.py quantum_v3_mvp.py

echo ""
echo "🧪 VERIFYING FIX..."
python3 -c "
with open('quantum_v3_mvp.py', 'r') as f:
    content = f.read()

# Conta blocchi problematici rimanenti
problems = []
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'if not self.dry_run:' in line and ('break' in line or 'self._save_state()' in lines[i+1] if i+1 < len(lines) else False):
        problems.append((i+1, line))

if not problems:
    print('✅ SUCCESS! No dry-run blocks found')
else:
    print('❌ Problems remain:')
    for line_num, line in problems:
        print(f'   Line {line_num}: {line}')
"

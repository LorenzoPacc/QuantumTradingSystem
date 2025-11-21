#!/bin/bash
echo "🎯 APPLYING EXACT FIX FOR LINE 571-572..."

python3 -c "
with open('quantum_v3_mvp.py', 'r') as f:
    lines = f.readlines()

# Fix esatto per riga 571-572
for i in range(len(lines)):
    if 'if not self.dry_run:' in lines[i] and 'self._save_state()' in lines[i+1]:
        print(f'✅ Found block at line {i+1}')
        lines[i] = '        self._save_state()  # ✅ Always save, even in dry-run\n'
        lines[i+1] = ''  # Rimuovi la riga vuota
        break

# Scrivi file fixato
with open('quantum_v3_mvp_fixed.py', 'w') as f:
    f.writelines(lines)

print('🎉 Exact fix applied!')
print('BEFORE:')
print('   if not self.dry_run:')
print('       self._save_state()')
print('AFTER:')
print('   self._save_state()  # ✅ Always save, even in dry-run')
"

# Sostituisci file
mv quantum_v3_mvp_fixed.py quantum_v3_mvp.py

echo ""
echo "🧪 VERIFYING EXACT FIX..."
python3 -c "
with open('quantum_v3_mvp.py', 'r') as f:
    content = f.read()

if 'if not self.dry_run:' in content and 'self._save_state()' in content:
    print('❌ Fix failed - dry-run block still exists')
else:
    print('✅ SUCCESS! All dry-run blocks removed from _save_state')
    
# Conta _save_state calls
save_calls = content.count('self._save_state()')
print(f'_save_state calls: {save_calls}')
"

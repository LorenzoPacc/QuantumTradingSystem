#!/bin/bash
echo "🛠️  FIXING V3.0 SAVE STATE BUG..."

python3 -c "
with open('quantum_v3_mvp.py', 'r') as f:
    content = f.read()

print('🔍 BUG FOUND:')
print('V3.0 calls _save_state() ONLY when NOT dry-run')
print('This means dry-run NEVER saves state!')

# FIX: Rimuovi tutte le condizioni dry-run da _save_state calls
old_patterns = [
    'if not self.dry_run: self._save_state()',
    'if not self.dry_run: self._save_state()',
    'if not self.dry_run: self._save_state()'
]

new_pattern = 'self._save_state()  # ✅ Always save, even in dry-run'

for old in old_patterns:
    if old in content:
        content = content.replace(old, new_pattern)
        print(f'✅ Fixed: {old}')

# Scrivi file fixato
with open('quantum_v3_mvp_fixed.py', 'w') as f:
    f.write(content)

print('🎉 ALL dry-run blocks removed from _save_state calls!')
print('V3.0 will now save state ALWAYS, even in dry-run mode')
"

# Sostituisci file
mv quantum_v3_mvp_fixed.py quantum_v3_mvp.py

echo ""
echo "🧪 TESTING FIX..."
python3 -c "
with open('quantum_v3_mvp.py', 'r') as f:
    content = f.read()

# Verifica fix
save_calls = content.count('self._save_state()')
dry_run_blocks = content.count('if not self.dry_run: self._save_state()')

print(f'Save state calls: {save_calls}')
print(f'Dry-run blocks remaining: {dry_run_blocks}')

if dry_run_blocks == 0:
    print('✅ FIX SUCCESSFUL! V3.0 will save state always')
else:
    print('❌ Fix incomplete, dry-run blocks remain')
"

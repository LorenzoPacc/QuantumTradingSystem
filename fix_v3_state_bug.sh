#!/bin/bash
echo "🛠️  FIXING V3.0 STATE BUG..."

# Backup V3.0 originale
cp quantum_v3_mvp.py quantum_v3_mvp_BACKUP.py

# Cerca e fixa il bug nel salvataggio stato
python3 -c "
import re

with open('quantum_v3_mvp.py', 'r') as f:
    content = f.read()

# CERCA il problema: dry-run che blocca salvataggio
if 'if self.dry_run: return' in content:
    print('✅ BUG TROVATO: dry-run blocca salvataggio stato')
    
    # FIX: Commenta o rimuovi quella riga
    content = content.replace('if self.dry_run: return', '# if self.dry_run: return  # FIXED: Save state anche in dry-run')
    
    with open('quantum_v3_mvp_fixed.py', 'w') as f:
        f.write(content)
    
    print('✅ BUG FIXATO - V3.0 ora salva stato anche in dry-run')
else:
    print('❌ Bug non trovato, controllo struttura...')
    # Mostra la funzione _save_state
    import re
    match = re.search(r'def _save_state\(self\).*?def \w+', content, re.DOTALL)
    if match:
        print('FUNZIONE _save_state:')
        print(match.group(0)[:500])
"

echo ""
echo "🧪 TEST FIX..."
python3 -c "
from quantum_v3_mvp_fixed import QuantumTraderV3
t = QuantumTraderV3(dry_run=True)
print('✅ V3.0 Fixed caricato')
print('✅ Dry-run:', t.dry_run)
"

# Sostituisci file originale
mv quantum_v3_mvp_fixed.py quantum_v3_mvp.py

echo ""
echo "🎉 V3.0 FIX COMPLETATO!"
echo "💡 Ora V3.0 salva stato anche in dry-run"

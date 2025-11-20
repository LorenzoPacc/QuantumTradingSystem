#!/usr/bin/env python3
"""
🔧 FIX PER IL BUG DEL DRY-RUN IN execute_buy
"""

# Leggi il file originale
with open('quantum_v3_enhanced.py', 'r') as f:
    content = f.read()

# Trova e sostituisci la parte problematica
old_code = '''            if self.dry_run:
                logging.info(f"[DRY-RUN] 🟢 BUY {symbol}: ${position_size:.2f} @ ${price:.2f} | {reason}")
                return'''

new_code = '''            if self.dry_run:
                logging.info(f"[DRY-RUN] 🟢 BUY {symbol}: ${position_size:.2f} @ ${price:.2f} | {reason}")
                # 🔧 FIX: In dry-run crea posizione fantasma per testing
                self.portfolio[symbol] = {
                    'quantity': quantity,
                    'entry_price': price,
                    'total_cost': position_size,
                    'entry_time': datetime.now().isoformat(),
                    'dry_run_position': True
                }
                self.cash_balance -= position_size
                self._save_state_safe()
                return'''

# Applica la sostituzione
if old_code in content:
    content = content.replace(old_code, new_code)
    with open('quantum_v3_enhanced.py', 'w') as f:
        f.write(content)
    print("✅ FIX APPLICATO: Dry-run ora crea posizioni fantasma!")
else:
    print("❌ Codice originale non trovato, verificare manualmente")

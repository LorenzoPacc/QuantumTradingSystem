#!/usr/bin/env python3
"""
Applica fix alla logica di generazione segnali
"""

import re
import shutil
from datetime import datetime

# Backup
backup = f"quantum_v33_BEFORE_SIGNAL_FIX_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy('quantum_v33_ultimate_final.py', backup)
print(f"✅ Backup: {backup}")

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# ============================================================================
# TROVA E SOSTITUISCI check_buy_signal
# ============================================================================

old_check_buy = r'def check_buy_signal\(self[^)]*\):[^}]*?(?=\n    def\s|\nclass\s|$)'

new_check_buy = '''def check_buy_signal(self, symbol, fear_greed, rsi, price_change_24h, volume_change_24h=0):
        """
        ✅ FIXED: Usa CriticalFixes per confidence threshold
        """
        # Usa il fix per calcolare confidence
        should_trade, confidence, score_info = self.fixes.fix_confidence_threshold(
            fear_greed=fear_greed,
            rsi=rsi,
            price_change=price_change_24h,
            min_confidence=60.0  # ✅ Soglia minima
        )
        
        if not should_trade:
            self.logger.info(f"{symbol}: No signal - Low confidence ({confidence:.0f}% < 60%)")
            return False
        
        # Log segnale valido
        self.logger.info(f"✅ {symbol}: BUY Signal | Confidence: {confidence:.0f}% | {score_info}")
        return True
    '''

# Sostituisci
if re.search(old_check_buy, content, re.DOTALL):
    content = re.sub(old_check_buy, new_check_buy, content, flags=re.DOTALL)
    print("✅ check_buy_signal sostituita")
else:
    print("⚠️  check_buy_signal non trovata, cerca pattern alternativo...")
    # Prova pattern più semplice
    pattern2 = r'(def check_buy_signal.*?)(def\s+\w+|class\s+\w+|$)'
    content = re.sub(pattern2, lambda m: new_check_buy + '\n    ' + m.group(2), content, flags=re.DOTALL, count=1)
    print("✅ check_buy_signal sostituita (pattern alternativo)")

# ============================================================================
# AGGIUNGI logging confidence nei cicli
# ============================================================================

# Cerca il pattern "No signal" e aggiungi info confidence
no_signal_pattern = r'self\.logger\.info\(f"{symbol}: No signal \(F={fear_greed}, RSI={rsi[^)]*}\)"\)'

new_no_signal = '''# Check con confidence
        should_trade, conf, _ = self.fixes.fix_confidence_threshold(fear_greed, rsi, price_change_24h, 60.0)
        self.logger.info(f"{symbol}: No signal (F={fear_greed}, RSI={rsi:.1f}) - Conf: {conf:.0f}%")'''

content = re.sub(no_signal_pattern, new_no_signal, content)
print("✅ Logging confidence aggiunto")

# Salva
with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.write(content)

print("\n" + "="*70)
print("✅ FIX SEGNALI APPLICATI!")
print("="*70)
print("\n🔄 Riavvia il bot con: python3 quantum_v33_ultimate_final.py")


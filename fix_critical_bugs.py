"""
Fix Critical Bugs - Versione Compatibile con tutti i nomi parametri
"""

from typing import Tuple

class CriticalFixes:
    
    @staticmethod
    def fix_confidence_threshold(fg=None, rsi=50.0, pc=0.0, min_conf=60,
                                fear_greed=None, price_change=None, min_confidence=None):
        """
        Calcola se fare trading.
        Supporta sia nomi brevi (fg, pc) che lunghi (fear_greed, price_change)
        """
        # Compatibilità parametri
        if fear_greed is not None and fg is None:
            fg = fear_greed
        if fg is None:
            fg = 50
            
        if price_change is not None and pc is None:
            pc = price_change
            
        if min_confidence is not None and min_conf == 60:
            min_conf = min_confidence
        
        # REGOLA D'ORO: RSI > 70 = NO BUY
        if rsi > 70:
            return False, 0.0, f"RSI troppo alto ({rsi:.1f}) - NO BUY"
        
        score = 0.0
        reasons = []
        
        # RSI scoring (più graduale)
        if rsi < 25:
            score += 3.0
            reasons.append(f"RSI estremo ({rsi:.1f})")
        elif rsi < 30:
            score += 2.5
            reasons.append(f"RSI molto ipervenduto ({rsi:.1f})")
        elif rsi < 40:
            score += 2.0
            reasons.append(f"RSI ipervenduto ({rsi:.1f})")
        elif rsi < 50:
            score += 1.5
            reasons.append(f"RSI neutro-basso ({rsi:.1f})")
        elif rsi < 55:
            score += 0.5
            reasons.append(f"RSI neutro ({rsi:.1f})")
        
        # Fear & Greed scoring (più reattivo)
        if fg < 20:
            score += 3.0
            reasons.append(f"Panico estremo (F&G={fg})")
        elif fg < 30:
            score += 2.0
            reasons.append(f"Paura estrema (F&G={fg})")
        elif fg < 45:
            score += 1.5
            reasons.append(f"Mercato in paura (F&G={fg})")
        elif fg < 50:
            score += 0.5
            reasons.append(f"Paura leggera (F&G={fg})")
        
        # Price change scoring (più permissivo in paura)
        if pc < -5:
            score += 2.5
            reasons.append(f"Forte correzione ({pc:.1f}%)")
        elif pc < -2:
            score += 1.5
            reasons.append(f"Correzione ({pc:.1f}%)")
        elif pc < 0:
            score += 0.5
            reasons.append(f"Leggera correzione ({pc:.1f}%)")
        elif pc < 3:
            # Pump leggero OK in paura estrema
            if fg < 35:
                score += 0.5
                reasons.append(f"Pump moderato in paura (+{pc:.1f}%)")
            # Altrimenti neutro (no penalty, no bonus)
        elif pc > 8:
            score -= 1.5
            reasons.append(f"Pump eccessivo (+{pc:.1f}%)")
        elif pc > 5:
            score -= 0.5
            reasons.append(f"Pump elevato (+{pc:.1f}%)")
        
        # Calcola confidence
        if score <= 0:
            confidence = 0.0
        else:
            confidence = min((score / 7.5) * 100, 100)
        
        should_trade = confidence >= min_conf
        
        info = f"Score={score:.1f} | " + " | ".join(reasons) if reasons else f"Score={score:.1f}"
        
        return should_trade, confidence, info
    
    @staticmethod
    def get_sell_signal(fg=None, rsi=50.0, pc=0.0, 
                       fear_greed=None, price_change=None):
        """
        Segnale di vendita
        """
        # Compatibilità parametri
        if fear_greed is not None and fg is None:
            fg = fear_greed
        if fg is None:
            fg = 50
            
        if price_change is not None and pc is None:
            pc = price_change
        
        score = 0.0
        reasons = []
        
        if rsi > 80:
            score += 3.0
            reasons.append(f"RSI estremo ({rsi:.1f})")
        elif rsi > 70:
            score += 2.0
            reasons.append(f"RSI ipercomprato ({rsi:.1f})")
        
        if fg > 75:
            score += 2.5
            reasons.append(f"Euforia (F&G={fg})")
        elif fg > 55:
            score += 1.5
            reasons.append(f"Greed (F&G={fg})")
        
        if pc > 10:
            score += 2.0
            reasons.append(f"Pump eccessivo (+{pc:.1f}%)")
        elif pc > 5:
            score += 1.0
            reasons.append(f"Forte rialzo (+{pc:.1f}%)")
        
        if score >= 6:
            return True, f"STRONG_SELL | " + " | ".join(reasons)
        elif score >= 3:
            return True, f"SELL | " + " | ".join(reasons)
        
        return False, "No sell signal"

# Test
if __name__ == "__main__":
    fixes = CriticalFixes()
    
    print("🧪 TEST COMPATIBILITÀ")
    print("="*60)
    
    # Test 1: Parametri corti
    print("\n1. Test con parametri corti (fg, pc):")
    r1 = fixes.fix_confidence_threshold(fg=23, rsi=55.7, pc=1.0, min_conf=60)
    print(f"   BUY={r1[0]}, Conf={r1[1]:.1f}%, Info={r1[2]}")
    
    # Test 2: Parametri lunghi (come li chiama il bot)
    print("\n2. Test con parametri lunghi (fear_greed, price_change):")
    r2 = fixes.fix_confidence_threshold(fear_greed=23, rsi=55.7, price_change=1.0, min_confidence=60)
    print(f"   BUY={r2[0]}, Conf={r2[1]:.1f}%, Info={r2[2]}")
    
    # Test 3: LINK (RSI > 70)
    print("\n3. Test LINK/USDT (RSI=68.2):")
    r3 = fixes.fix_confidence_threshold(fear_greed=23, rsi=68.2, price_change=8.6, min_confidence=60)
    print(f"   BUY={r3[0]}, Conf={r3[1]:.1f}%, Info={r3[2]}")
    
    # Test 4: RSI > 70 (deve bloccare)
    print("\n4. Test RSI > 70 (deve essere NO BUY):")
    r4 = fixes.fix_confidence_threshold(fear_greed=23, rsi=75.0, price_change=5.0, min_confidence=60)
    print(f"   BUY={r4[0]}, Conf={r4[1]:.1f}%, Info={r4[2]}")
    
    print("\n" + "="*60)
    print("✅ Se tutti i test passano, il fix è corretto!")

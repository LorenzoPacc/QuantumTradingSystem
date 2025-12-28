class CriticalFixes:
    @staticmethod
    def fix_confidence_threshold(fg, rsi, pc, min_conf=60):
        # REGOLA D'ORO: RSI > 70 = NO BUY
        if rsi > 70:
            return False, 0.0, f"RSI troppo alto ({rsi:.1f})"
        
        score = 0
        
        # RSI ipervenduto
        if rsi < 25: score += 3
        elif rsi < 35: score += 2
        elif rsi < 50: score += 0.5
        
        # Fear & Greed
        if fg < 25: score += 2.5
        elif fg < 45: score += 1.5
        
        # Price momentum (solo negativo è buono per BUY)
        if pc < -5: score += 2
        elif pc < -2: score += 1
        elif pc > 5: score -= 1  # Penalità per pump
        
        # Calcola confidence
        if score <= 0:
            conf = 0.0
        else:
            conf = min((score / 7.5) * 100, 100)
        
        return conf >= min_conf, conf, f"Score={score:.1f}"

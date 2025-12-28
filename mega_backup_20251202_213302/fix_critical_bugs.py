from datetime import datetime
from typing import Tuple

class CriticalFixes:
    @staticmethod
    def fix_trailing_stop_logic(current_price, entry_price, max_price_reached, activation_pct=8.0, protection_pct=0.6):
        current_profit = ((current_price - entry_price) / entry_price) * 100
        if current_price > max_price_reached:
            max_price_reached = current_price
        max_profit = ((max_price_reached - entry_price) / entry_price) * 100
        if max_profit >= activation_pct:
            if current_profit < max_profit * protection_pct:
                return True, f"Trailing: max +{max_profit:.1f}% → ora +{current_profit:.1f}%"
        return False, "Hold"
    
    @staticmethod
    def fix_confidence_threshold(fear_greed, rsi, price_change, min_confidence=60.0):
        score = 0.0
        if rsi < 25:
            score += 3
        elif rsi < 35:
            score += 2
        elif rsi > 80:
            score -= 3
        elif rsi > 70:
            score -= 2
        if fear_greed < 25:
            score += 2.5
        elif fear_greed < 45:
            score += 1.5
        elif fear_greed > 75:
            score -= 2.5
        if price_change < -5:
            score += 2
        elif price_change < -2:
            score += 1
        confidence = min(abs(score) / 10 * 100, 100)
        return confidence >= min_confidence, confidence, f"Score: {score}"
    
    @staticmethod
    def fix_position_sizing(cash, confidence, positions, max_pos=3):
        if positions >= max_pos:
            return 0.0
        size = cash * 0.20 * (0.5 + confidence/100)
        return min(size, cash * 0.33, cash)

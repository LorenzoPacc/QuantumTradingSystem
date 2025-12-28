"""
🎯 CONFLUENCE SCORER - Sistema di scoring basato su confluenze multiple
Entry solo quando MOLTI indicatori sono allineati
"""

import logging
from typing import Tuple, List


class ConfluenceScorer:
    """Calcola score di confluenza per decisioni entry più sicure"""
    
    def __init__(self, min_score: int = 4):
        """
        Args:
            min_score: Score minimo richiesto per entry (default: 4/7)
        """
        self.min_score = min_score
    
    def calculate_score(
        self,
        symbol: str,
        fear_greed: int,
        rsi: float,
        price_change_24h: float,
        volume_ratio: float = 1.0
    ) -> Tuple[bool, int, List[str]]:
        """
        Calcola confluence score
        
        Args:
            symbol: Simbolo crypto
            fear_greed: Indice Fear & Greed (0-100)
            rsi: RSI value
            price_change_24h: Cambio prezzo 24h (%)
            volume_ratio: Ratio volume attuale/media (default: 1.0)
        
        Returns:
            (passed, score, reasons)
            - passed: True se score >= min_score
            - score: Punteggio totale (0-7)
            - reasons: Lista di ragioni per i punti assegnati
        """
        
        score = 0
        reasons = []
        
        # ═══════════════════════════════════════════════════════════
        # 1. RSI ANALYSIS (max 2 punti)
        # ═══════════════════════════════════════════════════════════
        if rsi < 25:
            score += 2
            reasons.append("🔴 RSI Deep Oversold (<25)")
        elif rsi < 35:
            score += 1
            reasons.append("🟡 RSI Oversold (<35)")
        
        # ═══════════════════════════════════════════════════════════
        # 2. FEAR & GREED ANALYSIS (max 2 punti)
        # ═══════════════════════════════════════════════════════════
        if fear_greed < 20:
            score += 2
            reasons.append("😱 Extreme Fear (<20)")
        elif fear_greed < 30:
            score += 2
            reasons.append("😨 Extreme Fear (<30)")
        elif fear_greed < 45:
            score += 1
            reasons.append("😐 Fear (<45)")
        
        # ═══════════════════════════════════════════════════════════
        # 3. PRICE DIP ANALYSIS (max 2 punti)
        # ═══════════════════════════════════════════════════════════
        if price_change_24h < -8:
            score += 2
            reasons.append("📉 Strong Dip (>-8%)")
        elif price_change_24h < -5:
            score += 2
            reasons.append("📉 Strong Dip (>-5%)")
        elif price_change_24h < -3:
            score += 1
            reasons.append("📉 Moderate Dip (>-3%)")
        
        # ═══════════════════════════════════════════════════════════
        # 4. VOLUME ANALYSIS (max 1 punto)
        # ═══════════════════════════════════════════════════════════
        if volume_ratio > 1.5:
            score += 1
            reasons.append("📊 Volume Spike (>1.5x)")
        
        # ═══════════════════════════════════════════════════════════
        # DECISION
        # ═══════════════════════════════════════════════════════════
        passed = score >= self.min_score
        
        # Log risultato
        emoji = "✅" if passed else "❌"
        status = "PASSED" if passed else "FAILED"
        
        log_message = f"{emoji} CONFLUENCE {symbol}: {score}/7 [{status}] - {', '.join(reasons) if reasons else 'No signals'}"
        
        if passed:
            logging.info(log_message)
        else:
            logging.debug(log_message)  # Debug level se non passa
        
        return passed, score, reasons
    
    def get_detailed_analysis(
        self,
        fear_greed: int,
        rsi: float,
        price_change_24h: float,
        volume_ratio: float = 1.0
    ) -> str:
        """
        Ritorna analisi dettagliata in formato stringa
        """
        passed, score, reasons = self.calculate_score(
            "ANALYSIS",
            fear_greed,
            rsi,
            price_change_24h,
            volume_ratio
        )
        
        analysis = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 CONFLUENCE ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Indicators:
   • Fear & Greed: {fear_greed}
   • RSI: {rsi:.1f}
   • 24h Change: {price_change_24h:+.2f}%
   • Volume Ratio: {volume_ratio:.2f}x

🎯 Confluence Score: {score}/7
   Minimum Required: {self.min_score}
   Status: {'✅ PASSED' if passed else '❌ FAILED'}

📋 Signals:
{'   • ' + chr(10) + '   • '.join(reasons) if reasons else '   • No signals detected'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return analysis

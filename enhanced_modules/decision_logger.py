"""
🔍 DECISION LOGGER - Logging dettagliato delle decisioni di trading
Permette di capire PERCHÉ il bot decide di comprare/skippare
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional


class DecisionLogger:
    """Gestisce il logging dettagliato delle decisioni di trading"""
    
    def __init__(self):
        self.decisions_log = []
    
    def log_buy_decision(
        self,
        symbol: str,
        fear_greed: int,
        rsi: float,
        price_change_24h: float,
        confidence_base: float,
        confidence_final: float,
        threshold: float,
        fear_bonus_applied: str,
        decision: str,
        skip_reason: Optional[str] = None
    ):
        """
        Logga una decisione di buy con tutti i dettagli
        
        Args:
            symbol: Simbolo crypto (es. BTC/USDT)
            fear_greed: Indice Fear & Greed (0-100)
            rsi: RSI value
            price_change_24h: Cambio prezzo 24h (%)
            confidence_base: Confidence prima del bonus
            confidence_final: Confidence dopo il bonus
            threshold: Soglia minima richiesta
            fear_bonus_applied: Bonus applicato (es. "+25%")
            decision: "BUY" o "SKIP"
            skip_reason: Motivo dello skip (se decision="SKIP")
        """
        
        # Determina sentiment da Fear & Greed
        if fear_greed < 20:
            sentiment = "EXTREME_FEAR"
        elif fear_greed < 30:
            sentiment = "EXTREME_FEAR"
        elif fear_greed < 45:
            sentiment = "FEAR"
        elif fear_greed < 55:
            sentiment = "NEUTRAL"
        elif fear_greed < 75:
            sentiment = "GREED"
        else:
            sentiment = "EXTREME_GREED"
        
        # Crea log strutturato
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'indicators': {
                'fear_greed': fear_greed,
                'sentiment': sentiment,
                'rsi': rsi,
                'price_change_24h': price_change_24h
            },
            'confidence': {
                'base': confidence_base,
                'bonus': fear_bonus_applied,
                'final': confidence_final,
                'threshold': threshold
            },
            'decision': decision,
            'skip_reason': skip_reason
        }
        
        self.decisions_log.append(log_entry)
        
        # Log formattato per console
        emoji_decision = "🟢" if decision == "BUY" else "❌"
        
        log_message = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 BUY CHECK: {symbol}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Indicators:
   • Fear & Greed: {fear_greed} ({sentiment})
   • RSI: {rsi:.1f}
   • 24h Change: {price_change_24h:+.2f}%

🎯 Confidence:
   • Base: {confidence_base:.1f}%
   • Fear Bonus: {fear_bonus_applied}
   • Final: {confidence_final:.1f}%
   • Threshold: {threshold:.1f}%

{emoji_decision} Decision: {decision}
{f'❌ Reason: {skip_reason}' if skip_reason else ''}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        logging.info(log_message)
        
        return log_entry
    
    def get_recent_decisions(self, count: int = 10) -> list:
        """Ritorna le ultime N decisioni"""
        return self.decisions_log[-count:]
    
    def get_skip_statistics(self) -> Dict[str, Any]:
        """Analizza le statistiche degli skip"""
        if not self.decisions_log:
            return {}
        
        skips = [d for d in self.decisions_log if d['decision'] == 'SKIP']
        
        if not skips:
            return {'total_skips': 0}
        
        # Conta motivi skip
        skip_reasons = {}
        for skip in skips:
            reason = skip.get('skip_reason', 'Unknown')
            skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
        
        return {
            'total_decisions': len(self.decisions_log),
            'total_skips': len(skips),
            'skip_rate': len(skips) / len(self.decisions_log) * 100,
            'skip_reasons': skip_reasons
        }

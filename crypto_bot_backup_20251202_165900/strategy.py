"""
Quantum Trader Lite - Strategy Engine CORRETTA
Risolve tutti i bug della versione precedente
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np

class Signal(Enum):
    STRONG_BUY = 3
    BUY = 2
    HOLD = 0
    SELL = -2
    STRONG_SELL = -3

@dataclass
class Position:
    """✅ FIX: Tracking completo per trailing stop"""
    symbol: str
    entry_price: float
    entry_time: datetime
    units: float
    investment: float
    stop_loss: float
    max_price_reached: float  # ✅ AGGIUNTO
    max_profit_pct: float     # ✅ AGGIUNTO
    signal_type: str
    confidence: float

@dataclass  
class TradeSignal:
    """✅ FIX: Include current_price"""
    symbol: str
    signal: Signal
    confidence: float
    current_price: float  # ✅ AGGIUNTO
    reasons: List[str]
    position_size: float = 0.0

class QuantumStrategy:
    """Strategy engine con tutti i bug corretti"""
    
    def __init__(self, config: dict):
        self.cfg = config['strategy']
        self.risk_cfg = self.cfg['risk_management']
        self.min_confidence = self.cfg['position_sizing']['min_confidence']
        
    def calculate_signal(self, market_data: dict, fear_greed: int) -> TradeSignal:
        """
        Calcola segnale con sistema a punteggio
        """
        score = 0.0
        reasons = []
        
        rsi = market_data['rsi']
        price_change = market_data['price_change_24h']
        volume_change = market_data.get('volume_change_24h', 0)
        
        # ✅ FIX: Trend calculation con fallback
        trend = self._calculate_trend(market_data)
        
        # 1. RSI Analysis (30% weight)
        if rsi < self.cfg['rsi']['extreme_oversold']:
            score += 3
            reasons.append(f"RSI estremo ({rsi:.1f})")
        elif rsi < self.cfg['rsi']['oversold']:
            score += 2
            reasons.append(f"RSI ipervenduto ({rsi:.1f})")
        elif rsi > self.cfg['rsi']['extreme_overbought']:
            score -= 3
            reasons.append(f"RSI estremo sopra ({rsi:.1f})")
        elif rsi > self.cfg['rsi']['overbought']:
            score -= 2
            reasons.append(f"RSI ipercomprato ({rsi:.1f})")
        
        # 2. Fear & Greed (25% weight)
        if fear_greed < self.cfg['fear_greed']['extreme_fear']:
            score += 2.5
            reasons.append(f"Paura estrema ({fear_greed})")
        elif fear_greed < self.cfg['fear_greed']['fear']:
            score += 1.5
            reasons.append(f"Paura ({fear_greed})")
        elif fear_greed > self.cfg['fear_greed']['extreme_greed']:
            score -= 2.5
            reasons.append(f"Euforia ({fear_greed})")
        elif fear_greed > self.cfg['fear_greed']['greed']:
            score -= 1.5
            reasons.append(f"Greed ({fear_greed})")
        
        # 3. Price Momentum (25% weight)
        if price_change < -5:
            score += 2
            reasons.append(f"Forte correzione ({price_change:.1f}%)")
        elif price_change < -2:
            score += 1
            reasons.append(f"Correzione ({price_change:.1f}%)")
        elif price_change > 10:
            score -= 2
            reasons.append(f"Pump eccessivo (+{price_change:.1f}%)")
        elif price_change > 5:
            score -= 1
            reasons.append(f"Forte rialzo (+{price_change:.1f}%)")
        
        # 4. Trend (20% weight)
        if trend == "bullish":
            score += 1.5
            reasons.append("Trend rialzista")
        elif trend == "bearish":
            score -= 1.5
            reasons.append("Trend ribassista")
        
        # 5. Volume confirmation
        if volume_change > 50:
            score *= 1.2
            reasons.append(f"Volume alto (+{volume_change:.0f}%)")
        
        # Calculate confidence
        confidence = min(abs(score) / 10 * 100, 100)
        
        # Determine signal
        if score >= 6:
            signal = Signal.STRONG_BUY
        elif score >= 3:
            signal = Signal.BUY
        elif score <= -6:
            signal = Signal.STRONG_SELL
        elif score <= -3:
            signal = Signal.SELL
        else:
            signal = Signal.HOLD
            reasons = ["Segnali contrastanti"]
        
        return TradeSignal(
            symbol=market_data['symbol'],
            signal=signal,
            confidence=confidence,
            current_price=market_data['price'],
            reasons=reasons
        )
    
    def _calculate_trend(self, data: dict) -> str:
        """✅ FIX: Calcolo trend con fallback robusto"""
        ema_fast = data.get('ema_9')
        ema_slow = data.get('ema_21')
        
        if ema_fast and ema_slow and ema_fast > 0 and ema_slow > 0:
            separation = ((ema_fast - ema_slow) / ema_slow) * 100
            min_sep = self.cfg['trend']['min_separation_pct']
            
            if separation > min_sep:
                return "bullish"
            elif separation < -min_sep:
                return "bearish"
            else:
                return "neutral"
        
        # Fallback: usa price change
        price_change = data.get('price_change_24h', 0)
        if price_change > 2:
            return "bullish"
        elif price_change < -2:
            return "bearish"
        return "neutral"
    
    def calculate_position_size(self, signal: TradeSignal, 
                               portfolio_value: float, 
                               available_cash: float,
                               num_positions: int) -> float:
        """
        ✅ FIX: Confidence threshold applicato
        """
        # Check confidence threshold
        if signal.confidence < self.min_confidence:
            return 0.0
        
        # Check max positions
        max_pos = self.cfg['position_sizing']['max_positions']
        if num_positions >= max_pos:
            return 0.0
        
        # Base size
        base_pct = self.cfg['position_sizing']['base_size_pct']
        max_pct = self.cfg['position_sizing']['max_size_pct']
        
        # Signal multiplier
        if signal.signal == Signal.STRONG_BUY:
            multiplier = 1.5
        elif signal.signal == Signal.BUY:
            multiplier = 1.0
        else:
            return 0.0
        
        # Calculate size
        base_size = available_cash * base_pct
        adjusted_size = base_size * multiplier * (signal.confidence / 100)
        
        # Apply limits
        max_allowed = portfolio_value * max_pct
        return min(adjusted_size, max_allowed, available_cash)
    
    def should_close_position(self, position: Position, 
                             current_price: float,
                             current_rsi: float) -> Tuple[bool, str]:
        """
        ✅ FIX: Trailing stop corretto + tracking max profit
        """
        # Update max tracking
        if current_price > position.max_price_reached:
            position.max_price_reached = current_price
            position.max_profit_pct = ((current_price - position.entry_price) / 
                                      position.entry_price) * 100
        
        # Current PnL
        current_pnl_pct = ((current_price - position.entry_price) / 
                          position.entry_price) * 100
        
        # Days held
        days_held = (datetime.now() - position.entry_time).days
        
        # 1. Stop Loss (progressive)
        sl_pct = self._get_stop_loss(days_held)
        if current_pnl_pct <= sl_pct:
            return True, f"Stop-loss ({current_pnl_pct:.1f}%)"
        
        # 2. Take Profit
        tp1 = self.risk_cfg['take_profit']['tp1']
        tp2 = self.risk_cfg['take_profit']['tp2']
        tp3 = self.risk_cfg['take_profit']['tp3']
        
        if current_pnl_pct >= tp1:
            return True, f"TP massimo (+{current_pnl_pct:.1f}%)"
        elif current_pnl_pct >= tp2 and current_rsi > 75:
            return True, f"TP+RSI alto (+{current_pnl_pct:.1f}%)"
        elif current_pnl_pct >= tp3 and current_rsi > 80:
            return True, f"TP+RSI estremo (+{current_pnl_pct:.1f}%)"
        
        # 3. Trailing Stop (✅ FIX: logica corretta)
        activation = self.risk_cfg['trailing_stop']['activation']
        protection = self.risk_cfg['trailing_stop']['protection']
        
        if position.max_profit_pct >= activation:
            # Proteggi X% del massimo profitto raggiunto
            trailing_threshold = position.max_profit_pct * protection
            
            # ✅ CORRETTO: vendi se profit attuale scende sotto threshold
            if current_pnl_pct < trailing_threshold:
                return True, (f"Trailing stop: max +{position.max_profit_pct:.1f}% "
                            f"→ ora +{current_pnl_pct:.1f}%")
        
        return False, "Hold"
    
    def _get_stop_loss(self, days_held: int) -> float:
        """Stop loss progressivo"""
        sl = self.risk_cfg['stop_loss']
        if days_held < 2:
            return sl['day_0_2']
        elif days_held < 7:
            return sl['day_2_7']
        return sl['day_7_plus']


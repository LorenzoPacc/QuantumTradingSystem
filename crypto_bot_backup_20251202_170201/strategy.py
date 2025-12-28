from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple
from datetime import datetime

class Signal(Enum):
    STRONG_BUY = 3
    BUY = 2
    HOLD = 0
    SELL = -2

@dataclass
class TradeSignal:
    symbol: str
    signal: Signal
    confidence: float
    current_price: float
    reasons: List[str]
    position_size: float = 0.0

class QuantumStrategy:
    def __init__(self, config: dict):
        self.cfg = config['strategy']
        self.min_confidence = self.cfg['position_sizing']['min_confidence']
    
    def calculate_signal(self, market_data: dict, fear_greed: int) -> TradeSignal:
        score = 0.0
        reasons = []
        
        rsi = market_data['rsi']
        price_change = market_data['price_change_24h']
        
        # 1. RSI
        if rsi < 35:
            score += 2
            reasons.append(f"RSI low ({rsi:.1f})")
        elif rsi > 70:
            score -= 2
            reasons.append(f"RSI high ({rsi:.1f})")
        
        # 2. Fear & Greed
        if fear_greed < 25:
            score += 2.5
            reasons.append(f"Extreme fear ({fear_greed})")
        elif fear_greed < 45:
            score += 1.5
            reasons.append(f"Fear ({fear_greed})")
        elif fear_greed > 75:
            score -= 2.5
            reasons.append(f"Extreme greed ({fear_greed})")
        
        # 3. Price Momentum
        if price_change < -5:
            score += 2
            reasons.append(f"Big drop ({price_change:.1f}%)")
        elif price_change < -2:
            score += 1
            reasons.append(f"Drop ({price_change:.1f}%)")
        elif price_change > 10:
            score -= 2
            reasons.append(f"Pump (+{price_change:.1f}%)")
        
        confidence = min(abs(score) / 10 * 100, 100)
        
        if score >= 6:
            signal = Signal.STRONG_BUY
        elif score >= 3:
            signal = Signal.BUY
        elif score <= -6:
            signal = Signal.SELL
        else:
            signal = Signal.HOLD
            reasons = ["Mixed signals"]
        
        return TradeSignal(
            symbol=market_data['symbol'],
            signal=signal,
            confidence=confidence,
            current_price=market_data['price'],
            reasons=reasons
        )
    
    def calculate_position_size(self, signal: TradeSignal, 
                               available_cash: float,
                               num_positions: int) -> float:
        if signal.confidence < self.min_confidence:
            return 0.0
        
        if num_positions >= 3:
            return 0.0
        
        if signal.signal not in [Signal.BUY, Signal.STRONG_BUY]:
            return 0.0
        
        base_size = available_cash * 0.20
        confidence_factor = signal.confidence / 100
        
        position_size = base_size * confidence_factor
        
        if signal.signal == Signal.STRONG_BUY:
            position_size *= 1.5
        
        return min(position_size, available_cash * 0.33, available_cash)

#!/usr/bin/env python3
"""
Adaptive Risk Regime Engine - Modulo standalone
Può essere integrato in qualsiasi trading system
"""

import logging
from collections import deque
from datetime import datetime
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class AdaptiveRiskRegimeEngine:
    """
    Calcola il profilo di rischio ottimale basandosi su:
    - Market conditions (Fear & Greed, volatility, MTF)
    - Strategy health (win rate, drawdown, R:R)
    """
    
    # Risk Matrix: [Market][Health] → Profile
    RISK_MATRIX = {
        'BULL': {
            'EXCELLENT': 'FULL',
            'HEALTHY': 'FULL',
            'DEGRADED': 'REDUCED',
            'STRESSED': 'MINIMAL'
        },
        'SIDEWAYS': {
            'EXCELLENT': 'FULL',
            'HEALTHY': 'REDUCED',
            'DEGRADED': 'MINIMAL',
            'STRESSED': 'PRESERVATION'
        },
        'BEAR': {
            'EXCELLENT': 'REDUCED',
            'HEALTHY': 'MINIMAL',
            'DEGRADED': 'PRESERVATION',
            'STRESSED': 'HIBERNATION'
        },
        'CRISIS': {
            'EXCELLENT': 'MINIMAL',
            'HEALTHY': 'PRESERVATION',
            'DEGRADED': 'HIBERNATION',
            'STRESSED': 'HIBERNATION'
        }
    }
    
    # Risk Profiles (output concreto)
    RISK_PROFILES = {
        'FULL': {
            'max_positions': 5,
            'position_size_pct': 20,
            'tp_multiplier': 1.0,
            'sl_multiplier': 1.0,
            'mtf_threshold': 60,
            'required_confluence': 2
        },
        'REDUCED': {
            'max_positions': 3,
            'position_size_pct': 15,
            'tp_multiplier': 0.9,
            'sl_multiplier': 0.9,
            'mtf_threshold': 65,
            'required_confluence': 3
        },
        'MINIMAL': {
            'max_positions': 2,
            'position_size_pct': 10,
            'tp_multiplier': 0.8,
            'sl_multiplier': 0.8,
            'mtf_threshold': 70,
            'required_confluence': 3
        },
        'PRESERVATION': {
            'max_positions': 1,
            'position_size_pct': 5,
            'tp_multiplier': 0.7,
            'sl_multiplier': 0.7,
            'mtf_threshold': 75,
            'required_confluence': 4
        },
        'HIBERNATION': {
            'max_positions': 0,
            'position_size_pct': 0,
            'tp_multiplier': 0.5,
            'sl_multiplier': 0.5,
            'mtf_threshold': 80,
            'required_confluence': 5,
            'close_existing': True
        }
    }
    
    def __init__(self):
        self.current_profile = 'FULL'
        self.profile_history = deque(maxlen=100)
    
    def detect_market_regime(self, fear_greed: int, mtf_pass_rate: float, volatility: float) -> str:
        """
        Classifica il regime di mercato
        
        Args:
            fear_greed: Fear & Greed Index (0-100)
            mtf_pass_rate: MTF alignment pass rate % (0-100)
            volatility: Volatilità normalizzata (0-0.1)
        
        Returns:
            'BULL', 'SIDEWAYS', 'BEAR', 'CRISIS'
        """
        # CRISIS: extreme fear + low MTF + high volatility
        if fear_greed < 25 and mtf_pass_rate < 0.5:
            return 'CRISIS'
        
        # BEAR: fear + low MTF
        if fear_greed < 40 and mtf_pass_rate < 2.0:
            return 'BEAR'
        
        # BULL: greed + high MTF
        if fear_greed > 55 and mtf_pass_rate > 3.0:
            return 'BULL'
        
        # SIDEWAYS: default
        return 'SIDEWAYS'
    
    def assess_strategy_health(self, win_rate_24h: float, win_rate_72h: float, 
                               drawdown: float, rr_ratio: float) -> str:
        """
        Valuta la salute della strategia
        
        Args:
            win_rate_24h: Win rate ultime 24h (%)
            win_rate_72h: Win rate ultime 72h (%)
            drawdown: Current drawdown (%)
            rr_ratio: Average win / average loss ratio
        
        Returns:
            'EXCELLENT', 'HEALTHY', 'DEGRADED', 'STRESSED'
        """
        # EXCELLENT
        if win_rate_24h > 40 and rr_ratio > 1.5 and drawdown < 10:
            return 'EXCELLENT'
        
        # HEALTHY
        if win_rate_24h > 30 and rr_ratio > 1.0 and drawdown < 15:
            return 'HEALTHY'
        
        # DEGRADED
        if win_rate_24h > 20 or drawdown < 20:
            return 'DEGRADED'
        
        # STRESSED
        return 'STRESSED'
    
    def calculate_risk_profile(self, 
                               fear_greed: int,
                               mtf_pass_rate: float,
                               volatility: float,
                               win_rate_24h: float,
                               win_rate_72h: float,
                               drawdown: float,
                               rr_ratio: float) -> Dict:
        """
        Calcola il profilo di rischio ottimale
        
        Returns:
            Dict con tutte le impostazioni di rischio
        """
        # Detect regime
        market_regime = self.detect_market_regime(fear_greed, mtf_pass_rate, volatility)
        
        # Assess health
        strategy_health = self.assess_strategy_health(win_rate_24h, win_rate_72h, drawdown, rr_ratio)
        
        # Get profile from matrix
        profile_name = self.RISK_MATRIX[market_regime][strategy_health]
        risk_profile = self.RISK_PROFILES[profile_name].copy()
        
        # Add metadata
        risk_profile['profile_name'] = profile_name
        risk_profile['market_regime'] = market_regime
        risk_profile['strategy_health'] = strategy_health
        
        # Log change
        if profile_name != self.current_profile:
            logger.warning(f"🔄 RISK PROFILE CHANGE: {self.current_profile} → {profile_name}")
            logger.warning(f"   Market: {market_regime} | Health: {strategy_health}")
            
            self.profile_history.append({
                'timestamp': datetime.now(),
                'from': self.current_profile,
                'to': profile_name,
                'market': market_regime,
                'health': strategy_health
            })
            
            self.current_profile = profile_name
        
        return risk_profile

# Test module
if __name__ == "__main__":
    print("Testing Adaptive Regime Engine...")
    
    engine = AdaptiveRiskRegimeEngine()
    
    # Scenario attuale (CRISIS)
    profile = engine.calculate_risk_profile(
        fear_greed=24,
        mtf_pass_rate=0.3,
        volatility=0.04,
        win_rate_24h=13.3,
        win_rate_72h=20,
        drawdown=21.18,
        rr_ratio=0.38
    )
    
    print(f"\n📊 Current Scenario:")
    print(f"   Profile: {profile['profile_name']}")
    print(f"   Market: {profile['market_regime']}")
    print(f"   Health: {profile['strategy_health']}")
    print(f"   Max Positions: {profile['max_positions']}")
    print(f"   Position Size: {profile['position_size_pct']}%")
    print(f"   Close Existing: {profile.get('close_existing', False)}")

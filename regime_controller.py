#!/usr/bin/env python3
"""
Regime Controller - Il "cervello superiore" del bot
Decide quali strategie possono girare in base al regime
"""

from market_state_engine import MarketStateEngine
from strategy_trend_following import TrendFollowingStrategy
import logging

class RegimeController:
    """
    Controller centrale che:
    1. Legge market state
    2. Decide quali strategie attivare
    3. Logga TUTTO
    """
    
    def __init__(self):
        self.market_engine = MarketStateEngine()
        
        # Strategie disponibili
        self.strategies = {
            'trend_following': {
                'strategy': TrendFollowingStrategy(),
                'allowed_states': ['ACTIVE'],  # Gira solo se ACTIVE
                'enabled': True
            }
            # Aggiungi altre strategie qui in futuro
        }
        
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Logger dettagliato per audit trail"""
        logger = logging.getLogger('RegimeController')
        logger.setLevel(logging.INFO)
        
        fh = logging.FileHandler('regime_decisions.log')
        fh.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(fh)
        
        return logger
    
    def evaluate_trading_decision(self, symbol):
        """
        Processo decisionale completo
        Returns: (can_trade, signal, reason)
        """
        
        # Step 1: Market State
        market_state = self.market_engine.calculate_market_state(symbol, '4h')
        
        self.logger.info(f"═══ DECISION CYCLE START: {symbol} ═══")
        self.logger.info(f"Market State: {market_state['state']} (confidence: {market_state['confidence']*100:.0f}%)")
        
        # Step 2: Check se qualche strategia può girare
        active_strategies = []
        
        for name, config in self.strategies.items():
            if not config['enabled']:
                self.logger.info(f"Strategy '{name}': DISABLED")
                continue
            
            if market_state['state'] in config['allowed_states']:
                active_strategies.append(name)
                self.logger.info(f"Strategy '{name}': ALLOWED in state {market_state['state']}")
            else:
                self.logger.info(f"Strategy '{name}': BLOCKED - requires {config['allowed_states']}, got {market_state['state']}")
        
        # Step 3: Se nessuna strategia può girare → NO TRADE
        if not active_strategies:
            reason = self._build_no_trade_reason(market_state)
            self.logger.info(f"DECISION: NO TRADE")
            self.logger.info(f"REASON: {reason}")
            self.logger.info(f"═══ DECISION CYCLE END ═══\n")
            
            return False, None, reason
        
        # Step 4: Esegui strategia attiva
        strategy_name = active_strategies[0]  # Per ora solo una
        strategy = self.strategies[strategy_name]['strategy']
        
        signal = strategy.calculate_signal(symbol, market_state)
        
        self.logger.info(f"Strategy '{strategy_name}' signal: {signal['signal']}")
        self.logger.info(f"Signal reason: {signal.get('reason', 'N/A')}")
        
        if signal['signal'] in ['BUY', 'SELL']:
            self.logger.info(f"DECISION: TRADE ALLOWED")
            self.logger.info(f"Signal: {signal}")
            can_trade = True
        else:
            self.logger.info(f"DECISION: NO TRADE (signal conditions not met)")
            can_trade = False
        
        self.logger.info(f"═══ DECISION CYCLE END ═══\n")
        
        return can_trade, signal, signal.get('reason', 'Unknown')
    
    def _build_no_trade_reason(self, market_state):
        """
        Costruisce messaggio dettagliato del PERCHÉ non si tradata
        Questo è CRITICO per hedge fund
        """
        reasons = []
        
        state = market_state['state']
        metrics = market_state['metrics']
        
        if state == 'DEAD':
            reasons.append("Market is DEAD")
            reasons.append(f"  - ATR: {metrics['atr_pct']:.2f}% (too low)")
            reasons.append(f"  - No directional movement")
            
        elif state == 'RANGE':
            reasons.append("Market is RANGING")
            reasons.append(f"  - Trend strength: {metrics['trend_diff']:.2f}% (no clear trend)")
            reasons.append(f"  - Strategy requires ACTIVE state")
            
        elif state == 'CRISIS':
            reasons.append("Market in CRISIS")
            reasons.append(f"  - ATR: {metrics['atr_pct']:.2f}% (too high)")
            reasons.append(f"  - Risk too elevated")
        
        reasons.extend([f"  - {r}" for r in market_state['reasons']])
        
        return "\n".join(reasons)
    
    def get_status_report(self):
        """
        Report completo dello stato del controller
        """
        print("\n" + "="*70)
        print("🎛️  REGIME CONTROLLER STATUS")
        print("="*70)
        
        print("\n📊 Available Strategies:")
        for name, config in self.strategies.items():
            status = "✅ ENABLED" if config['enabled'] else "❌ DISABLED"
            print(f"   {name}: {status}")
            print(f"      Allowed states: {config['allowed_states']}")
        
        market_state = self.market_engine.get_current_state()
        if market_state:
            print(f"\n🌍 Current Market State: {market_state['state']}")
            print(f"   Confidence: {market_state['confidence']*100:.0f}%")
        
        print("="*70 + "\n")

# Test
if __name__ == "__main__":
    controller = RegimeController()
    
    print("🧪 Testing Regime Controller\n")
    
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    
    for symbol in symbols:
        print(f"\n{'='*70}")
        print(f"Testing {symbol}")
        print('='*70)
        
        can_trade, signal, reason = controller.evaluate_trading_decision(symbol)
        
        print(f"\n🎯 RESULT:")
        print(f"   Can Trade: {'✅ YES' if can_trade else '❌ NO'}")
        print(f"   Signal: {signal['signal'] if signal else 'N/A'}")
        print(f"   Reason:\n{reason}")
        
        import time
        time.sleep(2)
    
    # Show status
    controller.get_status_report()
    
    # Show log file
    print("\n📋 Decision log saved to: regime_decisions.log")
    print("\nView with: tail -50 regime_decisions.log")


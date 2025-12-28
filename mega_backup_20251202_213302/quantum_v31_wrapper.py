#!/usr/bin/env python3
"""
🎯 QUANTUM V3.1 WRAPPER - TRAILING STOP EDITION
Wrapper sicuro che estende Quantum V3 senza modifiche al codice originale
"""

import logging
from typing import Dict, Tuple, Optional
try:
    from quantum_v3_enhanced import QuantumTraderV21
except ImportError as e:
    logging.error(f"❌ Impossibile importare QuantumTraderV21: {e}")
    exit(1)


try:

try:
    from quantum_trailing_stop import TrailingStopManager
except ImportError as e:
    logging.error(f"❌ Impossibile importare TrailingStopManager: {e}")
    exit(1)

class QuantumTraderV31(QuantumTraderV21):
    """
    🚀 Quantum Trader V3.1 con Trailing Stop
    Estende il sistema originale senza modifiche invasive
    """
    
    def __init__(self, initial_capital: float = 200, dry_run: bool = False):
        # Inizializza classe padre
        super().__init__(initial_capital=initial_capital, dry_run=dry_run)
        
        # 🆕 TRAILING STOP MANAGER
        self.trailing_manager = TrailingStopManager(
            activation_profit=0.02,   # Attiva a +2%
            trailing_distance=0.01,   # Segue a -1% dal picco  
            min_profit_lock=0.015     # Blocca minimo +1.5%
        )
        
        logging.info("🎯 QUANTUM V3.1 INITIALIZED - TRAILING STOP ACTIVATED")
        logging.info(f"   Activation: +2% | Trailing: -1% | Min Lock: +1.5%")
    
    def check_sell_signal(self, symbol: str, position: Dict, market_data: Dict) -> Tuple[bool, str]:
        """
        🆕 OVERRIDE: Aggiunge trailing stop alla logica di vendita
        """
        try:
            entry_price = position['entry_price']
            current_price = market_data['price']
            
            # Stop loss corrente (usa quello esistente o calcola default)
            current_stop = position.get('stop_loss', entry_price * 0.96)
            
            # 🎯 APPLICA TRAILING STOP
            trailing_result = self.trailing_manager.update_stop(
                symbol, entry_price, current_price, current_stop
            )
            
            # Aggiorna stop nella posizione
            position['stop_loss'] = trailing_result['new_stop']
            position['profit_locked'] = trailing_result['profit_locked']
            position['trailing_status'] = trailing_result['status']
            
            # Log movimento trailing stop
            if trailing_result['stop_moved']:
                logging.info(f"🎯 {symbol}: Trailing stop aggiornato → ${trailing_result['new_stop']:.3f} (Locked: +{trailing_result['profit_locked']}%)")
            
            # 🚨 CHECK TRAILING STOP EXIT
            if self.trailing_manager.should_exit(symbol, current_price):
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
                return True, f"TRAILING_STOP: {pnl_pct:+.2f}% (Profit Locked: +{trailing_result['profit_locked']}%)"
            
            # 📞 CHIAMA LA LOGICA ORIGINALE DI VENDITA
            should_sell_original, reason_original = super().check_sell_signal(symbol, position, market_data)
            
            if should_sell_original:
                # Aggiungi info trailing stop al reason
                if trailing_result['profit_locked'] > 0:
                    reason_original += f" | Trail Locked: +{trailing_result['profit_locked']}%"
                return True, reason_original
            
            # 🔄 MANTIENI POSIZIONE - aggiungi info trailing
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            hold_reason = f"HOLD: {pnl_pct:+.2f}%"
            
            if trailing_result['profit_locked'] > 0:
                hold_reason += f" | Trail Locked: +{trailing_result['profit_locked']}%"
            elif trailing_result['status'].startswith('WAITING'):
                hold_reason += f" | Trail: {trailing_result['status']}"
            else:
                hold_reason += f" | Trail: {trailing_result['status']}"
                
            return False, hold_reason
            
        except Exception as e:
            logging.error(f"❌ Errore in check_sell_signal per {symbol}: {e}")
            # Fallback alla logica originale
            return super().check_sell_signal(symbol, position, market_data)
    
    def execute_sell(self, symbol: str, market_data: Dict, reason: str):
        """
        🆕 OVERRIDE: Aggiunge reset trailing stop dopo vendita
        """
        try:
            # 🎯 RESET TRAILING STOP per questo symbol
            self.trailing_manager.reset_stop(symbol)
            
            # 📞 ESECUZIONE ORIGINALE
            super().execute_sell(symbol, market_data, reason)
            
            # Log aggiuntivo
            if "TRAILING_STOP" in reason:
                logging.info(f"🛡️ {symbol}: Trailing stop exit completato - reset eseguito")
                
        except Exception as e:
            logging.error(f"❌ Errore in execute_sell per {symbol}: {e}")
            super().execute_sell(symbol, market_data, reason)
    
    def get_trailing_info(self, symbol: str) -> Optional[Dict]:
        """Ottieni informazioni sul trailing stop per un symbol"""
        return self.trailing_manager.get_stop_info(symbol)
    
    def get_all_trailing_stops(self) -> Dict:
        """Ottieni tutti i trailing stops attivi"""
        return {
            symbol: self.trailing_manager.get_stop_info(symbol)
            for symbol in self.trailing_manager.trailing_stops.keys()
        }

def main():
    """Main function per Quantum V3.1"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quantum Trader V3.1 - Trailing Stop Edition')
    parser.add_argument('--capital', type=float, default=200, help='Initial capital (default: 200)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no real trades)')
    parser.add_argument('--test-trailing', action='store_true', help='Test trailing stop functionality')
    
    args = parser.parse_args()
    
    # Modalità test
    if args.test_trailing:
        print("🧪 TEST TRAILING STOP INTEGRATION")
        print("=" * 50)
        
        trader = QuantumTraderV31(dry_run=True)
        
        # Test con posizione simulata
        test_position = {
            'entry_price': 2.662,
            'quantity': 12.15,
            'stop_loss': 2.662
        }
        
        test_market = {
            'price': 2.748,
            'atr': 0.05,
            'regime': 'BULL'
        }
        
        result = trader.check_sell_signal('DOTUSDT', test_position, test_market)
        print(f"✅ Test trailing stop: {result}")
        
        trailing_info = trader.get_trailing_info('DOTUSDT')
        print(f"📊 Trailing info: {trailing_info}")
        
        return
    
    # Avvio normale
    trader = QuantumTraderV31(initial_capital=args.capital, dry_run=args.dry_run)
    
    print("\n🚀 QUANTUM TRADER V3.1 - TRAILING STOP EDITION")
    print("=" * 55)
    print("✅ Sistema originale: INTEGRO")
    print("✅ Trailing Stop: ATTIVO")
    print("✅ Protezione profitti: ATTIVA")
    print("=" * 55)
    
    trader.run()

if __name__ == "__main__":
    main()

    # ========== MAIN LOOP ==========
    trader = QuantumTraderV31(
        dry_run=args.dry_run,
        initial_capital=args.capital
    )
    
    print(f"\n🚀 Starting Quantum V3.1 Trader")
    print(f"💰 Capital: ${args.capital}")
    print(f"🔒 Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print("=" * 50)
    
    cycle_interval = 600  # 10 minuti
    
    try:
        while True:
            try:
                trader.run_cycle()
                
                # Sleep con countdown
                for remaining in range(cycle_interval, 0, -30):
                    print(f"⏳ Next cycle in {remaining}s...", end='\r')
                    time.sleep(30)
                print()  # Newline
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping trader...")
                break
            except Exception as e:
                logging.error(f"❌ Cycle error: {e}")
                print(f"⚠️  Error in cycle: {e}")
                print("🔄 Retrying in 60s...")
                time.sleep(60)
                
    except KeyboardInterrupt:
        print("\n✅ Trader stopped by user")
    finally:
        trader._save_state_safe()
        print("💾 State saved")

if __name__ == '__main__':
    main()

    def check_and_execute_sells(self):
        """
        🆕 METODO MANCANTE: Controlla e esegue vendite
        """
        for symbol in list(self.portfolio.keys()):
            try:
                position = self.portfolio[symbol]
                
                # Get market data
                market_data = {
                    'symbol': symbol,
                    'price': self.api.get_price(symbol),
                    'regime': self.regime_detector.get_regime()
                }
                
                # Check sell signal
                should_sell, reason = self.check_sell_signal(symbol, position, market_data)
                
                if should_sell:
                    logging.info(f"🔴 SELL SIGNAL: {symbol} - {reason}")
                    self.execute_sell(symbol, market_data, reason)
                    
            except Exception as e:
                logging.error(f"❌ Error checking sell for {symbol}: {e}")

#!/usr/bin/env python3
"""
🎯 QUANTUM V3.1 FIXED - Con trailing stop E vendite funzionanti
Fix: Aggiunge il ciclo di vendita mancante
"""

from quantum_v31_wrapper import QuantumTraderV31
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class QuantumV31Fixed(QuantumTraderV31):
    """
    Versione fixed che aggiunge il ciclo di vendita mancante
    """
    
    def run_cycle_fixed(self):
        """
        Ciclo completo con:
        1. Check vendite (con trailing stop)
        2. Check acquisti
        """
        try:
            # 1. PRIMA: Controlla vendite (CRITICO!)
            self._check_and_execute_sells()
            
            # 2. POI: Esegui il ciclo originale (acquisti, etc)
            super().run()
            
        except Exception as e:
            logging.error(f"❌ Errore nel ciclo: {e}")
            raise
    
    def _check_and_execute_sells(self):
        """
        Controlla tutte le posizioni aperte per vendite
        Include trailing stop logic
        """
        if not self.portfolio:
            return
            
        logging.info(f"🔍 Checking SELL signals for {len(self.portfolio)} positions...")
        
        for symbol in list(self.portfolio.keys()):
            try:
                position = self.portfolio[symbol]
                
                # Get current market data
                current_price = self.api.get_price(symbol)
                
                market_data = {
                    'symbol': symbol,
                    'price': current_price,
                    'regime': getattr(self, 'regime_detector', None).get_regime() if hasattr(self, 'regime_detector') else 'NEUTRAL'
                }
                
                # Check sell signal (usa il metodo del wrapper con trailing stop)
                should_sell, reason = self.check_sell_signal(symbol, position, market_data)
                
                if should_sell:
                    logging.info(f"🔴 SELL SIGNAL: {symbol} - {reason}")
                    logging.info(f"   Entry: ${position['entry_price']:.3f} | Current: ${current_price:.3f}")
                    
                    # Esegui vendita
                    self.execute_sell(symbol, market_data, reason)
                    
                    # Salva state dopo vendita
                    self._save_state_safe()
                    
            except Exception as e:
                logging.error(f"❌ Error checking sell for {symbol}: {e}")
                import traceback
                traceback.print_exc()


def main():
    """Main function con loop corretto"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quantum Trader V3.1 FIXED')
    parser.add_argument('--capital', type=float, default=200, help='Initial capital')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    args = parser.parse_args()
    
    # Crea trader fixed
    trader = QuantumV31Fixed(
        initial_capital=args.capital,
        dry_run=args.dry_run
    )
    
    print("\n" + "="*60)
    print("🚀 QUANTUM TRADER V3.1 FIXED - STARTING")
    print("="*60)
    print("✅ Trailing Stop: ATTIVO")
    print("✅ Vendite automatiche: ATTIVE")
    print("✅ Risk Management: ATTIVO")
    print(f"💰 Capital: ${args.capital}")
    print(f"🔒 Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print("="*60 + "\n")
    
    cycle_interval = 600  # 10 minuti
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            
            print(f"\n{'='*60}")
            print(f"🎯 CYCLE {cycle_count} - {time.strftime('%H:%M:%S')}")
            print(f"{'='*60}")
            
            try:
                # Esegui ciclo fixed (con vendite!)
                trader.run_cycle_fixed()
                
                print(f"\n✅ Cycle {cycle_count} completed")
                
                # Sleep con countdown
                print(f"⏳ Next cycle in {cycle_interval}s...")
                for remaining in range(cycle_interval, 0, -60):
                    print(f"   {remaining}s remaining...", end='\r')
                    time.sleep(60)
                print()
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping trader...")
                break
                
            except Exception as e:
                logging.error(f"❌ Cycle error: {e}")
                print(f"⚠️  Error in cycle: {e}")
                print("🔄 Retrying in 60s...")
                time.sleep(60)
                
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("✅ Trader stopped by user")
        print("="*60)
        
    finally:
        # Salva state finale
        trader._save_state_safe()
        print("💾 Final state saved")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"   Total cycles: {cycle_count}")
        print(f"   Final balance: ${trader.cash_balance:.2f}")
        print(f"   Positions: {len(trader.portfolio)}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Quick test of V3.1 logic"""

import sys
sys.path.insert(0, '/home/orenzo/trading_project/QuantumTradingSystem')

from quantum_v31_complete import QuantumTradingV31

def test_single_cycle():
    print("\n🧪 TESTING QUANTUM V3.1 - SINGLE CYCLE\n")
    
    try:
        bot = QuantumTradingV31(dry_run=True)
        print("✅ Bot initialized successfully")
        print("\n🔄 Running ONE cycle...\n")
        
        bot.run_cycle()
        
        print("\n✅ Test completed successfully!")
        print(f"   Cash: ${bot.cash:.2f}")
        print(f"   Positions: {len(bot.portfolio)}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_cycle()

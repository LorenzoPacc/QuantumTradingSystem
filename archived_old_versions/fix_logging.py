#!/usr/bin/env python3

with open('quantum_v3_enhanced.py', 'r') as f:
    content = f.read()

# Trova e sostituisci check_buy_signal per aggiungere logging
old_check_buy = '''    def check_buy_signal(self, market_data: Dict, fear_greed: int) -> Tuple[bool, str]:
        """Controlla condizioni BUY usando SmartTradingEngine"""
        try:
            total_value = self.cash_balance
            if self.positions and '5m' in market_data:
                for p in self.positions.values():
                    total_value += p['quantity'] * market_data['5m']['price']
            
            should_buy, reason, metadata = self.smart_engine.generate_buy_signal(
                market_data=market_data,
                fear_greed=fear_greed,
                cash_balance=self.cash_balance,
                positions=self.positions,
                total_value=total_value
            )
            
            if should_buy:
                logging.info(f"✅ BUY Signal: {reason}")
            
            return should_buy, reason
        except Exception as e:
            logging.error(f"Error check_buy_signal: {e}")
            return False, str(e)'''

new_check_buy = '''    def check_buy_signal(self, market_data: Dict, fear_greed: int) -> Tuple[bool, str]:
        """Controlla condizioni BUY usando SmartTradingEngine"""
        try:
            total_value = self.cash_balance
            if self.positions and '5m' in market_data:
                for p in self.positions.values():
                    total_value += p['quantity'] * market_data['5m']['price']
            
            should_buy, reason, metadata = self.smart_engine.generate_buy_signal(
                market_data=market_data,
                fear_greed=fear_greed,
                cash_balance=self.cash_balance,
                positions=self.positions,
                total_value=total_value
            )
            
            if should_buy:
                logging.info(f"✅ BUY Signal: {reason}")
                logging.debug(f"Metadata: {metadata}")
            else:
                logging.info(f"❌ No BUY: {reason}")
                if metadata:
                    logging.debug(f"Details: {metadata}")
            
            return should_buy, reason
        except Exception as e:
            logging.error(f"Error check_buy_signal: {e}")
            return False, str(e)'''

content = content.replace(old_check_buy, new_check_buy)

with open('quantum_v3_enhanced.py', 'w') as f:
    f.write(content)

print("✅ Logging added to check_buy_signal")

# Test sintassi
import py_compile
try:
    py_compile.compile('quantum_v3_enhanced.py', doraise=True)
    print("✅ Syntax OK")
except Exception as e:
    print(f"❌ Error: {e}")


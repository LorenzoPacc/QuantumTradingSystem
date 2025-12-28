#!/usr/bin/env python3
"""
Safe patch per quantum_v3_enhanced.py
Applica modifiche senza rompere la sintassi
"""

import re

def safe_patch():
    with open('quantum_v3_enhanced.py', 'r') as f:
        content = f.read()
    
    original_content = content
    patches_applied = []
    
    # ========================================================================
    # PATCH 1: Import SmartTradingEngine
    # ========================================================================
    if 'from quantum_smart_improvements import SmartTradingEngine' not in content:
        # Trova "import logging" e aggiungi dopo
        content = content.replace(
            'import logging',
            'import logging\nfrom quantum_smart_improvements import SmartTradingEngine'
        )
        patches_applied.append("✅ Import SmartTradingEngine")
    
    # ========================================================================
    # PATCH 2: Inizializza SmartEngine
    # ========================================================================
    if 'self.smart_engine = SmartTradingEngine' not in content:
        content = content.replace(
            'self.api = AdvancedBinanceAPI()',
            'self.api = AdvancedBinanceAPI()\n        self.smart_engine = SmartTradingEngine(logging.getLogger(__name__))'
        )
        patches_applied.append("✅ SmartEngine inizializzato")
    
    # ========================================================================
    # PATCH 3-4: Sostituisci COMPLETAMENTE get_market_data
    # ========================================================================
    # Pattern per trovare il metodo completo (più robusto)
    pattern = r'(    def get_market_data\(self, symbol: str\)[^\n]*\n)(.*?)((?=\n    def )|(?=\nclass )|(?=\Z))'
    
    new_get_market_data = '''    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """Recupera dati di mercato con analisi multi-timeframe"""
        try:
            price = self.api.get_price(symbol)
            if not price:
                return None
            
            # Day Trading: 5m, 15m, 1h
            klines_5m = self.api.get_klines(symbol, '5m', 288)
            klines_15m = self.api.get_klines(symbol, '15m', 96)
            klines_1h = self.api.get_klines(symbol, '1h', 48)
            
            if not klines_5m or not klines_15m or not klines_1h:
                return None
            
            # Calcola closes per ogni timeframe
            closes_5m = [k['close'] for k in klines_5m]
            closes_15m = [k['close'] for k in klines_15m]
            closes_1h = [k['close'] for k in klines_1h]
            
            # Struttura multi-timeframe
            return {
                '5m': {
                    'price': price,
                    'rsi': TechnicalIndicators.rsi(closes_5m, 14),
                    'sma_fast': TechnicalIndicators.sma(closes_5m, 10),
                    'sma_slow': TechnicalIndicators.sma(closes_5m, 30),
                    'atr': TechnicalIndicators.atr(klines_5m, 14),
                    'volume': klines_5m[-1]['volume'] if klines_5m else 0,
                    'klines': klines_5m,
                },
                '15m': {
                    'price': price,
                    'rsi': TechnicalIndicators.rsi(closes_15m, 14),
                    'sma_fast': TechnicalIndicators.sma(closes_15m, 10),
                    'sma_slow': TechnicalIndicators.sma(closes_15m, 30),
                    'atr': TechnicalIndicators.atr(klines_15m, 14),
                    'volume': klines_15m[-1]['volume'] if klines_15m else 0,
                    'klines': klines_15m,
                },
                '1h': {
                    'price': price,
                    'rsi': TechnicalIndicators.rsi(closes_1h, 14),
                    'sma_fast': TechnicalIndicators.sma(closes_1h, 10),
                    'sma_slow': TechnicalIndicators.sma(closes_1h, 30),
                    'atr': TechnicalIndicators.atr(klines_1h, 14),
                    'volume': klines_1h[-1]['volume'] if klines_1h else 0,
                    'regime': MarketRegimeDetector.detect_regime(klines_1h[-30:] if len(klines_1h) >= 30 else klines_1h),
                    'klines': klines_1h,
                }
            }
        except Exception as e:
            logging.error(f"Errore get_market_data {symbol}: {e}")
            return None

'''
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content[:match.start()] + new_get_market_data + content[match.end():]
        patches_applied.append("✅ get_market_data aggiornato")
    
    # ========================================================================
    # PATCH 5: Sostituisci check_buy_signal
    # ========================================================================
    pattern_buy = r'(    def check_buy_signal\(self, market_data: Dict, fear_greed: int\)[^\n]*\n)(.*?)((?=\n    def )|(?=\nclass )|(?=\Z))'
    
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
            
            return should_buy, reason
        except Exception as e:
            logging.error(f"Error check_buy_signal: {e}")
            return False, str(e)

'''
    
    match_buy = re.search(pattern_buy, content, re.DOTALL)
    if match_buy:
        content = content[:match_buy.start()] + new_check_buy + content[match_buy.end():]
        patches_applied.append("✅ check_buy_signal aggiornato")
    
    # ========================================================================
    # PATCH 6: Sostituisci check_sell_signal
    # ========================================================================
    pattern_sell = r'(    def check_sell_signal\(self, symbol: str, position: Dict, market_data: Dict\)[^\n]*\n)(.*?)((?=\n    def )|(?=\nclass )|(?=\Z))'
    
    new_check_sell = '''    def check_sell_signal(self, symbol: str, position: Dict, market_data: Dict) -> Tuple[bool, str]:
        """Controlla condizioni SELL usando SmartExit"""
        try:
            if '5m' in market_data:
                position['current_price'] = market_data['5m']['price']
            
            should_exit, reason = self.smart_engine.smart_exit.check_exit_signal(
                position=position,
                market_data=market_data
            )
            
            if should_exit:
                logging.info(f"✅ SELL Signal {symbol}: {reason}")
            
            return should_exit, reason
        except Exception as e:
            logging.error(f"Error check_sell_signal {symbol}: {e}")
            return False, str(e)

'''
    
    match_sell = re.search(pattern_sell, content, re.DOTALL)
    if match_sell:
        content = content[:match_sell.start()] + new_check_sell + content[match_sell.end():]
        patches_applied.append("✅ check_sell_signal aggiornato")
    
    # ========================================================================
    # Salva solo se ci sono modifiche
    # ========================================================================
    if content != original_content:
        with open('quantum_v3_enhanced.py', 'w') as f:
            f.write(content)
        
        print("🔧 PATCH APPLICATE:")
        for patch in patches_applied:
            print(f"  {patch}")
        
        return True
    else:
        print("⚠️  Nessuna modifica applicata")
        return False

if __name__ == "__main__":
    success = safe_patch()
    
    # Test sintassi
    print("\n🧪 Test sintassi Python...")
    import py_compile
    try:
        py_compile.compile('quantum_v3_enhanced.py', doraise=True)
        print("✅ Sintassi corretta!")
    except py_compile.PyCompileError as e:
        print(f"❌ Errore sintassi: {e}")
        exit(1)


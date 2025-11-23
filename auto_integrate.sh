#!/bin/bash

echo "🔧 AUTO-INTEGRATION QUANTUM SMART V3"
echo "===================================="
echo ""

# Backup pre-modifica
cp quantum_v3_enhanced.py quantum_v3_enhanced.py.pre-patch

echo "📝 Applicazione patch a quantum_v3_enhanced.py..."

# Crea il file patchato
python3 << 'PYTHON_PATCH'
import re

# Leggi il file originale
with open('quantum_v3_enhanced.py', 'r') as f:
    content = f.read()

# ============================================================================
# PATCH 1: Aggiungi import SmartTradingEngine
# ============================================================================
if 'from quantum_smart_improvements import SmartTradingEngine' not in content:
    # Trova la posizione dopo gli import esistenti (dopo "import logging")
    import_pos = content.find('import logging')
    if import_pos != -1:
        # Trova la fine della riga
        newline_pos = content.find('\n', import_pos)
        # Inserisci il nuovo import
        content = (
            content[:newline_pos+1] + 
            'from quantum_smart_improvements import SmartTradingEngine\n' +
            content[newline_pos+1:]
        )
        print("✅ PATCH 1: Import SmartTradingEngine aggiunto")
    else:
        print("⚠️  PATCH 1: Posizione import non trovata")
else:
    print("✅ PATCH 1: Import già presente")

# ============================================================================
# PATCH 2: Inizializza SmartEngine in __init__
# ============================================================================
if 'self.smart_engine = SmartTradingEngine' not in content:
    # Trova self.api = AdvancedBinanceAPI()
    api_init = content.find('self.api = AdvancedBinanceAPI()')
    if api_init != -1:
        newline_pos = content.find('\n', api_init)
        content = (
            content[:newline_pos+1] +
            '        self.smart_engine = SmartTradingEngine(logging.getLogger(__name__))\n' +
            content[newline_pos+1:]
        )
        print("✅ PATCH 2: SmartEngine inizializzato")
    else:
        print("⚠️  PATCH 2: Posizione __init__ non trovata")
else:
    print("✅ PATCH 2: SmartEngine già inizializzato")

# ============================================================================
# PATCH 3: Cambia timeframes in get_market_data
# ============================================================================
# Cerca il pattern dei klines vecchi
old_klines_pattern = r"klines_1h = self\.api\.get_klines\(symbol, '1h', \d+\)\s*klines_1d = self\.api\.get_klines\(symbol, '1d', \d+\)"

new_klines = """# Day Trading: 5m, 15m, 1h
        klines_5m = self.api.get_klines(symbol, '5m', 288)   # 24h di dati
        klines_15m = self.api.get_klines(symbol, '15m', 96)  # 24h di dati
        klines_1h = self.api.get_klines(symbol, '1h', 48)    # 48h di dati
        
        if not klines_5m or not klines_15m or not klines_1h:
            return None"""

if re.search(old_klines_pattern, content):
    content = re.sub(old_klines_pattern, new_klines, content)
    print("✅ PATCH 3: Timeframes aggiornati (5m, 15m, 1h)")
elif 'klines_5m = self.api.get_klines' in content:
    print("✅ PATCH 3: Timeframes già aggiornati")
else:
    print("⚠️  PATCH 3: Pattern klines non trovato")

# ============================================================================
# PATCH 4: Struttura dati multi-timeframe
# ============================================================================
# Cerca e sostituisci il return del get_market_data

old_return_pattern = r"closes_1h = \[k\['close'\] for k in klines_1h\].*?return \{[^}]+\}"

new_return = """# Calcola closes per ogni timeframe
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
        }"""

if re.search(old_return_pattern, content, re.DOTALL):
    content = re.sub(old_return_pattern, new_return, content, flags=re.DOTALL)
    print("✅ PATCH 4: Struttura multi-timeframe applicata")
elif "'5m': {" in content and "'15m': {" in content:
    print("✅ PATCH 4: Struttura multi-timeframe già presente")
else:
    print("⚠️  PATCH 4: Pattern return non trovato - applicazione manuale richiesta")

# ============================================================================
# PATCH 5: Nuovo check_buy_signal con SmartEngine
# ============================================================================
new_check_buy = '''    def check_buy_signal(self, market_data: Dict, fear_greed: int) -> Tuple[bool, str]:
        """
        Controlla se ci sono condizioni per BUY usando SmartTradingEngine
        """
        try:
            # Calcola total value
            total_value = self.cash_balance
            if self.positions and '5m' in market_data:
                for p in self.positions.values():
                    total_value += p['quantity'] * market_data['5m']['price']
            
            # Usa il motore smart per generare il segnale
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
                logging.debug(f"❌ No BUY: {reason}")
            
            return should_buy, reason
            
        except Exception as e:
            logging.error(f"Error in check_buy_signal: {e}")
            return False, str(e)'''

# Trova e sostituisci il metodo check_buy_signal
pattern_buy = r'def check_buy_signal\(self, market_data: Dict, fear_greed: int\)[^:]+:.*?(?=\n    def |\nclass |\Z)'

if re.search(pattern_buy, content, re.DOTALL):
    content = re.sub(pattern_buy, new_check_buy + '\n', content, flags=re.DOTALL)
    print("✅ PATCH 5: check_buy_signal aggiornato")
elif 'self.smart_engine.generate_buy_signal' in content:
    print("✅ PATCH 5: check_buy_signal già aggiornato")
else:
    print("⚠️  PATCH 5: Metodo check_buy_signal non trovato")

# ============================================================================
# PATCH 6: Nuovo check_sell_signal con SmartExit
# ============================================================================
new_check_sell = '''    def check_sell_signal(self, symbol: str, position: Dict, market_data: Dict) -> Tuple[bool, str]:
        """
        Controlla se ci sono condizioni per SELL usando SmartExit
        """
        try:
            # Aggiorna current_price nella posizione
            if '5m' in market_data:
                position['current_price'] = market_data['5m']['price']
            
            # Usa SmartExit per verificare uscita
            should_exit, reason = self.smart_engine.smart_exit.check_exit_signal(
                position=position,
                market_data=market_data
            )
            
            if should_exit:
                logging.info(f"✅ SELL Signal for {symbol}: {reason}")
            
            return should_exit, reason
            
        except Exception as e:
            logging.error(f"Error in check_sell_signal for {symbol}: {e}")
            return False, str(e)'''

pattern_sell = r'def check_sell_signal\(self, symbol: str, position: Dict, market_data: Dict\)[^:]+:.*?(?=\n    def |\nclass |\Z)'

if re.search(pattern_sell, content, re.DOTALL):
    content = re.sub(pattern_sell, new_check_sell + '\n', content, flags=re.DOTALL)
    print("✅ PATCH 6: check_sell_signal aggiornato")
elif 'self.smart_engine.smart_exit.check_exit_signal' in content:
    print("✅ PATCH 6: check_sell_signal già aggiornato")
else:
    print("⚠️  PATCH 6: Metodo check_sell_signal non trovato")

# ============================================================================
# Salva il file modificato
# ============================================================================
with open('quantum_v3_enhanced.py', 'w') as f:
    f.write(content)

print("\n✅ File quantum_v3_enhanced.py aggiornato!")
print("📝 Backup salvato in: quantum_v3_enhanced.py.pre-patch")

PYTHON_PATCH

echo ""
echo "===================================="
echo "✅ AUTO-INTEGRATION COMPLETATA!"
echo "===================================="
echo ""
echo "📋 Prossimi passi:"
echo "  1. ./verify_integration.sh"
echo "  2. ./test_smart_bot.sh"

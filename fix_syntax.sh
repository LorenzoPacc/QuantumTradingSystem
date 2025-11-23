#!/bin/bash

echo "🔧 FIX SYNTAX ERROR"
echo "==================="

python3 << 'PYTHON_FIX'
# Leggi il file
with open('quantum_v3_enhanced.py', 'r') as f:
    lines = f.readlines()

# Trova la riga con l'errore (circa riga 318)
fixed_lines = []
in_get_market_data = False
found_try = False

for i, line in enumerate(lines, 1):
    # Identifica il metodo get_market_data
    if 'def get_market_data(self, symbol: str)' in line:
        in_get_market_data = True
        fixed_lines.append(line)
        continue
    
    # Cerca il blocco try all'interno di get_market_data
    if in_get_market_data and 'try:' in line and not found_try:
        found_try = True
        fixed_lines.append(line)
        continue
    
    # Se troviamo i klines dopo un try, assicuriamoci che ci sia il blocco except
    if found_try and 'klines_5m = self.api.get_klines' in line:
        # Verifiamo che non ci sia già un except
        # Cerchiamo nelle prossime righe
        needs_except = True
        for j in range(i, min(i+30, len(lines))):
            if 'except' in lines[j]:
                needs_except = False
                break
            if 'def ' in lines[j] and j > i:  # Nuovo metodo = fine blocco
                break
        
        if needs_except:
            # Aggiungi questa riga e poi costruisci il blocco try-except corretto
            print(f"⚠️  Trovato blocco try senza except alla riga {i}")
            print("🔧 Applicazione fix...")
        
        found_try = False
        in_get_market_data = False
    
    fixed_lines.append(line)

# Strategia alternativa: ricostruiamo il metodo get_market_data completo
print("🔧 Ricostruzione metodo get_market_data...")

# Trova inizio e fine del metodo
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if 'def get_market_data(self, symbol: str)' in line:
        start_idx = i
    elif start_idx is not None and line.strip().startswith('def ') and i > start_idx:
        end_idx = i
        break

if start_idx is not None:
    if end_idx is None:
        end_idx = len(lines)
    
    print(f"✅ Metodo trovato: righe {start_idx+1} - {end_idx}")
    
    # Nuovo metodo corretto
    new_method = '''    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """Recupera dati di mercato con analisi multi-timeframe"""
        try:
            price = self.api.get_price(symbol)
            if not price:
                return None
            
            # Day Trading: 5m, 15m, 1h
            klines_5m = self.api.get_klines(symbol, '5m', 288)   # 24h di dati
            klines_15m = self.api.get_klines(symbol, '15m', 96)  # 24h di dati
            klines_1h = self.api.get_klines(symbol, '1h', 48)    # 48h di dati
            
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
    
    # Ricostruisci il file
    new_content = ''.join(lines[:start_idx]) + new_method + ''.join(lines[end_idx:])
    
    # Salva
    with open('quantum_v3_enhanced.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Metodo get_market_data ricostruito correttamente")
else:
    print("❌ Metodo get_market_data non trovato!")

PYTHON_FIX

echo ""
echo "✅ FIX COMPLETATO"
echo ""
echo "Verifica sintassi:"
python3 -m py_compile quantum_v3_enhanced.py && echo "✅ Sintassi OK" || echo "❌ Ancora errori"


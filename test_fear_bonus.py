import sys
import os
sys.path.append(os.getcwd())

try:
    # Importa il trader
    exec(open('quantum_v33_ultimate_final.py').read())
    
    trader = QuantumTrader()
    print("🧪 Test FEAR BONUS nella funzione check_buy...")
    
    # Estrai il codice della funzione
    with open('quantum_v33_ultimate_final.py', 'r') as f:
        content = f.read()
        
    # Trova la funzione check_buy
    import re
    pattern = r'def check_buy\(self, symbol\):.*?def check_sell'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        func_code = match.group(0)
        print(f"✅ Funzione check_buy trovata ({len(func_code)} chars)")
        
        # Cerca Fear Bonus nel codice
        if 'fear_index < 30' in func_code:
            print("✅ Rilevato controllo Extreme Fear")
        else:
            print("❌ NON trovo controllo Extreme Fear!")
            
        if 'confidence * 1.25' in func_code or 'confidence *= 1.25' in func_code:
            print("✅ Rilevato bonus +25%")
        else:
            print("❌ NON trovo bonus +25%!")
            
        if 'confidence >= 40.0' in func_code:
            print("✅ Rilevato auto-buy a 40%")
        else:
            print("❌ NON trovo auto-buy a 40%!")
            
        # Mostra le linee chiave
        print("\n📋 SEZIONI CHIAVE:")
        lines = func_code.split('\n')
        for i, line in enumerate(lines):
            if 'fear' in line.lower() or 'confidence' in line.lower() or 'bonus' in line.lower():
                print(f"   {i:3}: {line.strip()[:80]}")
    else:
        print("❌ Non riesco a trovare la funzione check_buy!")
        
    print("\n🔍 Test chiamata reale...")
    # Forza fear index basso per test
    import types
    
    # Monkey patch per forzare extreme fear
    original_get_fear = trader.get_fear_greed_index
    trader.get_fear_greed_index = lambda: 25  # Extreme Fear
    
    result, info = trader.check_buy("BTCUSDT")
    print(f"✅ Risultato check_buy: {result}")
    print(f"📊 Info: {info}")
    
    if isinstance(info, dict):
        print(f"   Confidence: {info.get('confidence', 'N/A')}%")
        print(f"   Fear Index: {info.get('fear_index', 'N/A')}")
        
        if info.get('confidence', 0) >= 40:
            print("🚀 FEAR BONUS FUNZIONA! Confidence > 40%")
        else:
            print(f"❌ Confidence solo {info.get('confidence', 0)}% - Fear Bonus non applicato?")
    
except Exception as e:
    print(f"❌ Errore: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

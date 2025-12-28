"""
PATCH v3.3 REGIME FIX
Integra i nuovi moduli nel bot principale
"""

import sys
import os
import importlib.util

# Importa i nuovi moduli
try:
    # Import regime detection
    regime_spec = importlib.util.spec_from_file_location(
        "regime_detection", 
        "/home/orenzo/trading_project/QuantumTradingSystem/regime_detection.py"
    )
    regime_module = importlib.util.module_from_spec(regime_spec)
    regime_spec.loader.exec_module(regime_module)
    
    # Import dip buy module
    dip_spec = importlib.util.spec_from_file_location(
        "dip_buy_module",
        "/home/orenzo/trading_project/QuantumTradingSystem/dip_buy_module.py"
    )
    dip_module = importlib.util.module_from_spec(dip_spec)
    dip_spec.loader.exec_module(dip_module)
    
    print("✅ Moduli patch caricati con successo")
except Exception as e:
    print(f"⚠️  Errore nel caricare moduli patch: {e}")
    regime_module = None
    dip_module = None

def apply_patch_to_trader():
    """
    Applica le patch al trader principale
    """
    original_file = "/home/orenzo/trading_project/QuantumTradingSystem/quantum_v33_ultimate_final.py"
    
    with open(original_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Aggiungi import dei nuovi moduli all'inizio
    if "import regime_detection" not in content:
        # Trova la sezione imports
        import_section = "import ccxt"
        new_imports = '''import sys
import os

# REGIME DETECTION PATCH
try:
    from regime_detection import detect_market_regime, get_position_size_based_on_regime
    from dip_buy_module import check_dip_buy_signal, calculate_dip_scaling
    PATCH_ACTIVE = True
    print("✅ REGIME PATCH v1.0 ATTIVA - Mercato: Extreme Fear")
except ImportError as e:
    PATCH_ACTIVE = False
    print(f"⚠️  Regime patch non disponibile: {e}")
    
'''
        content = content.replace(import_section, new_imports + import_section)
    
    # 2. Modifica la funzione analyze_symbol per usare regime detection
    analyze_symbol_pattern = "def analyze_symbol"
    if analyze_symbol_pattern in content and "regime_info = detect_market_regime" not in content:
        # Aggiungi regime detection all'analisi
        regime_injection = '''
        # === REGIME DETECTION PATCH ===
        try:
            if PATCH_ACTIVE:
                regime_info = detect_market_regise(df, fear_greed, close_prices[-1])
                print(f"   Regime: {regime_info['regime']} ({regime_info['confidence']:.1%}) - {regime_info['action']}")
                
                # Override decisione basata sul regime
                if regime_info['action'] in ['BUY_ACCUMULATE', 'BUY_TREND', 'BUY_REVERSION']:
                    if signal == 'HOLD' or signal == 'SELL':
                        signal = 'BUY'
                        buy_signal_strength = max(buy_signal_strength, regime_info['confidence'])
                        
                elif regime_info['action'] == 'AVOID_LONG':
                    if signal == 'BUY':
                        signal = 'HOLD'
                        print(f"   ⚠️  Regime OVERRIDE: Evita long in downtrend")
        except Exception as e:
            print(f"   ⚠️  Regime patch error: {e}")
        # === FINE PATCH ===
        '''
        
        # Trova la fine della funzione analyze_symbol
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "return {" in line and "signal" in lines[i-1]:
                # Inietta prima del return
                lines.insert(i, regime_injection)
                content = '\n'.join(lines)
                break
    
    # 3. Modifica execute_buy per usare position sizing dinamico
    execute_buy_pattern = "def execute_buy"
    if execute_buy_pattern in content and "dip_signal = check_dip_buy_signal" not in content:
        # Inietta dip buy logic
        dip_injection = '''
        # === DIP BUY PATCH ===
        try:
            if PATCH_ACTIVE:
                # Controlla segnale dip buy
                dip_signal = check_dip_buy_signal(
                    df=symbol_data,
                    fear_greed=fear_greed,
                    current_price=price,
                    portfolio_cash=self.portfolio.cash,
                    position_count=len(self.portfolio.positions),
                    max_positions=self.max_positions
                )
                
                if dip_signal:
                    print(f"🎯 DIP BUY SIGNAL DETECTED!")
                    print(f"   Signal: {dip_signal['signal']}")
                    print(f"   Reason: {dip_signal['reason']}")
                    print(f"   Confidence: {dip_signal['confidence']:.1%}")
                    
                    # Override size con dip sizing
                    size = min(dip_signal['size'], self.portfolio.cash * 0.3)
                    
                    # Override SL/TP se forniti
                    if dip_signal.get('stoploss_pct'):
                        stop_loss_pct = dip_signal['stoploss_pct']
                    if dip_signal.get('takeprofit_pct'):
                        take_profit_pct = dip_signal['takeprofit_pct']
                    
                    print(f"   DIP Size: ${size:.2f} ({(size/self.portfolio.cash*100):.1f}% of cash)")
        except Exception as e:
            print(f"⚠️  Dip buy patch error: {e}")
        # === FINE PATCH ===
        '''
        
        # Trova la linea con "size =" in execute_buy
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "def execute_buy" in line:
                # Cerca la linea del size
                for j in range(i, min(i+50, len(lines))):
                    if "size =" in lines[j] and "portfolio_cash" in lines[j]:
                        # Inietta dopo la linea del size
                        lines.insert(j+1, dip_injection)
                        content = '\n'.join(lines)
                        break
                break
    
    # 4. Aggiungi report regime all'inizio di ogni ciclo
    cycle_start_pattern = "CYCLE "
    if cycle_start_pattern in content and "MARKET REGIME REPORT" not in content:
        regime_report = '''
        # === MARKET REGIME REPORT ===
        try:
            if PATCH_ACTIVE:
                # Analisi regime globale basata su BTC
                btc_data = self.get_symbol_data('BTC/USDT')
                if btc_data is not None and len(btc_data) > 50:
                    regime_info = detect_market_regime(btc_data, fear_greed)
                    
                    print("📊 MARKET REGIME REPORT:")
                    print(f"   Regime: {regime_info['regime']}")
                    print(f"   Action: {regime_info['action']}")
                    print(f"   Confidence: {regime_info['confidence']:.1%}")
                    print(f"   Reason: {regime_info['reason']}")
                    
                    # Logica speciale per extreme fear
                    if regime_info['regime'] == 'PANIC_CAPITULATION':
                        print("🚨 ULTIMATE FEAR DETECTED! BUY THE DIP OPPORTUNITY!")
                        print("   Strategy: Accumulate gradually")
                        print("   Target: 2-3 positions max")
                        # Riduci threshold per buy
                        self.fear_greed_threshold = 35  # Più aggressivo
        except Exception as e:
            print(f"⚠️  Market regime report error: {e}")
        # === FINE REPORT ===
        '''
        
        # Inietta dopo il log del ciclo
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "CYCLE " in line and " - " in line:
                # Inietta dopo 2 righe
                lines.insert(i+2, regime_report)
                content = '\n'.join(lines)
                break
    
    # Salva il file patchato
    patched_file = original_file.replace('.py', '_PATCHED.py')
    with open(patched_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Patch applicata: {patched_file}")
    print(f"📋 Differenze principali:")
    print(f"   1. Regime detection integrato")
    print(f"   2. Buy the dip module attivo")
    print(f"   3. Position sizing dinamico")
    print(f"   4. Market regime report ogni ciclo")
    
    return patched_file

if __name__ == "__main__":
    patched_file = apply_patch_to_trader()
    print(f"\n🚀 PER AVVIARE IL BOT PATCHATO:")
    print(f"   cp {patched_file} quantum_v33_ultimate_final.py")
    print(f"   ~/qrestart")


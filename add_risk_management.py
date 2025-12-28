#!/usr/bin/env python3
"""
Aggiunge stop-loss e take-profit migliori
"""

risk_management = '''
    def calculate_stop_loss(self, entry_price, rsi, volatility):
        """
        Calcola stop-loss dinamico basato su RSI e volatilità
        """
        # Base stop-loss: -3%
        base_sl = 0.03
        
        # Se RSI molto basso (< 30), rischio di ulteriore calo
        if rsi < 30:
            base_sl = 0.04  # -4%
        elif rsi < 40:
            base_sl = 0.035  # -3.5%
        
        # Aggiusta per volatilità
        if volatility > 0.05:  # Alta volatilità
            base_sl *= 1.2
        
        stop_loss_price = entry_price * (1 - base_sl)
        return round(stop_loss_price, 8)
    
    def calculate_take_profit(self, entry_price, rsi, confidence):
        """
        Take-profit dinamico basato su confidence
        """
        # Base take-profit: +4%
        base_tp = 0.04
        
        # Se confidence alta, target più ambizioso
        if confidence > 70:
            base_tp = 0.06  # +6%
        elif confidence > 60:
            base_tp = 0.05  # +5%
        
        # Se RSI già alto, target conservativo
        if rsi > 60:
            base_tp = 0.03  # +3%
        
        take_profit_price = entry_price * (1 + base_tp)
        return round(take_profit_price, 8)
'''

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Trova dove inserire le nuove funzioni (dopo __init__ o altra funzione)
if 'def check_sell_conditions' in content:
    # Inserisci prima di check_sell_conditions
    insert_pos = content.find('def check_sell_conditions')
    new_content = content[:insert_pos] + risk_management + '\n    ' + content[insert_pos:]
    
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Risk management aggiunto al bot")
else:
    print("⚠️ Funzione di vendita non trovata, salvo in file separato")
    with open('risk_management_module.py', 'w') as f:
        f.write(risk_management)
    print("✅ Salvato in risk_management_module.py")

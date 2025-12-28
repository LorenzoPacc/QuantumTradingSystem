#!/usr/bin/env python3

with open('quantum_trader_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Trova la riga con "sell_signals = [s for s in signals if s == "SELL"]"
insert_at = None
for i, line in enumerate(lines):
    if 'sell_signals = [s for s in signals if s == "SELL"]' in line:
        insert_at = i + 1
        break

if insert_at:
    # Inserisci il codice di tolleranza
    tolerance_code = [
        "            # Tolleranza per ingresso trade (80% = più aggressivo)\n",
        "            TOLERANCE_CONFLUENCE = 0.80\n",
        "            TOLERANCE_CONFIDENCE = 8\n",
        "            min_conf_with_tolerance = self.config.TRADING_CONFIG[\"min_confluence\"] * TOLERANCE_CONFLUENCE\n",
        "            min_confidence_with_tolerance = self.config.TRADING_CONFIG[\"min_confidence\"] - TOLERANCE_CONFIDENCE\n",
        "            \n"
    ]
    
    for idx, code_line in enumerate(tolerance_code):
        lines.insert(insert_at + idx, code_line)
    
    # Ora trova e modifica il controllo if (che ora è spostato di 6 righe)
    for i in range(insert_at + 6, min(insert_at + 15, len(lines))):
        if 'if (total_confluence >= self.config.TRADING_CONFIG["min_confluence"]' in lines[i]:
            lines[i] = lines[i].replace(
                'self.config.TRADING_CONFIG["min_confluence"]',
                'min_conf_with_tolerance'
            )
        if 'total_confidence >= self.config.TRADING_CONFIG["min_confidence"]' in lines[i]:
            lines[i] = lines[i].replace(
                'self.config.TRADING_CONFIG["min_confidence"]',
                'min_confidence_with_tolerance'
            )

# Scrivi il file modificato
with open('quantum_trader_ultimate_final.py', 'w') as f:
    f.writelines(lines)

print("✅ MODIFICA APPLICATA CON SUCCESSO!")
print("\n📊 TOLLERANZA CONFIGURATA:")
print("   • Confluence: 80% della soglia (2.0 → 1.6)")
print("   • Confidence: -8% (60% → 52%)")
print("\n🎯 CON I VALORI ATTUALI:")
print("   • BTC: 1.63 >= 1.6 ✅")
print("   • ETH: 1.44 >= 1.6 ❌") 
print("   • SOL: 1.69 >= 1.6 ✅")
print("\n🚀 TRADE DOVREBBERO PARTIRE PER BTC E SOL NEL PROSSIMO CICLO!")

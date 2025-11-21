with open('quantum_trader_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Trova la riga con sell_signals
insert_at = None
for i, line in enumerate(lines):
    if 'sell_signals = [s for s in signals if s == "SELL"]' in line:
        insert_at = i + 1
        break

if insert_at:
    # Codice da inserire con indentazione corretta (12 spazi)
    new_code = [
        "\n",
        "            # Tolleranza per ingresso trade (70% = molto aggressivo)\n",
        "            TOLERANCE_CONFLUENCE = 0.70\n",
        "            TOLERANCE_CONFIDENCE = 10\n",
        "            min_conf_with_tolerance = self.config.TRADING_CONFIG[\"min_confluence\"] * TOLERANCE_CONFLUENCE\n",
        "            min_confidence_with_tolerance = self.config.TRADING_CONFIG[\"min_confidence\"] - TOLERANCE_CONFIDENCE\n",
        "\n",
        "            # DEBUG\n",
        "            print(f\"🔍 SIGNALS: {signals}\")\n",
        "            print(f\"🔍 BUY={len([s for s in signals if s=='BUY'])} SELL={len([s for s in signals if s=='SELL'])}\")\n",
        "            print(f\"🔍 Conf: {self.config.TRADING_CONFIG.get('min_confluence', 0):.2f} * 0.70 = {min_conf_with_tolerance:.2f}\")\n",
        "\n"
    ]
    
    # Inserisci
    for idx, code_line in enumerate(new_code):
        lines.insert(insert_at + idx, code_line)
    
    # Modifica il controllo if (cerca dopo l'inserimento)
    for i in range(insert_at + len(new_code), min(insert_at + len(new_code) + 15, len(lines))):
        if 'if (total_confluence >= self.config.TRADING_CONFIG["min_confluence"]' in lines[i]:
            lines[i] = '            if (total_confluence >= min_conf_with_tolerance and\n'
        elif 'total_confidence >= self.config.TRADING_CONFIG["min_confidence"]' in lines[i]:
            lines[i] = '                total_confidence >= min_confidence_with_tolerance):\n'

# Scrivi
with open('quantum_trader_ultimate_final.py', 'w') as f:
    f.writelines(lines)

print("✅ Modifica applicata!")

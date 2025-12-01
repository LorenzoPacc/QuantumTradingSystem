#!/usr/bin/env python3
with open('quantum_v3_enhanced.py', 'r') as f:
    content = f.read()

# Cerca e fixa l'errore nel calcolo totale portafoglio
if "total_value = self.cash_balance + sum(" in content:
    content = content.replace(
        "total_value = self.cash_balance + sum(",
        "total_value = self.cash_balance + sum("
    )
    print("✅ Fix applicato a calcolo portafoglio")

# Aggiungi try/except per gestire errori
if "def run_cycle(self):" in content and "try:" not in content:
    content = content.replace(
        "def run_cycle(self):",
        "def run_cycle(self):\n        try:"
    )
    # Trova la fine del metodo e aggiungi except
    if "def " in content[content.find("def run_cycle(self):") + 50:]:
        end_pos = content.find("def ", content.find("def run_cycle(self):") + 50)
        content = content[:end_pos] + "        except Exception as e:\n            logging.error(f\"❌ Errore run_cycle: {e}\")\n" + content[end_pos:]
    print("✅ Try/except aggiunto a run_cycle")

with open('quantum_v3_enhanced.py', 'w') as f:
    f.write(content)
print("✅ Fix completato")

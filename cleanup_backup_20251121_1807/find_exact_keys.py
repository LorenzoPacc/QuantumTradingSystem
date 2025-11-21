print("🔍 Ricerca esatta delle chiavi API...")

with open('quantum_trader_production.py', 'r') as f:
    content = f.read()
    lines = content.split('\n')

print("📋 Controllo variabili globali e di classe...")

# Cerca nelle prime 50 linee per variabili globali
print("\\n🌍 VARIABILI GLOBALI (prime 50 linee):")
for i, line in enumerate(lines[:50]):
    if any(keyword in line for keyword in ['API_KEY', 'API_SECRET', 'api_key', 'api_secret', 'KEY', 'SECRET']):
        print(f"Linea {i+1}: {line.strip()}")

# Cerca nella definizione della classe
print("\\n🏗️  INIZIALIZZAZIONE CLASSE:")
class_start = None
for i, line in enumerate(lines):
    if 'class QuantumAutoTrader' in line:
        class_start = i
        break

if class_start:
    for i in range(class_start, min(class_start + 30, len(lines))):
        if any(keyword in lines[i] for keyword in ['api_key', 'api_secret', 'self.', '__init__']):
            print(f"Linea {i+1}: {lines[i].strip()}")

# Cerca import da altri file
print("\\n📁 IMPORTAZIONI DA ALTRI FILE:")
for i, line in enumerate(lines):
    if any(keyword in line for keyword in ['import', 'from', 'config', '.py']):
        if 'api' in line.lower() or 'key' in line.lower():
            print(f"Linea {i+1}: {line.strip()}")

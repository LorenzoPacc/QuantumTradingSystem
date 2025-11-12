#!/usr/bin/env python3
"""
🚀 QUANTUM SYSTEM FIXED - CARICA STATO
Versione corretta che carica lo stato salvato
"""

import sys
import os
sys.path.append('.')

# Importa e avvia il loader invece del sistema rotto
from quantum_loader import QuantumLoader

print("🚀 QUANTUM SYSTEM FIXED - AVVIATO")
print("✅ Carica stato salvato automaticamente")
print("📊 Dashboard: http://localhost:8090")

if __name__ == "__main__":
    loader = QuantumLoader()
    loader.run()

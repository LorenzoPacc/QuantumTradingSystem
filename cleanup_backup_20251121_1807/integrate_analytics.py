#!/usr/bin/env python3
"""
Integra Performance Analytics in Quantum V3.1
"""

# Verifica che il file esista
import os
if not os.path.exists('quantum_v31_wrapper.py'):
    print("❌ quantum_v31_wrapper.py non trovato!")
    print("   Analytics engine creato, ma non integrato automaticamente")
    print("   Puoi usarlo manualmente con:")
    print("   python3 quantum_performance_analytics.py")
    exit(0)

print("✅ Analytics Engine pronto!")
print("")
print("📊 USO:")
print("   # Report completo ultimi 30 giorni:")
print("   python3 quantum_performance_analytics.py")
print("")
print("   # Report ultimi 7 giorni:")
print("   python3 quantum_performance_analytics.py --days 7")
print("")
print("   # Output JSON:")
print("   python3 quantum_performance_analytics.py --json")
print("")
print("🎯 PROSSIMI STEP:")
print("   1. Lascia girare il bot 3-7 giorni")
print("   2. Esegui analytics per vedere metriche")
print("   3. Decidi ottimizzazioni basate su dati")


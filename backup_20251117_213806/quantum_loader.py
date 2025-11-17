#!/usr/bin/env python3
"""
🚀 QUANTUM LOADER - CARICA STATO AUTOMATICAMENTE
Risolve il problema del bot che non carica lo stato salvato
"""

import json
import time
from quantum_real_perfect import QuantumTraderPerfect

class QuantumLoader:
    def __init__(self):
        self.bot = None
        self.load_state()
    
    def load_state(self):
        """Carica lo stato dal backup o crea nuovo bot"""
        print("🔄 CARICAMENTO STATO BOT...")
        
        try:
            # Prova a caricare il backup
            with open('portfolio_backup.json', 'r') as f:
                backup = json.load(f)
            
            print(f"💾 Backup trovato:")
            print(f"   Cash: ${backup['cash_balance']}")
            print(f"   Posizioni: {len(backup['portfolio'])}")
            print(f"   Ciclo: {backup['cycle_count']}")
            
            # Crea bot e carica stato
            self.bot = QuantumTraderPerfect(200)
            self.bot.cash_balance = backup['cash_balance']
            self.bot.portfolio = backup['portfolio']
            self.bot.cycle_count = backup['cycle_count']
            
            print("✅ Stato caricato dal backup!")
            
        except Exception as e:
            print(f"❌ Errore caricamento backup: {e}")
            print("🆕 Creo nuovo bot...")
            self.bot = QuantumTraderPerfect(200)
        
        print(f"💰 Cash finale: ${self.bot.cash_balance}")
        print(f"📈 Posizioni finali: {len(self.bot.portfolio)}")
        print("")
    
    def run(self):
        """Esegui il bot con cicli visibili"""
        print("🎯 QUANTUM PERFECT TRADER - ATTIVO")
        print("📊 Strategy: Fear & Greed + Stop Loss/TP")
        print("⏰ Cicli ogni 2 minuti (per testing)")
        print("")
        
        cycle_count = self.bot.cycle_count
        
        while True:
            cycle_count += 1
            print("=" * 80)
            print(f"🧠 CICLO {cycle_count} - QUANTUM PERFECT (INIZIO)")
            print("=" * 80)
            
            # Esegui ciclo di trading
            self.bot.execute_trading_cycle()
            
            # Aggiorna ciclo count
            self.bot.cycle_count = cycle_count
            
            # Salva stato dopo ogni ciclo
            self.save_state()
            
            print("=" * 80)
            print(f"✅ CICLO {cycle_count} COMPLETATO")
            print(f"⏳ Prossimo ciclo in 120 secondi...")
            print("")
            
            time.sleep(120)  # 2 minuti per testing
    
    def save_state(self):
        """Salva stato manualmente"""
        try:
            state = {
                'cash_balance': self.bot.cash_balance,
                'portfolio': self.bot.portfolio,
                'cycle_count': self.bot.cycle_count
            }
            with open('portfolio_backup.json', 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"⚠️ Errore salvataggio: {e}")

if __name__ == "__main__":
    loader = QuantumLoader()
    loader.run()

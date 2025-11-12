#!/usr/bin/env python3
"""
🔄 MIGRATION SCRIPT V1 → V2
Migra il portfolio dal sistema V1 al V2
"""

import json
import shutil
import os
from datetime import datetime

def backup_v1_files():
    """Backup completo sistema V1"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    files_to_backup = [
        'portfolio_backup.json',
        'trading_real_performance.db',
        'quantum_v2_state.json'
    ]
    
    print("📦 BACKUP SISTEMA V1")
    print("=" * 50)
    
    for filename in files_to_backup:
        try:
            if os.path.exists(filename):
                backup_name = f"{filename}.backup_{timestamp}"
                shutil.copy(filename, backup_name)
                print(f"✅ {filename} → {backup_name}")
            else:
                print(f"⚠️  {filename} non trovato (skip)")
        except Exception as e:
            print(f"❌ Errore backup {filename}: {e}")
    
    print("=" * 50)

def migrate_portfolio():
    """Migra portfolio da V1 a V2"""
    
    print("\n🔄 MIGRAZIONE PORTFOLIO V1 → V2")
    print("=" * 50)
    
    # 1. Carica V1 state
    try:
        with open('portfolio_backup.json', 'r') as f:
            v1_state = json.load(f)
        
        print(f"✅ V1 State caricato:")
        print(f"   Cash: ${v1_state['cash_balance']:.2f}")
        print(f"   Posizioni: {len(v1_state['portfolio'])}")
        print(f"   Ciclo: {v1_state.get('cycle_count', 0)}")
        
    except FileNotFoundError:
        print("❌ portfolio_backup.json non trovato!")
        print("   Il bot V1 non è mai stato eseguito?")
        return False
    except Exception as e:
        print(f"❌ Errore lettura V1: {e}")
        return False
    
    # 2. Converti formato V1 → V2
    v2_state = {
        'cash_balance': v1_state['cash_balance'],
        'portfolio': {},
        'cycle_count': v1_state.get('cycle_count', 0),
        'timestamp': datetime.now().isoformat(),
        'migrated_from_v1': True
    }
    
    # 3. Migra ogni posizione
    print(f"\n📊 POSIZIONI DA MIGRARE:")
    for symbol, position in v1_state['portfolio'].items():
        v2_state['portfolio'][symbol] = {
            'quantity': position['quantity'],
            'entry_price': position['entry_price'],
            'total_cost': position['total_cost'],
            'entry_time': position.get('entry_time', datetime.now().isoformat()),
            'migrated_from_v1': True
        }
        
        value = position['quantity'] * position['entry_price']
        print(f"   ✅ {symbol}: {position['quantity']:.6f} @ ${position['entry_price']:.2f}")
    
    # 4. Salva V2 state
    try:
        with open('quantum_v2_state.json', 'w') as f:
            json.dump(v2_state, f, indent=2)
        
        print(f"\n✅ MIGRAZIONE COMPLETATA!")
        print(f"   File creato: quantum_v2_state.json")
        
        # 5. Verifica
        total_invested = sum(p['total_cost'] for p in v2_state['portfolio'].values())
        total_capital = v2_state['cash_balance'] + total_invested
        
        print(f"\n💰 VERIFICA FINALE:")
        print(f"   Cash: ${v2_state['cash_balance']:.2f}")
        print(f"   Investito: ${total_invested:.2f}")
        print(f"   Totale: ${total_capital:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore salvataggio V2: {e}")
        return False

def main():
    print("\n" + "="*50)
    print("🔄 QUANTUM TRADER - MIGRATION TOOL")
    print("="*50)
    
    # Chiedi conferma
    print("\n⚠️  ATTENZIONE:")
    print("   Questo script migrerà il portfolio da V1 a V2")
    print("   Verrà creato un backup automatico")
    
    confirm = input("\n▶️  Procedere? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y', 'si', 's']:
        print("❌ Migrazione annullata")
        return
    
    # Step 1: Backup
    backup_v1_files()
    
    # Step 2: Migrazione
    success = migrate_portfolio()
    
    if success:
        print("\n" + "="*50)
        print("🎉 MIGRAZIONE COMPLETATA CON SUCCESSO!")
        print("="*50)
        print("\n🚀 PROSSIMI PASSI:")
        print("   1. Verifica quantum_v2_state.json")
        print("   2. Testa con: python3 quantum_v2_complete.py --dry-run")
        print("   3. Se ok, avvia: python3 quantum_v2_complete.py")
        print("\n💡 TIP: I backup sono in .backup_TIMESTAMP")
    else:
        print("\n❌ Migrazione fallita - controlla gli errori sopra")

if __name__ == "__main__":
    main()

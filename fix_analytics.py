#!/usr/bin/env python3
"""
Fix Analytics per schema database corretto
"""

import sqlite3

print("🔍 ANALISI DATABASE SCHEMA...")
print("="*50)

try:
    conn = sqlite3.connect("quantum_v2_performance.db")
    cursor = conn.cursor()
    
    # Get table schema
    cursor.execute("PRAGMA table_info(trades)")
    columns = cursor.fetchall()
    
    print("📊 COLONNE DISPONIBILI:")
    for col in columns:
        print(f"   {col[1]} ({col[2]})")
    
    print("\n🔍 SAMPLE TRADE:")
    cursor.execute("SELECT * FROM trades LIMIT 1")
    sample = cursor.fetchone()
    
    if sample:
        print("   Dati esempio:")
        for i, col in enumerate(columns):
            print(f"   {col[1]}: {sample[i]}")
    else:
        print("   ⚠️  Nessun trade nel database")
    
    # Count trades
    cursor.execute("SELECT COUNT(*) FROM trades")
    count = cursor.fetchone()[0]
    print(f"\n📈 TOTALE TRADES: {count}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Errore: {e}")


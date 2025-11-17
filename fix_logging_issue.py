#!/usr/bin/env python3
"""
Fix logging import conflict
"""

import re

def fix_logging_conflict():
    with open('quantum_v3_enhanced.py', 'r') as f:
        content = f.read()
    
    # Trova e sostituisce la sezione problematica
    old_section = '''        # 🚀 QUANTUM V3 GATING SYSTEM INTEGRATION
        # Ensure logger exists for gating system
        if not hasattr(self, 'logger'):
            import logging
            self.logger = logging.getLogger("QuantumTraderV21")'''
    
    new_section = '''        # 🚀 QUANTUM V3 GATING SYSTEM INTEGRATION
        # Ensure logger exists for gating system
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger("QuantumTraderV21")'''
    
    content = content.replace(old_section, new_section)
    
    with open('quantum_v3_enhanced.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Fixed logging import conflict")

if __name__ == "__main__":
    fix_logging_conflict()

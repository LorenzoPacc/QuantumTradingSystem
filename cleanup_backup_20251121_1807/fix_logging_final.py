#!/usr/bin/env python3
"""
Final fix for logging issue
"""

def fix_logging():
    with open('quantum_v3_enhanced.py', 'r') as f:
        content = f.read()
    
    # Rimuovi l'import logging duplicato
    old_code = '''        # 🚀 QUANTUM V3 GATING SYSTEM INTEGRATION
        # Ensure logger exists for gating system
        if not hasattr(self, 'logger'):
            import logging
            self.logger = logging.getLogger("QuantumTraderV21")'''
    
    new_code = '''        # 🚀 QUANTUM V3 GATING SYSTEM INTEGRATION
        # Ensure logger exists for gating system
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger("QuantumTraderV21")'''
    
    content = content.replace(old_code, new_code)
    
    with open('quantum_v3_enhanced.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed logging import successfully")

if __name__ == "__main__":
    fix_logging()

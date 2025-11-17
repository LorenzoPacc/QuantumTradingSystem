#!/usr/bin/env python3
"""
Quantum Trader V3 Integration Patcher
"""
import re
import sys
import os

def patch_existing_bot():
    input_file = "quantum_v2_1_complete.py"
    output_file = "quantum_v3_enhanced.py"
    
    if not os.path.exists(input_file):
        print("❌ Error: quantum_v2_1_complete.py not found!")
        return False
    
    print(f"📖 Reading {input_file}...")
    with open(input_file, 'r') as f:
        content = f.read()
    
    original_content = content
    modifications = []
    
    # Add imports
    if "from entry_gating_system import" not in content:
        print("  → Adding gating system imports...")
        
        lines = content.split('\n')
        last_import_idx = 0
        
        for i, line in enumerate(lines):
            if line.startswith(('import ', 'from ')):
                last_import_idx = i
            elif line.strip() and not line.startswith(('#', '"""', "'''")):
                break
        
        new_imports = [
            "",
            "# =============================================",
            "# QUANTUM V3 GATING SYSTEM INTEGRATION",
            "# =============================================",
            "from entry_gating_system import AdvancedGatingSystem, QuantumIntegrationManager",
            ""
        ]
        
        lines = lines[:last_import_idx+1] + new_imports + lines[last_import_idx+1:]
        content = '\n'.join(lines)
        modifications.append("Added gating system imports")
    
    # Add gating system to __init__
    if "self.gating_system" not in content:
        print("  → Integrating gating system into bot class...")
        
        class_pattern = r'(class QuantumTraderV21.*?def __init__\(self[^)]*\):\s*\n)(.*?)(?=\n    def \w+|\nclass |\Z)'
        
        match = re.search(class_pattern, content, re.DOTALL)
        if match:
            init_body = match.group(2)
            
            gating_init = '''
        # 🚀 QUANTUM V3 GATING SYSTEM INTEGRATION
        self.gating_config = {
            'min_volume_ratio': 0.75,
            'max_correlation': 0.7,
            'min_mtf_score': 0.65,
            'max_portfolio_positions': getattr(self, 'max_positions', 6),
            'min_liquidity_depth': 8000,
            'max_daily_drawdown': -0.03,
            'fear_greed_threshold': 20,
            'max_daily_volatility': 0.08,
            'position_size_base': 0.10,
            'min_position_size': 15.0,
            'max_position_size': 35.0,
        }
        
        self.gating_system = AdvancedGatingSystem(self.gating_config)
        self.integration_manager = QuantumIntegrationManager(self)
        self.integration_manager.dry_run_mode = True  # ⚠️ SAFETY FIRST!
        
        self.logger.info("🚀 QUANTUM V3 GATING SYSTEM INTEGRATED - DRY RUN MODE")
'''
            
            new_init_body = init_body.rstrip() + gating_init
            content = content.replace(init_body, new_init_body)
            modifications.append("Added gating system to __init__")
    
    # Save patched bot
    if modifications:
        print(f"  → Saving patched bot to {output_file}...")
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        print(f"\n✅ SUCCESS! Created {output_file}")
        print("📊 Modifications applied:")
        for mod in modifications:
            print(f"   • {mod}")
        
        return True
    else:
        print("ℹ️  No modifications needed")
        return True

def main():
    print("🚀 QUANTUM V3 BOT PATCHER")
    print("=" * 50)
    
    success = patch_existing_bot()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 PATCHING COMPLETED SUCCESSFULLY!")
        print("\n📁 Generated files:")
        print("   • entry_gating_system.py - Advanced gating system")
        print("   • quantum_v3_enhanced.py - Your enhanced bot")
        print("\n🚀 NEXT STEPS:")
        print("   1. Review: quantum_v3_enhanced.py")
        print("   2. Test: python3 quantum_v3_enhanced.py")
        print("   3. Monitor gating decisions in logs")
        print("   4. When confident: Set dry_run_mode = False")
        print("\n⚠️  SAFETY: Starts in DRY RUN mode - no live trades!")
    else:
        print("\n❌ PATCHING FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()

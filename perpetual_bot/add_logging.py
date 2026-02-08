import sys

# Read file
with open('perpetual_bot.py', 'r') as f:
    lines = f.readlines()

# Find imports section
import_index = 0
for i, line in enumerate(lines):
    if 'from positions_manager import PositionsPersistence' in line:
        import_index = i + 1
        break

# Insert logging import
lines.insert(import_index, "import logging\n")

# Find __init__ method
init_index = 0
for i, line in enumerate(lines):
    if 'def __init__(self, config_file=' in line:
        init_index = i + 1
        break

# Find where to add logger setup (after loading config)
config_index = 0
for i in range(init_index, len(lines)):
    if 'with open(config_file) as f:' in lines[i]:
        # Find next line after json.load
        for j in range(i, len(lines)):
            if 'self.config = json.load(f)' in lines[j]:
                config_index = j + 1
                break
        break

# Add logger setup
logger_code = """        
        # Setup detailed logging
        self.logger = logging.getLogger('PerpetualBot')
        self.logger.setLevel(logging.INFO)
        
        # Format like V37
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        self.logger.addHandler(console)
        
"""

lines.insert(config_index, logger_code)

# Save
with open('perpetual_bot.py', 'w') as f:
    f.writelines(lines)

print("✅ Logging configuration added!")

# Now replace all print() with self.logger.info()
with open('perpetual_bot.py', 'r') as f:
    content = f.read()

# Replace prints in run_cycle
content = content.replace('print("=" * 80)', 'self.logger.info("=" * 80)')
content = content.replace('print(f"🔄 CYCLE {self.cycle_count}', 'self.logger.info(f"🔄 CYCLE {self.cycle_count}')
content = content.replace('print(f"📊 Managing {len(self.positions)}', 'self.logger.info(f"📊 Managing {len(self.positions)}')
content = content.replace('print(f"🔍 Scanning {len(self.config', 'self.logger.info(f"🔍 Scanning {len(self.config')
content = content.replace('print(f"   {symbol}:")', 'self.logger.info(f"   {symbol}:")')
content = content.replace('print(f"      Signal:', 'self.logger.info(f"      Signal:')
content = content.replace('print(f"      Reason:', 'self.logger.info(f"      Reason:')
content = content.replace('print(f"      Funding:', 'self.logger.info(f"      Funding:')
content = content.replace('print(f"      ❌ BLOCKED:', 'self.logger.info(f"      ❌ BLOCKED:')
content = content.replace('print(f"      ⚠️ Cannot open:', 'self.logger.info(f"      ⚠️ Cannot open:')
content = content.replace('print(f"      ❌ R:R too low:', 'self.logger.info(f"      ❌ R:R too low:')
content = content.replace('print(f"      🟢 OPENED', 'self.logger.info(f"      🟢 OPENED')
content = content.replace('print(f"         Entry:', 'self.logger.info(f"         Entry:')
content = content.replace('print(f"         Size:', 'self.logger.info(f"         Size:')
content = content.replace('print(f"         Leverage:', 'self.logger.info(f"         Leverage:')
content = content.replace('print(f"         SL:', 'self.logger.info(f"         SL:')
content = content.replace('print(f"         TP:', 'self.logger.info(f"         TP:')
content = content.replace('print(f"         R:R:', 'self.logger.info(f"         R:R:')
content = content.replace('print(f"   {symbol} {direction}:")', 'self.logger.info(f"   {symbol} {direction}:")')
content = content.replace('print(f"      Entry: ${entry', 'self.logger.info(f"      Entry: ${entry')
content = content.replace('print(f"      PnL:', 'self.logger.info(f"      PnL:')
content = content.replace('print(f"      ✅ Trailing stop ACTIVATED', 'self.logger.info(f"      ✅ Trailing stop ACTIVATED')
content = content.replace('print(f"      📈 Trailing stop moved', 'self.logger.info(f"      📈 Trailing stop moved')
content = content.replace('print(f"      📉 Trailing stop moved', 'self.logger.info(f"      📉 Trailing stop moved')
content = content.replace('print(f"      🔴 CLOSED', 'self.logger.info(f"      🔴 CLOSED')
content = content.replace('print(f"         Exit:', 'self.logger.info(f"         Exit:')
content = content.replace('print(f"         New Capital:', 'self.logger.info(f"         New Capital:')
content = content.replace('print("")', 'self.logger.info("")')
content = content.replace('print("💼 PORTFOLIO STATUS")', 'self.logger.info("💼 PORTFOLIO STATUS")')
content = content.replace('print(f"   Capital:', 'self.logger.info(f"   Capital:')
content = content.replace('print(f"   Positions:', 'self.logger.info(f"   Positions:')
content = content.replace('print(f"   Daily PnL:', 'self.logger.info(f"   Daily PnL:')
content = content.replace('print(f"   Trades Today:', 'self.logger.info(f"   Trades Today:')
content = content.replace('print(f"   Total Trades:', 'self.logger.info(f"   Total Trades:')
content = content.replace('print(f"⏰ Next cycle', 'self.logger.info(f"⏰ Next cycle')

with open('perpetual_bot.py', 'w') as f:
    f.write(content)

print("✅ All print() replaced with logger.info()!")

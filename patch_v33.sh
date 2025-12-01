#!/bin/bash
set -e

echo "🔧 PATCH SPECIFICO PER quantum_v33_ultimate_final.py"
echo "======================================================================"

BOT_FILE="quantum_v33_ultimate_final.py"

# Verifica file esiste
if [ ! -f "$BOT_FILE" ]; then
    echo "❌ File $BOT_FILE non trovato!"
    exit 1
fi

echo "✅ Bot trovato: $BOT_FILE"
echo "📏 Dimensione: $(ls -lh "$BOT_FILE" | awk '{print $5}')"

# Backup con timestamp
BACKUP="${BOT_FILE%.py}_BACKUP_$(date +%Y%m%d_%H%M%S).py"
cp "$BOT_FILE" "$BACKUP"
echo "✅ Backup creato: $BACKUP"
echo ""

# PATCH 1: Intervallo check
echo "1️⃣ Check interval: 10min → 2min"
sed -i 's/sleep(600)/sleep(120)  # PATCHED: 2min/' "$BOT_FILE"
sed -i 's/time\.sleep(600)/time.sleep(120)  # PATCHED: 2min/' "$BOT_FILE"
echo "   ✅ Intervallo patchato"

# PATCH 2: Stop Loss
echo "2️⃣ Stop Loss: -2.5% → -2.0% | -3.5% → -2.5%"
sed -i 's/self\.stop_loss_pct = 0\.025/self.stop_loss_pct = 0.020  # PATCHED/' "$BOT_FILE"
sed -i 's/self\.stop_loss_extreme_fear = 0\.035/self.stop_loss_extreme_fear = 0.025  # PATCHED/' "$BOT_FILE"
echo "   ✅ Stop Loss patchati"

# PATCH 3: Take Profit
echo "3️⃣ Take Profit: 12%→5% | 8%→4% | 5%→3%"
sed -i 's/self\.TAKE_PROFIT_EXTREME = 0\.12/self.TAKE_PROFIT_EXTREME = 0.05  # PATCHED/' "$BOT_FILE"
sed -i 's/self\.TAKE_PROFIT_FEAR = 0\.08/self.TAKE_PROFIT_FEAR = 0.04  # PATCHED/' "$BOT_FILE"
sed -i 's/self\.TAKE_PROFIT_NORMAL = 0\.05/self.TAKE_PROFIT_NORMAL = 0.03  # PATCHED/' "$BOT_FILE"
echo "   ✅ Take Profit patchati"

# PATCH 4: Trailing
echo "4️⃣ Trailing: Trigger 2.5%→1.5% | Stop 1.5%→1.0%"
sed -i 's/self\.trailing_trigger = 0\.025/self.trailing_trigger = 0.015  # PATCHED/' "$BOT_FILE"
sed -i 's/self\.trailing_stop = 0\.015/self.trailing_stop = 0.010  # PATCHED/' "$BOT_FILE"
echo "   ✅ Trailing patchati"

# PATCH 5: Fear threshold
echo "5️⃣ Fear threshold: 25 → 30"
sed -i 's/self\.FG_EXTREME_FEAR = 25/self.FG_EXTREME_FEAR = 30  # PATCHED/' "$BOT_FILE"
echo "   ✅ Fear threshold patchato"

echo ""
echo "======================================================================"
echo "✅ TUTTI I PATCH APPLICATI!"
echo "======================================================================"
echo ""

# Test sintassi
echo "🧪 Test sintassi Python..."
python3 -m py_compile "$BOT_FILE" && echo "✅ Sintassi OK" || echo "❌ Errore sintassi"

echo ""
echo "📊 RIEPILOGO:"
echo "  Check: 10min → 2min (+400%)"
echo "  Stop Loss: -2.5% → -2.0%"
echo "  Take Profit: 5-12% → 3-5%"
echo "  Fear: 25 → 30"
echo ""
echo "🔄 Per riavviare:"
echo "  pkill -f quantum_v33"
echo "  python3 quantum_v33_ultimate_final.py &"

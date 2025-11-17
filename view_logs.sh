#!/bin/bash
echo "📊 QUANTUM SYSTEMS LIVE LOGS"
echo "============================"
echo "1. V2.1 LIVE Log"
echo "2. V3.0 DRY-RUN Log" 
echo "3. Both logs (side by side)"
echo "4. Back to main"
echo ""
read -p "Select option: " choice

case $choice in
    1)
        echo "📁 V2.1 LIVE Log (Ctrl+C to exit):"
        tail -f v21_live.log
        ;;
    2)
        echo "📁 V3.0 DRY-RUN Log (Ctrl+C to exit):"
        tail -f v30_dryrun.log
        ;;
    3)
        echo "📁 Both logs (Ctrl+C to exit):"
        tail -f v21_live.log v30_dryrun.log
        ;;
    4)
        exit 0
        ;;
    *)
        echo "❌ Invalid option"
        ;;
esac

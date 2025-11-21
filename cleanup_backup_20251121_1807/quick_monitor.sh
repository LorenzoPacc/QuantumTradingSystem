#!/bin/bash
echo "🔍 Quantum Systems Quick Monitor"
echo "================================"
echo "V2.1 LIVE:    $(ps -p $(cat v21_pid.txt 2>/dev/null) >/dev/null 2>&1 && echo '🟢 RUNNING' || echo '🔴 STOPPED')"
echo "V3.0 DRY-RUN: $(ps -p $(cat v30_pid.txt 2>/dev/null) >/dev/null 2>&1 && echo '🟢 RUNNING' || echo '🔴 STOPPED')"
echo ""
echo "Ultimi log V2.1:"
tail -3 v21_live.log 2>/dev/null | while read line; do echo "  📝 $line"; done
echo ""
echo "Ultimi log V3.0:"  
tail -3 v30_dryrun.log 2>/dev/null | while read line; do echo "  📝 $line"; done

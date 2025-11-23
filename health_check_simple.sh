#!/bin/bash
echo "🏥 QUANTUM HEALTH CHECK - ULTRA SIMPLE"
echo "======================================"
echo "✅ Bot: $(ps aux | grep -q "[q]uantum_simple_fixed.py" && echo "RUNNING" || echo "STOPPED")"
echo "📊 Fear: $(curl -s https://api.alternative.me/fng/?limit=1 | grep -o '"value":"[^"]*' | cut -d'"' -f4 2>/dev/null || echo "N/A")"
echo "💾 Disk: $(df -h . | awk 'NR==2 {print $5}')"
echo "======================================"

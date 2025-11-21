#!/bin/bash

echo "🚀 Installing Quantum Trader Final Real..."
echo "=========================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip
echo "🐍 Installing Python and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv quantum_env
source quantum_env/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip

pip install requests pandas numpy plotly streamlit matplotlib seaborn

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs cache data

# Set permissions
echo "🔒 Setting permissions..."
chmod +x quantum_trader_final_real.py
chmod +x *.sh

# Test installation
echo "🧪 Testing installation..."
python3 -c "
import requests, pandas, numpy, plotly
print('✅ All dependencies installed successfully')
"

echo ""
echo "🎉 INSTALLAZIONE COMPLETATA!"
echo "============================"
echo ""
echo "🚀 PER AVVIARE:"
echo "1. source quantum_env/bin/activate"
echo "2. python3 quantum_trader_final_real.py"
echo ""
echo "📊 PER LA DASHBOARD:"
echo "   streamlit run quantum_dashboard_final.py"
echo ""
echo "🔍 PER MONITORARE:"
echo "   ./quantum_monitor.sh"

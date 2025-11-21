#!/bin/bash
echo "🚀 Setting up Quantum Trader Pro Final..."

# Create virtual environment
python3 -m venv quantum_env
source quantum_env/bin/activate

# Install dependencies
pip install pandas numpy ta requests fastapi uvicorn

# Create necessary directories
mkdir -p logs

# Copy environment template if .env doesn't exist
if [ ! -f .env ]; then
    cp .env.template .env
    echo "⚠️  Please edit .env file with your API keys!"
fi

echo "✅ Setup complete!"
echo "🔧 Edit .env file with your API keys"
echo "🚀 Run with: source quantum_env/bin/activate && python3 quantum_trader_pro_final.py"

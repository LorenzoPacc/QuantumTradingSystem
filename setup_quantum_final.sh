#!/bin/bash
echo "🚀 Setting up Quantum Trader Ultimate Final..."

# Create virtual environment
python3 -m venv quantum_env
source quantum_env/bin/activate

# Install final dependencies
pip install pandas numpy ta requests fastapi uvicorn python-dotenv yfinance scikit-learn

# Create necessary directories
mkdir -p logs backtests

# Copy environment template if .env doesn't exist
if [ ! -f .env ]; then
    cp .env.template .env
    echo "⚠️  Please edit .env file with your API keys!"
    echo "📝 Get testnet keys from: https://testnet.binance.vision/"
    echo "🤖 Get Telegram bot token from: @BotFather"
    echo "🔧 Configure trading parameters in .env file"
fi

echo "✅ Ultimate Final setup complete!"
echo "🔧 Edit .env file with your API keys and parameters"
echo "🚀 Run LIVE trading: source quantum_env/bin/activate && python3 quantum_trader_ultimate_final.py"
echo "🧪 Run BACKTEST: source quantum_env/bin/activate && python3 quantum_trader_ultimate_final.py --backtest --symbol BTCUSDT --start 2024-01-01 --end 2024-03-01"
echo "🌐 Dashboard: http://localhost:8000"

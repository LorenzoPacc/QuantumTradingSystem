from binance.client import Client
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('BINANCE_TESTNET_API_KEY')
api_secret = os.getenv('BINANCE_TESTNET_SECRET_KEY')

print(f"🔑 API Key: {api_key[:10]}...")
print(f"🔑 Secret: {api_secret[:10]}...")

try:
    client = Client(api_key, api_secret, testnet=True)
    
    # Test semplice
    server_time = client.get_server_time()
    print("✅ Server time OK")
    
    # Test account
    account = client.get_account()
    print(f"✅ Account: {len(account['balances'])} assets")
    
    # Test balance
    balance = client.get_asset_balance(asset='USDT')
    print(f"💰 USDT Balance: {balance['free']}")
    
    # Test order (solo validazione)
    symbol_info = client.get_symbol_info('BTCUSDT')
    print(f"✅ Symbol info OK")
    
except Exception as e:
    print(f"❌ Errore: {e}")

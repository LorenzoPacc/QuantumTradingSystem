"""
🎯 QUANTUM TRADING - CONFIGURAZIONE CENTRALE
Unico file per tutte le API Key e impostazioni
"""

# ⚠️ INSERISCI LE TUE CHIAVI QUI UNA VOLTA SOLA ⚠️
BINANCE_TESTNET = {
    "api_key": "h9LX8Z2xTLVOcfDjcX410QZG3sU5DxzOGBLxcbX5GYrvz9lfCs7RDjb8N2jzDWXW",      # ⬅️ SOSTITUISCI
    "api_secret": "V98bXD1RQTJTwRqEke1kkqBAFaPhQJ80RQ8R1jI8uUgnkLqX91YoNhPneuPTYsv7",    # ⬅️ SOSTITUISCI
    "base_url": "https://testnet.binance.vision/api/v3"
}

# Configurazione Trading
TRADING_CONFIG = {
    "confluence_min": 3.0,
    "confidence_min": 70,
    "risk_per_trade": 0.02,
    "max_trades": 3,
    "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
    "check_interval": 60
}

# Configurazione Dashboard
DASHBOARD_CONFIG = {
    "refresh_interval": 30,
    "max_trades_display": 10,
    "auto_refresh": True
}

# Database
DATABASE_CONFIG = {
    "path": "quantum_unified.db",
    "backup_interval": 3600  # 1 ora
}

#!/usr/bin/env python3
"""
🔔 QUANTUM TRADER V2 - ALERT SYSTEM
Alert per eventi critici via Telegram
"""

import requests
import json
from datetime import datetime
import logging

class QuantumAlertSystem:
    def __init__(self, telegram_bot_token=None, chat_id=None):
        self.telegram_bot_token = telegram_bot_token
        self.chat_id = chat_id
        self.enabled = bool(telegram_bot_token and chat_id)
        
    def send_alert(self, level: str, message: str, data: dict = None):
        """Invia alert con livello di priorità"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"🚨 QUANTUM V2 {level} - {timestamp}\n{message}"
        
        if data:
            full_message += f"\n📊 Dati: {json.dumps(data, indent=2)}"
        
        print(f"🔔 {full_message}")  # Log locale
        
        if self.enabled:
            self._send_telegram_alert(full_message)
    
    def _send_telegram_alert(self, message: str):
        """Invia messaggio via Telegram Bot"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                logging.error(f"Errore invio Telegram: {response.text}")
        except Exception as e:
            logging.error(f"Errore connessione Telegram: {e}")
    
    # Alert specifici per Quantum Trader
    def alert_trade_executed(self, symbol: str, action: str, quantity: float, price: float, total_value: float, reason: str):
        """Alert per trade eseguito"""
        emoji = "🟢" if action == "BUY" else "🔴"
        message = f"{emoji} {action} {symbol}\n"
        message += f"Quantità: {quantity:.6f}\n"
        message += f"Prezzo: ${price:.2f}\n"
        message += f"Totale: ${total_value:.2f}\n"
        message += f"Motivo: {reason}"
        
        self.send_alert("TRADE", message)
    
    def alert_drawdown_warning(self, current_value: float, initial_capital: float, drawdown_percent: float):
        """Alert per drawdown significativo"""
        message = f"📉 DRAWDOWN WARNING\n"
        message += f"Portfolio: ${current_value:.2f}\n"
        message += f"Capitale: ${initial_capital:.2f}\n"
        message += f"Drawdown: {drawdown_percent:+.1f}%"
        
        level = "CRITICAL" if drawdown_percent <= -8 else "WARNING"
        self.send_alert(level, message)
    
    def alert_emergency_stop(self, drawdown_percent: float):
        """Alert per emergency stop"""
        message = f"🛑 EMERGENCY STOP ATTIVATO\n"
        message += f"Drawdown: {drawdown_percent:+.1f}%\n"
        message += f"Bot fermato automaticamente"
        
        self.send_alert("CRITICAL", message)
    
    def alert_regime_change(self, old_regime: str, new_regime: str):
        """Alert per cambio regime di mercato"""
        message = f"🎯 CAMBIO REGIME\n"
        message += f"Da: {old_regime}\n"
        message += f"A: {new_regime}"
        
        self.send_alert("INFO", message)

# Istanza globale (configura dopo con i tuoi token)
alert_system = QuantumAlertSystem()

def setup_telegram_alerts(bot_token: str, chat_id: str):
    """Configura gli alert Telegram"""
    global alert_system
    alert_system = QuantumAlertSystem(bot_token, chat_id)
    print("✅ Sistema alert Telegram configurato")

# Per testare
if __name__ == "__main__":
    # Test alert
    alert_system.send_alert("TEST", "Sistema alert funzionante!")
    alert_system.alert_trade_executed("BTCUSDT", "BUY", 0.001, 45000, 45.0, "F&G=15, RSI=30")

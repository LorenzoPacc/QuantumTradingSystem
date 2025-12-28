#!/usr/bin/env python3
"""
🎯 TELEGRAM PRO - Minimalista & Intelligente
Bug fixed + migliorie performance
"""
import os
import requests
from datetime import datetime
import json

class TelegramPro:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.token and self.chat_id)
        self.state_file = "telegram_state.json"
        self.state = self._load_state()
        
        if self.enabled:
            print("✅ Telegram Pro: ATTIVO (modalità minimalista)")
        else:
            print("⚠️  Telegram: Disabilitato - Configura TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID")
    
    def _load_state(self):
        """Carica stato con reset giornaliero intelligente"""
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
        except:
            state = {}
        
        # Reset contatori giornalieri se nuovo giorno
        today = datetime.now().strftime('%Y-%m-%d')
        if state.get('last_daily_check') != today:
            state.update({
                'trades_today': 0,
                'fear_alerts_today': 0,
                'last_daily_check': today
            })
        
        # Ensure required fields
        defaults = {
            'fear_zone_active': False,
            'last_fear_alert': None
        }
        for key, value in defaults.items():
            if key not in state:
                state[key] = value
        
        return state
    
    def _save_state(self):
        """Salva stato - versione robusta"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"⚠️  Salvataggio stato Telegram fallito: {e}")

    def send(self, message, important=True):
        """Invia messaggio - SEMPLICE e AFFIDABILE"""
        if not self.enabled:
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_notification': not important  # Suono solo per importanti
            }
            response = requests.post(url, json=payload, timeout=10)
            success = response.status_code == 200
            
            if not success:
                print(f"⚠️  Telegram API error: {response.status_code}")
            
            return success
            
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False
    
    def trade_alert(self, action, symbol, price, quantity, total_value, remaining_cash=None):
        """🚨 TRADE ESEGUITO - SEMPRE NOTIFICATO"""
        if not self.enabled:
            return False
        
        emoji = "🟢" if action.upper() == "BUY" else "🔴"
        action_text = "ACQUISTO" if action.upper() == "BUY" else "VENDITA"
        
        cash_info = f"\n💼 Cash rimanente: ${remaining_cash:.2f}" if remaining_cash else ""
        
        message = f"""
{emoji} <b>{action_text} ESEGUITA</b>

{symbol}
📦 {quantity:.6f} @ ${price:,.2f}
💰 Totale: ${total_value:.2f}{cash_info}

⏰ {datetime.now().strftime('%H:%M')}
        """
        
        self.state['trades_today'] = self.state.get('trades_today', 0) + 1
        self._save_state()
        
        return self.send(message.strip(), important=True)
    
    def fear_intelligence_alert(self, current_fear):
        """🎯 FEAR & GREED INTELLIGENTE - MAX 2/giorno"""
        if not self.enabled:
            return False
        
        # Controllo rate limiting giornaliero
        fear_alerts_today = self.state.get('fear_alerts_today', 0)
        if fear_alerts_today >= 2:
            return False
        
        now_in_zone = 16 <= current_fear <= 28
        was_in_zone = self.state.get('fear_zone_active', False)
        last_fear = self.state.get('last_fear_alert')
        
        # 🔥 NOTIFICA SOLO SE:
        # 1. Entra in zona compra per la prima volta
        if not was_in_zone and now_in_zone:
            message = f"""
🎯 <b>ZONA COMPRA ATTIVA</b>

📊 Fear & Greed: {current_fear}
✅ Bot inizierà ad acquistare

Riceverai notifica al primo trade.

⏰ {datetime.now().strftime('%H:%M')}
            """
            self.state.update({
                'fear_zone_active': True,
                'fear_alerts_today': fear_alerts_today + 1,
                'last_fear_alert': current_fear
            })
            self._save_state()
            return self.send(message.strip(), important=True)
        
        # 2. Cambio significativo (≥10 punti) dopo prima notifica
        elif (last_fear is not None and 
              abs(current_fear - last_fear) >= 10 and 
              fear_alerts_today < 2):
            
            trend = "↗️ SALITA" if current_fear > last_fear else "↘️ DISCESA"
            message = f"""
📊 <b>FEAR UPDATE</b>

{last_fear} → {current_fear} {trend}

💡 Continua monitoraggio

⏰ {datetime.now().strftime('%H:%M')}
            """
            self.state.update({
                'fear_alerts_today': fear_alerts_today + 1,
                'last_fear_alert': current_fear
            })
            self._save_state()
            return self.send(message.strip(), important=False)
        
        # Aggiorna stato zona
        if was_in_zone and not now_in_zone:
            self.state['fear_zone_active'] = False
            self._save_state()
        
        return False
    
    def smart_daily_summary(self, cash, total, positions, market_change=None):
        """📊 RIEPILOGO SERALE INTELLIGENTE"""
        if not self.enabled:
            return False
        
        # Solo una volta al giorno, dopo le 20:00
        current_hour = datetime.now().hour
        if current_hour < 20:  # Prima delle 20:00
            return False
        
        today = datetime.now().strftime('%Y-%m-%d')
        if self.state.get('last_daily_summary') == today:
            return False
        
        trades_today = self.state.get('trades_today', 0)
        
        # Notifica solo se c'è stata attività significativa
        if trades_today > 0 or positions > 0:
            market_info = f"\n📈 Variazione: {market_change}" if market_change else ""
            
            message = f"""
📊 <b>RIEPILOGO SERALE</b>

💰 Liquidità: ${cash:.2f}
📈 Valore totale: ${total:.2f}
📦 Posizioni attive: {positions}/6
🔄 Trade eseguiti: {trades_today}{market_info}

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}
            """
            
            self.state['last_daily_summary'] = today
            self._save_state()
            
            return self.send(message.strip(), important=False)
        
        return False
    
    def system_alert(self, alert_type, details=""):
        """⚠️ ALERT SISTEMA - Solo per problemi critici"""
        if not self.enabled:
            return False
        
        alerts = {
            'error': '🚨 ERRORE CRITICO',
            'warning': '⚠️  AVVISO SISTEMA', 
            'info': 'ℹ️  INFO SISTEMA'
        }
        
        title = alerts.get(alert_type, '⚠️  NOTIFICA SISTEMA')
        
        message = f"""
{title}

{details}

⏰ {datetime.now().strftime('%d/%m %H:%M')}
        """
        
        return self.send(message.strip(), important=(alert_type in ['error', 'warning']))

# Istanza globale
telegram = TelegramPro()

if __name__ == "__main__":
    print("🧪 TELEGRAM PRO - TEST SYSTEM")
    print(f"Status: {'✅ ATTIVO' if telegram.enabled else '❌ DISABILITATO'}")
    
    if telegram.enabled:
        print("📤 Test invio notifica...")
        success = telegram.send(
            "🤖 Quantum Bot Pro - Sistema test OK\n\nConfigurazione completata correttamente!",
            important=False
        )
        print(f"Risultato test: {'✅ SUCCESSO' if success else '❌ FALLITO'}")
        
        # Mostra stato corrente
        print(f"\n📊 STATO ATTUALE:")
        print(f"   Trade oggi: {telegram.state.get('trades_today', 0)}")
        print(f"   Alert Fear oggi: {telegram.state.get('fear_alerts_today', 0)}")
        print(f"   Zona compra attiva: {telegram.state.get('fear_zone_active', False)}")
    else:
        print("\n🔧 PER ATTIVARE:")
        print("   1. Configura TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID")
        print("   2. Riavvia il terminale o esegui: source ~/.bashrc")
        print("   3. Riesegui questo test")

"""Safe Mode Manager - Protezione automatica"""
import json
import logging
from typing import Dict, Any
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class TradingMetrics:
    daily_pnl_percent: float = 0.0
    drawdown_percent: float = 0.0
    consecutive_losses: int = 0
    api_errors_count: int = 0


class SafeModeManager:
    def __init__(self, config: Dict[str, Any]):
        self.safe_mode_config = config.get("safe_mode", {})
        self.kill_switch_config = config.get("kill_switch", {})
        
        self.safe_mode_active = False
        self.kill_switch_triggered = False
        self.safe_mode_reason = ""
        self.kill_switch_reason = ""
        
        logger.info("✅ SafeModeManager inizializzato")
    
    def check_and_update(self, metrics: TradingMetrics) -> Dict[str, Any]:
        if self._check_kill_switch(metrics):
            self._trigger_kill_switch(metrics)
            return {
                "kill_switch": True,
                "safe_mode": True,
                "allow_new_entries": False,
                "reason": self.kill_switch_reason
            }
        
        if self._check_safe_mode(metrics):
            if not self.safe_mode_active:
                self._activate_safe_mode(metrics)
        else:
            if self.safe_mode_active:
                self._deactivate_safe_mode()
        
        return {
            "kill_switch": False,
            "safe_mode": self.safe_mode_active,
            "allow_new_entries": not self.safe_mode_active,
            "reason": self.safe_mode_reason if self.safe_mode_active else ""
        }
    
    def _check_safe_mode(self, metrics: TradingMetrics) -> bool:
        if not self.safe_mode_config.get("enabled", True):
            return False
        
        triggers = self.safe_mode_config.get("triggers", {})
        
        if metrics.daily_pnl_percent <= triggers.get("daily_loss_percent", -5.0):
            self.safe_mode_reason = f"Perdita giornaliera {metrics.daily_pnl_percent:.2f}%"
            return True
        
        if metrics.consecutive_losses >= triggers.get("consecutive_losses", 5):
            self.safe_mode_reason = f"{metrics.consecutive_losses} perdite consecutive"
            return True
        
        if metrics.api_errors_count >= triggers.get("api_errors_threshold", 10):
            self.safe_mode_reason = f"{metrics.api_errors_count} errori API"
            return True
        
        return False
    
    def _check_kill_switch(self, metrics: TradingMetrics) -> bool:
        if not self.kill_switch_config.get("enabled", True):
            return False
        
        if self.kill_switch_triggered:
            return True
        
        triggers = self.kill_switch_config.get("triggers", {})
        
        if metrics.daily_pnl_percent <= triggers.get("daily_loss_percent", -10.0):
            self.kill_switch_reason = f"PERDITA CRITICA: {metrics.daily_pnl_percent:.2f}%"
            return True
        
        return False
    
    def _activate_safe_mode(self, metrics: TradingMetrics):
        self.safe_mode_active = True
        logger.warning(f"🛡️ SAFE MODE ATTIVATO: {self.safe_mode_reason}")
    
    def _deactivate_safe_mode(self):
        logger.info("✅ Safe mode disattivato")
        self.safe_mode_active = False
        self.safe_mode_reason = ""
    
    def _trigger_kill_switch(self, metrics: TradingMetrics):
        if not self.kill_switch_triggered:
            self.kill_switch_triggered = True
            logger.critical(f"🚨 KILL SWITCH ATTIVATO: {self.kill_switch_reason}")
    
    def record_api_error(self, error: str):
        pass  # Simplified
    
    def manual_override(self, action: str):
        if action == "activate_safe_mode":
            self.safe_mode_active = True
            self.safe_mode_reason = "Attivazione manuale"
        elif action == "deactivate_safe_mode":
            self.safe_mode_active = False


def init_safe_mode_manager(config_path: str = "bot_improvements_config.json"):
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return SafeModeManager(config)
    except Exception as e:
        logger.error(f"❌ Errore init safe mode: {e}")
        return SafeModeManager({"safe_mode": {"enabled": False}, "kill_switch": {"enabled": False}})

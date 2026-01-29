"""Tracking Systems - Timeline e metriche rolling"""
import json
import logging
from typing import Dict, Any, List
from pathlib import Path
from collections import deque
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TradeResult:
    symbol: str
    side: str
    pnl: float
    pnl_percent: float
    duration_seconds: float
    exit_reason: str


class TimelineTracker:
    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get("enabled", True)
        self.directory = Path(config.get("directory", "./timelines"))
        
        if self.enabled:
            self.directory.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ TimelineTracker attivo")
    
    def record_event(self, trade_id: str, event_type: str, price: float, **details):
        pass  # Simplified
    
    def finalize_trade(self, trade_id: str, final_pnl: float):
        pass  # Simplified


class RollingMetrics:
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.recent_trades = deque(maxlen=window_size)
        
        logger.info(f"✅ RollingMetrics: finestra {window_size} trade")
    
    def add_trade(self, symbol: str, side: str, pnl: float, pnl_percent: float, 
                  duration: float, exit_reason: str):
        trade = TradeResult(symbol, side, pnl, pnl_percent, duration, exit_reason)
        self.recent_trades.append(trade)
    
    def calculate_metrics(self) -> Dict[str, Any]:
        if not self.recent_trades:
            return {"trades_in_window": 0, "win_rate": 0}
        
        winners = [t for t in self.recent_trades if t.pnl > 0]
        total = len(self.recent_trades)
        win_rate = (len(winners) / total * 100) if total > 0 else 0
        
        avg_win = sum(t.pnl for t in winners) / len(winners) if winners else 0
        losers = [t for t in self.recent_trades if t.pnl < 0]
        avg_loss = sum(t.pnl for t in losers) / len(losers) if losers else 0
        expectancy = (win_rate/100 * avg_win) + ((1-win_rate/100) * avg_loss)
        
        return {
            "trades_in_window": total,
            "win_rate": round(win_rate, 2),
            "winners": len(winners),
            "losers": len(losers),
            "expectancy": round(expectancy, 2)
        }


def init_tracking_systems(window_size: int = 20, config_path: str = "bot_improvements_config.json") -> Dict[str, Any]:
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        return {
            "timeline": TimelineTracker(config["timeline_events"]),
            "metrics": RollingMetrics(window_size)
        }
    except Exception as e:
        logger.error(f"❌ Errore init tracking: {e}")
        return {
            "timeline": TimelineTracker({"enabled": False}),
            "metrics": RollingMetrics(window_size)
        }

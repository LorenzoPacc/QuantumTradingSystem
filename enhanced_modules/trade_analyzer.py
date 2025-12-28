"""
📊 TRADE ANALYZER - Analisi dei trade chiusi per identificare pattern
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import json


class TradeAnalyzer:
    """Analizza i trade chiusi per imparare pattern vincenti"""
    
    def __init__(self, history_file: str = "trade_analysis_history.json"):
        self.history_file = history_file
        self.trade_history = []
        self._load_history()
    
    def _load_history(self):
        """Carica storico analisi da file"""
        try:
            with open(self.history_file, 'r') as f:
                self.trade_history = json.load(f)
            logging.info(f"✅ Loaded {len(self.trade_history)} historical trade analyses")
        except FileNotFoundError:
            logging.info("📝 Creating new trade analysis history")
            self.trade_history = []
        except Exception as e:
            logging.error(f"Error loading trade history: {e}")
            self.trade_history = []
    
    def _save_history(self):
        """Salva storico su file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.trade_history, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving trade history: {e}")
    
    def analyze_closed_trade(
        self,
        symbol: str,
        entry_time: datetime,
        exit_time: datetime,
        entry_price: float,
        exit_price: float,
        pnl_pct: float,
        entry_fear: int,
        entry_rsi: float,
        entry_price_change: float,
        exit_reason: str,
        high_watermark: float
    ) -> Dict[str, Any]:
        """
        Analizza un trade chiuso
        
        Returns:
            Dict con analisi completa del trade
        """
        
        # Calcola durata
        duration = exit_time - entry_time
        duration_hours = duration.total_seconds() / 3600
        
        # Determina performance
        performance = "WIN" if pnl_pct > 0 else "LOSS"
        
        # Classifica quality del setup
        setup_quality = self._classify_setup_quality(entry_fear, entry_rsi, entry_price_change)
        
        # Crea analisi
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'entry': {
                'time': entry_time.isoformat(),
                'price': entry_price,
                'fear_greed': entry_fear,
                'rsi': entry_rsi,
                'price_change_24h': entry_price_change
            },
            'exit': {
                'time': exit_time.isoformat(),
                'price': exit_price,
                'reason': exit_reason
            },
            'performance': {
                'pnl_pct': pnl_pct,
                'duration_hours': duration_hours,
                'high_watermark': high_watermark,
                'result': performance,
                'setup_quality': setup_quality
            }
        }
        
        # Salva in history
        self.trade_history.append(analysis)
        self._save_history()
        
        # Log formattato
        log_message = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 TRADE CLOSED ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🪙 Symbol: {symbol}

📈 Entry:
   • Time: {entry_time.strftime('%Y-%m-%d %H:%M')}
   • Price: ${entry_price:.2f}
   • Fear & Greed: {entry_fear}
   • RSI: {entry_rsi:.1f}
   • 24h Change: {entry_price_change:+.2f}%
   • Setup Quality: {setup_quality}

📉 Exit:
   • Time: {exit_time.strftime('%Y-%m-%d %H:%M')}
   • Price: ${exit_price:.2f}
   • Reason: {exit_reason}

💰 Performance:
   • Duration: {duration_hours:.1f}h
   • PnL: {pnl_pct:+.2f}%
   • High: {high_watermark:+.2f}%
   • Result: {'🟢 WIN' if performance == 'WIN' else '🔴 LOSS'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        logging.info(log_message)
        
        return analysis
    
    def _classify_setup_quality(self, fear: int, rsi: float, price_change: float) -> str:
        """Classifica la qualità del setup entry"""
        score = 0
        
        # Fear & Greed
        if fear < 25:
            score += 2
        elif fear < 35:
            score += 1
        
        # RSI
        if rsi < 30:
            score += 2
        elif rsi < 40:
            score += 1
        
        # Price change
        if price_change < -7:
            score += 2
        elif price_change < -4:
            score += 1
        
        if score >= 5:
            return "EXCELLENT"
        elif score >= 3:
            return "GOOD"
        elif score >= 1:
            return "AVERAGE"
        else:
            return "POOR"
    
    def get_winning_patterns(self, min_trades: int = 10) -> Dict[str, Any]:
        """Identifica pattern che hanno portato a vittorie"""
        if len(self.trade_history) < min_trades:
            return {'message': 'Not enough trades for analysis'}
        
        winners = [t for t in self.trade_history if t['performance']['result'] == 'WIN']
        losers = [t for t in self.trade_history if t['performance']['result'] == 'LOSS']
        
        if not winners:
            return {'message': 'No winning trades yet'}
        
        # Analizza setup vincenti
        winner_fear_avg = sum(t['entry']['fear_greed'] for t in winners) / len(winners)
        winner_rsi_avg = sum(t['entry']['rsi'] for t in winners) / len(winners)
        winner_pc_avg = sum(t['entry']['price_change_24h'] for t in winners) / len(winners)
        winner_duration_avg = sum(t['performance']['duration_hours'] for t in winners) / len(winners)
        
        return {
            'total_trades': len(self.trade_history),
            'winners': len(winners),
            'losers': len(losers),
            'win_rate': len(winners) / len(self.trade_history) * 100,
            'winning_setup_avg': {
                'fear_greed': winner_fear_avg,
                'rsi': winner_rsi_avg,
                'price_change_24h': winner_pc_avg,
                'duration_hours': winner_duration_avg
            }
        }
    
    def get_recent_performance(self, last_n: int = 20) -> Dict[str, Any]:
        """Performance degli ultimi N trade"""
        if not self.trade_history:
            return {}
        
        recent = self.trade_history[-last_n:]
        wins = len([t for t in recent if t['performance']['result'] == 'WIN'])
        
        return {
            'recent_trades': len(recent),
            'wins': wins,
            'losses': len(recent) - wins,
            'win_rate': wins / len(recent) * 100 if recent else 0,
            'avg_pnl': sum(t['performance']['pnl_pct'] for t in recent) / len(recent) if recent else 0
        }

"""API Protection - Rate limiting, idempotency, graceful degradation"""
import time
import json
import logging
import hashlib
from typing import Dict, Any, Optional, Callable
from collections import deque
from pathlib import Path

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get("enabled", True)
        self.limit_per_min = config.get("binance_limit_per_min", 1000)
        safety_margin = config.get("safety_margin_percent", 20) / 100
        self.effective_limit = int(self.limit_per_min * (1 - safety_margin))
        self.call_times = deque(maxlen=self.effective_limit)
        
        logger.info(f"✅ RateLimiter: {self.effective_limit} calls/min")
    
    def acquire(self, weight: int = 1) -> bool:
        if not self.enabled:
            return True
        
        now = time.time()
        cutoff = now - 60
        
        while self.call_times and self.call_times[0] < cutoff:
            self.call_times.popleft()
        
        if len(self.call_times) + weight > self.effective_limit:
            return False
        
        for _ in range(weight):
            self.call_times.append(now)
        
        return True
    
    def wait_if_needed(self, weight: int = 1):
        while not self.acquire(weight):
            time.sleep(1)
    
    def get_stats(self) -> Dict[str, Any]:
        now = time.time()
        cutoff = now - 60
        recent_calls = sum(1 for t in self.call_times if t > cutoff)
        
        return {
            "calls_last_minute": recent_calls,
            "limit": self.effective_limit,
            "usage_percent": (recent_calls / self.effective_limit * 100) if self.effective_limit > 0 else 0
        }


class IdempotencyCache:
    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get("enabled", True)
        self.cache_dir = Path(config.get("cache_directory", "./trade_cache"))
        self.memory_cache: Dict[str, float] = {}
        
        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ IdempotencyCache attivo")
    
    def generate_key(self, symbol: str, side: str, timestamp: float, **kwargs) -> str:
        key_parts = [symbol, side, str(int(timestamp))]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        key_string = "|".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def check_and_set(self, trade_key: str) -> bool:
        if not self.enabled:
            return True
        
        now = time.time()
        
        if trade_key in self.memory_cache:
            age = now - self.memory_cache[trade_key]
            if age < 300:  # 5 min TTL
                return False
        
        self.memory_cache[trade_key] = now
        return True


class GracefulDegradation:
    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get("enabled", True)
        self.max_retries = config.get("max_retries", 3)
        self.skip_on_error = config.get("skip_cycle_on_error", True)
        self.consecutive_errors = 0
        
        logger.info("✅ GracefulDegradation attivo")
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Optional[Any]:
        if not self.enabled:
            return func(*args, **kwargs)
        
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                self.consecutive_errors = 0
                return result
            except Exception as e:
                self.consecutive_errors += 1
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"❌ Fallito dopo {self.max_retries} tentativi")
        
        return None
    
    def should_skip_cycle(self) -> bool:
        return self.enabled and self.skip_on_error and self.consecutive_errors >= 3


def init_api_protection(config_path: str = "bot_improvements_config.json") -> Dict[str, Any]:
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        return {
            "rate_limiter": RateLimiter(config["rate_limiting"]),
            "idempotency": IdempotencyCache(config["idempotency"]),
            "degradation": GracefulDegradation(config["graceful_degradation"])
        }
    except Exception as e:
        logger.error(f"❌ Errore init API protection: {e}")
        return {
            "rate_limiter": RateLimiter({"enabled": False}),
            "idempotency": IdempotencyCache({"enabled": False}),
            "degradation": GracefulDegradation({"enabled": False})
        }

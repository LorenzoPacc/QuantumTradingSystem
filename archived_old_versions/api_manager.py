"""
API MANAGER per Quantum Trader - Gestione robusta chiamate Binance
"""

import asyncio
import time
from typing import Any, Callable, Optional, Dict

class APIManager:
    """
    Gestisce chiamate API con retry, rate limiting e error handling
    """
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.request_times = []
        self.rate_limit = 1100  # Binance: 1200 requests/minute
        self.window = 60  # 60 secondi
        
    async def safe_api_call(self, api_func: Callable, *args, **kwargs) -> Optional[Any]:
        """
        Esegue chiamata API con retry e rate limiting
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Rate limiting
                await self._wait_for_rate_limit()
                
                # Esegui chiamata
                result = await api_func(*args, **kwargs)
                
                # Registra successo
                self._record_request()
                
                return result
                
            except Exception as e:
                last_error = e
                
                if self._should_retry(e, attempt):
                    delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                    print(f"⚠️ API call failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                    continue
                else:
                    break
        
        print(f"❌ API call failed after {self.max_retries} attempts: {last_error}")
        return None
    
    def _should_retry(self, error: Exception, attempt: int) -> bool:
        """
        Determina se ritentare la chiamata
        """
        error_str = str(error).lower()
        
        # Errori temporanei - ritenta
        temporary_errors = [
            'timeout', 'connection', 'gateway', 'busy', 
            'overloaded', 'maintenance', 'rate limit'
        ]
        
        if any(temp_err in error_str for temp_err in temporary_errors):
            return attempt < self.max_retries
        
        # Errori permanenti - non ritentare
        permanent_errors = [
            'invalid symbol', 'insufficient balance', 'permission denied'
        ]
        
        if any(perm_err in error_str for perm_err in permanent_errors):
            return False
        
        # Default: ritenta per altri errori
        return attempt < self.max_retries
    
    async def _wait_for_rate_limit(self):
        """
        Attende se necessario per rispettare rate limits
        """
        now = time.time()
        
        # Rimuovi request più vecchie di window
        self.request_times = [t for t in self.request_times if now - t < self.window]
        
        # Se troppo vicini al limite, aspetta
        if len(self.request_times) >= self.rate_limit:
            oldest_time = self.request_times[0]
            wait_time = self.window - (now - oldest_time)
            if wait_time > 0:
                print(f"⏳ Rate limit接近, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
    
    def _record_request(self):
        """Registra una request per rate limiting"""
        self.request_times.append(time.time())
    
    def get_request_stats(self) -> Dict[str, Any]:
        """Restituisce statistiche requests"""
        now = time.time()
        recent_requests = [t for t in self.request_times if now - t < self.window]
        
        return {
            'requests_last_minute': len(recent_requests),
            'rate_limit_remaining': self.rate_limit - len(recent_requests),
            'window_seconds': self.window
        }

class BinanceAPIManager(APIManager):
    """
    Specializzato per API Binance
    """
    
    def __init__(self, client):
        super().__init__()
        self.client = client
    
    async def get_klines_safe(self, symbol: str, interval: str, limit: int = 100):
        """Safe version di get_klines"""
        return await self.safe_api_call(
            self.client.get_klines,
            symbol=symbol,
            interval=interval,
            limit=limit
        )
    
    async def get_orderbook_safe(self, symbol: str, limit: int = 10):
        """Safe version di get_orderbook"""
        return await self.safe_api_call(
            self.client.get_order_book,
            symbol=symbol,
            limit=limit
        )
    
    async def get_account_safe(self):
        """Safe version di get_account"""
        return await self.safe_api_call(self.client.get_account)
    
    async def create_order_safe(self, symbol: str, side: str, order_type: str, **kwargs):
        """Safe version di create_order"""
        return await self.safe_api_call(
            self.client.create_order,
            symbol=symbol,
            side=side,
            type=order_type,
            **kwargs
        )

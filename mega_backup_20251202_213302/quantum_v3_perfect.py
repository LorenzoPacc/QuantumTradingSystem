
# ============================================
# SINGLE INSTANCE LOCK
# ============================================
import os
import atexit

LOCK_FILE = '/tmp/quantum_v3.lock'

def check_lock():
    """Verifica che non ci sia già un'istanza attiva"""
    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE, 'r') as f:
            old_pid = f.read().strip()
        
        # Verifica se il processo esiste ancora
        try:
            os.kill(int(old_pid), 0)
            print(f"❌ ERRORE: Quantum V3 già in esecuzione! PID: {old_pid}")
            print(f"   Usa: kill {old_pid}  oppure  ~/qstop_v3")
            sys.exit(1)
        except (OSError, ValueError):
            # Processo morto, rimuovi lock
            os.remove(LOCK_FILE)
    
    # Crea nuovo lock
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))
    
    # Rimuovi lock all'uscita
    atexit.register(lambda: os.remove(LOCK_FILE) if os.path.exists(LOCK_FILE) else None)

# ============================================
# PORTFOLIO PERSISTENCE
# ============================================
import json

PORTFOLIO_FILE = 'portfolio_v3.json'

def save_portfolio(self):
    """Salva portfolio su disco"""
    data = {
        'cash': self.cash,
        'portfolio': {},
        'capital_initial': self.capital_initial,
        'cycle_count': self.cycle_count,
        'timestamp': datetime.now().isoformat()
    }
    
    for symbol, pos in self.portfolio.items():
        data['portfolio'][symbol] = {
            'entry_price': pos['entry_price'],
            'amount': pos['amount'],
            'entry_time': pos['entry_time'].isoformat(),
            'signal_strength': pos['signal_strength']
        }
    
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.debug(f"💾 Portfolio salvato: {len(self.portfolio)} posizioni")

def load_portfolio(self):
    """Carica portfolio da disco"""
    if not os.path.exists(PORTFOLIO_FILE):
        logger.info("💾 Nessun portfolio precedente trovato")
        return False
    
    try:
        with open(PORTFOLIO_FILE, 'r') as f:
            data = json.load(f)
        
        self.cash = data['cash']
        self.capital_initial = data['capital_initial']
        self.cycle_count = data.get('cycle_count', 0)
        
        for symbol, pos in data['portfolio'].items():
            self.portfolio[symbol] = {
                'entry_price': pos['entry_price'],
                'amount': pos['amount'],
                'entry_time': datetime.fromisoformat(pos['entry_time']),
                'signal_strength': pos['signal_strength']
            }
        
        logger.info(f"💾 Portfolio caricato: {len(self.portfolio)} posizioni, ${self.cash:.2f} cash")
        return True
    except Exception as e:
        logger.error(f"❌ Errore caricamento portfolio: {e}")
        return False

# ============================================
# RETRY MECHANISM
# ============================================
from functools import wraps

def retry_on_error(max_retries=3, delay=2):
    """Decorator per retry automatico"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (ccxt.NetworkError, ccxt.ExchangeError, requests.exceptions.RequestException) as e:
                    if attempt == max_retries - 1:
                        logger.error(f"❌ {func.__name__} fallito dopo {max_retries} tentativi: {e}")
                        raise
                    logger.warning(f"⚠️ {func.__name__} fallito (tentativo {attempt+1}/{max_retries}): {e}")
                    time.sleep(delay * (attempt + 1))  # Exponential backoff
                except Exception as e:
                    # Per altri errori, non ritentare
                    logger.error(f"❌ {func.__name__} errore irreversibile: {e}")
                    raise
            return None
        return wrapper
    return decorator

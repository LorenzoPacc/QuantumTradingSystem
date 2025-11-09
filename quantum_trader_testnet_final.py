import os
import time
import hmac
import hashlib
import requests
import json
from datetime import datetime
from decimal import Decimal, ROUND_DOWN, getcontext
from urllib.parse import urlencode

# ===============================
# CONFIGURAZIONE BASE
# ===============================
RECV_WINDOW = 60000

# ===============================
# FUNZIONI DI SUPPORTO
# ===============================
def get_server_time(base_url):
    try:
        r = requests.get(base_url + '/api/v3/time', timeout=5)
        r.raise_for_status()
        return int(r.json()['serverTime'])
    except Exception:
        return int(time.time() * 1000)

def sign_payload(params: dict, secret_key: str, base_url=None):
    """Restituisce (signed_params, query_string) con signature corretta e timestamp del server."""
    params = dict(params)
    params['recvWindow'] = RECV_WINDOW
    if base_url:
        params['timestamp'] = get_server_time(base_url)
    else:
        params['timestamp'] = int(time.time() * 1000)

    ordered = dict(sorted(params.items()))
    qs = urlencode(ordered, doseq=True)
    signature = hmac.new(secret_key.encode('utf-8'), qs.encode('utf-8'), hashlib.sha256).hexdigest()
    ordered['signature'] = signature
    return ordered, qs + '&signature=' + signature

def api_request(method, endpoint, params=None, signed=False, base_url="https://testnet.binance.vision",
                api_key=None, secret_key=None, max_retries=3):
    """Wrapper API Binance con retry e gestione firma HMAC."""
    url = base_url + endpoint
    params = params or {}

    headers = {}
    if api_key:
        headers['X-MBX-APIKEY'] = api_key

    if signed:
        params_to_send, _ = sign_payload(params, secret_key, base_url)
    else:
        params_to_send = params

    attempt = 0
    backoff = 0.5
    while attempt < max_retries:
        try:
            if method.upper() == 'GET':
                r = requests.get(url, headers=headers, params=params_to_send, timeout=10)
            elif method.upper() == 'POST':
                r = requests.post(url, headers=headers, params=params_to_send, timeout=10)
            elif method.upper() == 'DELETE':
                r = requests.delete(url, headers=headers, params=params_to_send, timeout=10)
            else:
                raise ValueError("Metodo HTTP non supportato")

            if r.status_code in (200, 201):
                try:
                    return r.json()
                except ValueError:
                    return r.text
            if r.status_code in (429, 418) or r.status_code >= 500:
                attempt += 1
                time.sleep(backoff)
                backoff *= 2
                continue

            try:
                err = r.json()
            except:
                err = r.text
            raise RuntimeError(f"API Error {r.status_code}: {err}")

        except requests.exceptions.RequestException as e:
            attempt += 1
            time.sleep(backoff)
            backoff *= 2
            last_exc = e

    raise RuntimeError(f"Errore di rete dopo {max_retries} tentativi: {last_exc}")

def quantize_step_size(quantity: float, step_size_str: str):
    """Arrotonda quantità *verso il basso* al passo di trading corretto."""
    getcontext().prec = 18
    q = Decimal(str(quantity))
    step = Decimal(str(step_size_str))
    exp = abs(step.as_tuple().exponent)
    quant = Decimal(1).scaleb(-exp)
    return q.quantize(quant, rounding=ROUND_DOWN)

# ===============================
# CLASSE PRINCIPALE TRADER
# ===============================
class BinanceTestNetTrader:
    def __init__(self):
        self.base_url = "https://testnet.binance.vision"
        self.api_key = os.getenv('BINANCE_TESTNET_API_KEY', '')
        self.secret_key = os.getenv('BINANCE_TESTNET_SECRET_KEY', '')

        self.balance = 0.0
        self.portfolio = {}
        self.buy_threshold = 0.7
        self.xrp_blocked_cycles = 0

        # Test connessione all'inizializzazione
        if not self.test_connection():
            raise RuntimeError("❌ Impossibile connettersi a Binance TestNet. Controlla le API Key.")

        self.update_balances()

    def test_connection(self):
        """Testa la connessione e le API Key"""
        try:
            data = api_request('GET', '/api/v3/account', signed=True,
                             base_url=self.base_url,
                             api_key=self.api_key, 
                             secret_key=self.secret_key)
            if data and 'accountType' in data:
                self.heartbeat("✅ Connessione TestNet OK - API Key valide!")
                return True
            return False
        except Exception as e:
            self.heartbeat(f"❌ Errore connessione: {e}")
            return False

    def heartbeat(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

    def update_balances(self):
        endpoint = "/api/v3/account"
        try:
            data = api_request('GET', endpoint, signed=True,
                               base_url=self.base_url,
                               api_key=self.api_key,
                               secret_key=self.secret_key)
        except Exception as e:
            self.heartbeat(f"❌ Errore nel recupero bilancio: {e}")
            return

        if data:
            self.balance = 0
            self.portfolio = {}
            for asset in data['balances']:
                free = float(asset['free'])
                locked = float(asset['locked'])
                if free > 0 or locked > 0:
                    if asset['asset'] == 'USDT':
                        self.balance = free
                    else:
                        symbol = f"{asset['asset']}USDT"
                        total = free + locked
                        if total > 0.000001:  # Filtra quantità minuscole
                            self.portfolio[symbol] = total
            self.heartbeat(f"💰 Balance aggiornato: ${self.balance:.2f} USDT")

    def get_symbol_price(self, symbol):
        try:
            data = api_request('GET', '/api/v3/ticker/price', {'symbol': symbol},
                               base_url=self.base_url,
                               api_key=self.api_key)
            return float(data['price']) if data and 'price' in data else None
        except Exception as e:
            self.heartbeat(f"❌ Errore prezzo {symbol}: {e}")
            return None

    def execute_market_buy(self, symbol, usdt_amount):
        self.heartbeat(f"🔄 Inviando BUY: {symbol} - ${usdt_amount:.2f}")
        
        price = self.get_symbol_price(symbol)
        if not price:
            self.heartbeat("❌ Impossibile ottenere prezzo")
            return None

        # Ottieni info simbolo
        try:
            info = api_request('GET', '/api/v3/exchangeInfo',
                               {'symbol': symbol},
                               base_url=self.base_url,
                               api_key=self.api_key)
            symbol_info = next((s for s in info['symbols'] if s['symbol'] == symbol), None)
            if not symbol_info:
                self.heartbeat("❌ Symbol info non trovata")
                return None
        except Exception as e:
            self.heartbeat(f"❌ Errore info simbolo: {e}")
            return None

        # Trova filtri
        lot_filter = next((f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE'), None)
        min_notional_filter = next((f for f in symbol_info['filters'] if f['filterType'] == 'MIN_NOTIONAL'), None)

        # Calcola quantità
        quantity = Decimal(str(usdt_amount)) / Decimal(str(price))
        if lot_filter:
            quantity = quantize_step_size(float(quantity), lot_filter['stepSize'])

        notional = float(quantity) * price
        if min_notional_filter and notional < float(min_notional_filter['minNotional']):
            self.heartbeat(f"⚠️ Notionale minimo non raggiunto: {notional:.8f}")
            return None

        if float(quantity) <= 0:
            self.heartbeat("❌ Quantità non valida")
            return None

        self.heartbeat(f"📊 Dettaglio ordine: {float(quantity):.6f} {symbol} @ ~${price:.4f}")

        # Test ordine prima di eseguire
        try:
            api_request('POST', '/api/v3/order/test',
                        {'symbol': symbol, 'side': 'BUY', 'type': 'MARKET', 'quantity': float(quantity)},
                        signed=True, base_url=self.base_url,
                        api_key=self.api_key, secret_key=self.secret_key)
            self.heartbeat("✅ Test ordine superato")
        except Exception as e:
            self.heartbeat(f"❌ Test ordine fallito: {e}")
            return None

        # Esegui ordine reale
        try:
            result = api_request('POST', '/api/v3/order',
                                 {'symbol': symbol, 'side': 'BUY', 'type': 'MARKET', 'quantity': float(quantity)},
                                 signed=True, base_url=self.base_url,
                                 api_key=self.api_key, secret_key=self.secret_key)

            if result and 'orderId' in result:
                self.heartbeat(f"✅ BUY REALE TestNet COMPLETATO! Order ID: {result['orderId']}")
                time.sleep(2)
                self.update_balances()
                return result
            else:
                self.heartbeat(f"❌ Ordine BUY fallito: {result}")
                return None
        except Exception as e:
            self.heartbeat(f"❌ Errore durante ordine BUY: {e}")
            return None

    def execute_market_sell(self, symbol, quantity):
        self.heartbeat(f"🔄 Inviando SELL: {symbol} - {quantity:.6f}")
        
        # Ottieni info simbolo per lot size
        try:
            info = api_request('GET', '/api/v3/exchangeInfo',
                               {'symbol': symbol},
                               base_url=self.base_url,
                               api_key=self.api_key)
            symbol_info = next((s for s in info['symbols'] if s['symbol'] == symbol), None)
            if symbol_info:
                lot_filter = next((f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE'), None)
                if lot_filter:
                    quantity = quantize_step_size(float(quantity), lot_filter['stepSize'])
        except Exception as e:
            self.heartbeat(f"⚠️ Errore info simbolo SELL: {e}")

        if float(quantity) <= 0:
            self.heartbeat("❌ Quantità non valida per SELL")
            return None

        # Esegui ordine
        try:
            result = api_request('POST', '/api/v3/order',
                                 {'symbol': symbol, 'side': 'SELL', 'type': 'MARKET', 'quantity': float(quantity)},
                                 signed=True, base_url=self.base_url,
                                 api_key=self.api_key, secret_key=self.secret_key)
            
            if result and 'orderId' in result:
                self.heartbeat(f"💰 SELL REALE TestNet COMPLETATO! Order ID: {result['orderId']}")
                time.sleep(2)
                self.update_balances()
                return result
            else:
                self.heartbeat(f"❌ Ordine SELL fallito: {result}")
                return None
        except Exception as e:
            self.heartbeat(f"❌ Errore durante ordine SELL: {e}")
            return None

    def auto_trade(self, symbol, analysis):
        signal = analysis.get('signal')
        score = analysis.get('score', 0)

        # Gestione XRP con sblocco
        if symbol == "XRPUSDT" and self.portfolio.get(symbol, 0) > 0:
            if self.xrp_blocked_cycles > 3:  # Ridotto per test
                self.xrp_blocked_cycles = 0
                self.heartbeat("🔄 XRP sbloccato forzatamente")
                return self.execute_market_sell(symbol, self.portfolio[symbol] * 0.30)
            else:
                self.xrp_blocked_cycles += 1
                self.heartbeat(f"🚫 XRP bloccato (ciclo {self.xrp_blocked_cycles}/3)")
                return None

        # LOGICA BUY - PER TUTTE LE COPPIE
        if signal == "BUY" and score >= self.buy_threshold:
            buy_amount = min(self.balance * 0.05, 30)  # Ridotto per TestNet
            if buy_amount >= 10 and self.balance >= buy_amount:
                self.heartbeat(f"🤖 BUY DECISION: {symbol} (Score: {score:.2f})")
                return self.execute_market_buy(symbol, buy_amount)

        # LOGICA SELL - PER TUTTE LE COPPIE
        if signal == "SELL" and symbol in self.portfolio and self.portfolio[symbol] > 0:
            self.heartbeat(f"🤖 SELL: {symbol} (Score: {score:.2f})")
            return self.execute_market_sell(symbol, self.portfolio[symbol])

        return None

    def print_status(self):
        self.update_balances()
        print(f"\n📊 STATO TESTNET REALE:")
        print(f"   Balance USDT: ${self.balance:.2f}")
        print(f"   Asset in portfolio: {len(self.portfolio)}")
        
        if self.portfolio:
            print(f"   Dettaglio portfolio:")
            for symbol, qty in self.portfolio.items():
                price = self.get_symbol_price(symbol)
                if price:
                    value = qty * price
                    print(f"     • {symbol}: {qty:.6f} (${value:.2f})")
        
        # Calcola valore totale
        total_value = self.balance
        for symbol, qty in self.portfolio.items():
            price = self.get_symbol_price(symbol)
            if price:
                total_value += qty * price
        print(f"   💰 VALORE TOTALE: ${total_value:.2f}")

# ===============================
# ESECUZIONE PRINCIPALE
# ===============================
if __name__ == "__main__":
    print("🚀 QUANTUM TRADING SYSTEM - BINANCE TESTNET REALE")
    print("=" * 60)

    if not os.getenv("BINANCE_TESTNET_API_KEY") or not os.getenv("BINANCE_TESTNET_SECRET_KEY"):
        print("\n❌ ERRORE: Esporta le chiavi TestNet prima di avviare:")
        print("   export BINANCE_TESTNET_API_KEY='tua_api_key'")
        print("   export BINANCE_TESTNET_SECRET_KEY='tua_secret_key'")
        print("\n💡 Ottieni le API Key da: https://testnet.binance.vision/")
        exit(1)

    try:
        trader = BinanceTestNetTrader()
        trader.print_status()

        print("\n🎯 COMANDI PER TESTARE:")
        print("   trader.auto_trade('BTCUSDT', {'signal': 'BUY', 'score': 0.8})")
        print("   trader.auto_trade('ETHUSDT', {'signal': 'BUY', 'score': 0.75})")
        print("   trader.auto_trade('ADAUSDT', {'signal': 'BUY', 'score': 0.85})")
        
        print("\n💡 Per un test immediato, esegui:")
        print("   python3 -c \"")
        print("   from quantum_trader_testnet_final import BinanceTestNetTrader")
        print("   t = BinanceTestNetTrader()")
        print("   t.auto_trade('BTCUSDT', {'signal': 'BUY', 'score': 0.8})")
        print("   \"")

    except Exception as e:
        print(f"\n💥 ERRORE CRITICO: {e}")
        print("   Controlla:")
        print("   1. Le API Key sono corrette?")
        print("   2. Hai fondi sul TestNet?")
        print("   3. La connessione internet funziona?")
        exit(1)

import requests
import time
import json
from datetime import datetime
from decimal import Decimal, ROUND_DOWN

class PaperTradingEngine:
    def __init__(self, starting_balance=150.0):
        self.balance = Decimal(str(starting_balance))
        self.initial_balance = Decimal(str(starting_balance))
        self.portfolio = {}
        self.orders_history = []
        self.order_id = 1000
        self.total_fees = Decimal('0')
        
        print(f"🎮 Paper Trading Engine Inizializzato")
        print(f"💰 Balance Iniziale: €{starting_balance:,.2f}")
        
        if self._test_binance_connection():
            print(f"✅ Connesso a Binance - Prezzi REALI attivi")
        else:
            print(f"⚠️  Connessione Binance fallita")

    def _test_binance_connection(self):
        try:
            price = self.get_real_price('BTCUSDT')
            if price:
                print(f"   🌐 BTC Prezzo Corrente: ${float(price):,.2f}")
                return True
        except Exception as e:
            print(f"   ❌ Errore: {e}")
        return False

    def get_real_price(self, symbol):
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return Decimal(str(data['price']))
            return None
        except:
            return None

    def get_real_24h_data(self, symbol):
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'price': Decimal(str(data['lastPrice'])),
                    'volume': Decimal(str(data['volume'])),
                    'priceChange': Decimal(str(data['priceChange'])),
                    'priceChangePercent': Decimal(str(data['priceChangePercent']))
                }
        except:
            pass
        return None

    def apply_trading_fee(self, amount, fee_pct=0.1):
        """Simula fee Binance (0.1%)"""
        fee = amount * Decimal(str(fee_pct / 100))
        return amount - fee, fee

    def market_buy(self, symbol, usdt_amount):
        timestamp = datetime.now()
        usdt_amount = Decimal(str(usdt_amount))
        
        if usdt_amount > self.balance:
            print(f"❌ Fondi insufficienti! Disponibile: ${self.balance:.2f}")
            return None
        
        price = self.get_real_price(symbol)
        if not price:
            print(f"❌ Impossibile ottenere prezzo per {symbol}")
            return None
        
        # Applica fee trading (0.1%)
        amount_after_fee, fee = self.apply_trading_fee(usdt_amount)
        self.total_fees += fee
        
        quantity = amount_after_fee / price
        self.balance -= usdt_amount
        
        self.portfolio[symbol] = self.portfolio.get(symbol, Decimal('0')) + quantity
        
        order = {
            'orderId': self.order_id,
            'symbol': symbol,
            'side': 'BUY',
            'type': 'MARKET',
            'quantity': float(quantity),
            'price': float(price),
            'usdt_spent': float(usdt_amount),
            'fee': float(fee),
            'timestamp': timestamp,
            'status': 'FILLED (SIMULATED)'
        }
        
        self.orders_history.append(order)
        self.order_id += 1
        
        print(f"[{timestamp.strftime('%H:%M:%S')}] 🟢 BUY SIMULATO:")
        print(f"   {symbol}: {float(quantity):.8f} @ ${float(price):,.4f}")
        print(f"   Totale: ${float(usdt_amount):.2f}")
        print(f"   Fee (0.1%): ${float(fee):.4f}")
        print(f"   Balance rimanente: ${float(self.balance):.2f}")
        
        return order

    def market_sell(self, symbol, quantity=None):
        timestamp = datetime.now()
        
        if quantity is None:
            quantity = self.portfolio.get(symbol, Decimal('0'))
        
        available = self.portfolio.get(symbol, Decimal('0'))
        if quantity > available:
            print(f"❌ Quantità insufficiente! Disponibile: {float(available):.8f}")
            return None
        
        if quantity <= Decimal('0'):
            print(f"❌ Quantità non valida: {float(quantity)}")
            return None
        
        price = self.get_real_price(symbol)
        if not price:
            print(f"❌ Impossibile ottenere prezzo per {symbol}")
            return None
        
        usdt_received = quantity * price
        
        # Applica fee trading (0.1%)
        amount_after_fee, fee = self.apply_trading_fee(usdt_received)
        self.total_fees += fee
        
        self.portfolio[symbol] -= quantity
        
        if self.portfolio[symbol] < Decimal('0.000001'):
            del self.portfolio[symbol]
        
        self.balance += amount_after_fee
        
        order = {
            'orderId': self.order_id,
            'symbol': symbol,
            'side': 'SELL',
            'type': 'MARKET',
            'quantity': float(quantity),
            'price': float(price),
            'usdt_received': float(usdt_received),
            'amount_after_fee': float(amount_after_fee),
            'fee': float(fee),
            'timestamp': timestamp,
            'status': 'FILLED (SIMULATED)'
        }
        
        self.orders_history.append(order)
        self.order_id += 1
        
        print(f"[{timestamp.strftime('%H:%M:%S')}] 🔴 SELL SIMULATO:")
        print(f"   {symbol}: {float(quantity):.8f} @ ${float(price):,.4f}")
        print(f"   Totale: ${float(usdt_received):.2f}")
        print(f"   Fee (0.1%): ${float(fee):.4f}")
        print(f"   Netto: ${float(amount_after_fee):.2f}")
        print(f"   Balance aggiornato: ${float(self.balance):.2f}")
        
        return order

    def check_stop_loss(self, symbol, stop_loss_pct=10):
        """Vendi se loss supera la percentuale specificata"""
        profit_data = self.get_asset_profit(symbol)
        
        if profit_data and profit_data['profit_pct'] < -stop_loss_pct:
            print(f"🚨 STOP LOSS attivato per {symbol} (-{stop_loss_pct}%)")
            print(f"   Loss attuale: {profit_data['profit_pct']:.2f}%")
            return self.market_sell(symbol)
        return None

    def check_take_profit(self, symbol, take_profit_pct=15):
        """Vendi se profit supera la percentuale specificata"""
        profit_data = self.get_asset_profit(symbol)
        
        if profit_data and profit_data['profit_pct'] > take_profit_pct:
            print(f"🎉 TAKE PROFIT per {symbol} (+{take_profit_pct}%)")
            print(f"   Profit attuale: {profit_data['profit_pct']:.2f}%")
            # Vendi metà della posizione
            qty_to_sell = self.portfolio[symbol] * Decimal('0.5')
            return self.market_sell(symbol, qty_to_sell)
        return None

    def get_portfolio_value(self):
        total = self.balance
        
        for symbol, qty in self.portfolio.items():
            price = self.get_real_price(symbol)
            if price:
                total += qty * price
        
        return total

    def calculate_profit(self):
        current_value = self.get_portfolio_value()
        profit = current_value - self.initial_balance
        profit_pct = (profit / self.initial_balance) * 100
        return profit, profit_pct

    def get_asset_profit(self, symbol):
        if symbol not in self.portfolio:
            return None
        
        current_price = self.get_real_price(symbol)
        if not current_price:
            return None
        
        buy_orders = [o for o in self.orders_history 
                     if o['symbol'] == symbol and o['side'] == 'BUY']
        
        if not buy_orders:
            return None
        
        total_cost = Decimal('0')
        total_qty = Decimal('0')
        
        for order in buy_orders:
            total_cost += Decimal(str(order['usdt_spent']))
            total_qty += Decimal(str(order['quantity']))
        
        avg_buy_price = total_cost / total_qty if total_qty > Decimal('0') else Decimal('0')
        profit_pct = ((current_price - avg_buy_price) / avg_buy_price * 100) if avg_buy_price > Decimal('0') else Decimal('0')
        current_value = self.portfolio[symbol] * current_price
        profit_usd = current_value - (self.portfolio[symbol] * avg_buy_price)
        
        return {
            'avg_buy_price': float(avg_buy_price),
            'current_price': float(current_price),
            'profit_pct': float(profit_pct),
            'profit_usd': float(profit_usd),
            'quantity': float(self.portfolio[symbol]),
            'current_value': float(current_value)
        }

    def print_status(self):
        total_value = self.get_portfolio_value()
        profit, profit_pct = self.calculate_profit()
        
        print("\n" + "="*70)
        print("📊 PAPER TRADING STATUS - €150 CAPITALE")
        print("="*70)
        
        print(f"\n💵 LIQUIDITÀ:")
        print(f"   Balance: ${float(self.balance):.2f}")
        
        portfolio_value = total_value - self.balance
        print(f"\n💼 PORTFOLIO:")
        print(f"   Valore Asset: ${float(portfolio_value):.2f}")
        print(f"   Numero Asset: {len(self.portfolio)}")
        
        if self.portfolio:
            print(f"\n🎯 DETTAGLIO ASSET:")
            
            assets_with_data = []
            for symbol, qty in self.portfolio.items():
                profit_data = self.get_asset_profit(symbol)
                if profit_data:
                    assets_with_data.append((symbol, profit_data))
            
            assets_with_data.sort(key=lambda x: x[1]['current_value'], reverse=True)
            
            for symbol, data in assets_with_data:
                emoji = "🟢" if data['profit_pct'] >= 0 else "🔴"
                print(f"   {emoji} {symbol:12}")
                print(f"      Qty: {data['quantity']:.6f}")
                print(f"      Prezzo Acquisto: ${data['avg_buy_price']:.4f}")
                print(f"      Prezzo Corrente: ${data['current_price']:.4f}")
                print(f"      Valore: ${data['current_value']:.2f}")
                print(f"      P&L: ${data['profit_usd']:+.2f} ({data['profit_pct']:+.2f}%)")
        
        print(f"\n💎 TOTALI:")
        print(f"   Valore Totale: ${float(total_value):.2f}")
        print(f"   Capitale Iniziale: ${float(self.initial_balance):.2f}")
        
        if profit >= Decimal('0'):
            print(f"   📈 Profit: +${float(profit):.2f} (+{float(profit_pct):.2f}%) 🎉")
        else:
            print(f"   📉 Loss: ${float(profit):.2f} ({float(profit_pct):.2f}%)")
        
        print(f"\n📋 STATISTICHE:")
        print(f"   Ordini Totali: {len(self.orders_history)}")
        print(f"   Fee Totali Pagate: ${float(self.total_fees):.4f}")
        
        buy_orders = [o for o in self.orders_history if o['side'] == 'BUY']
        sell_orders = [o for o in self.orders_history if o['side'] == 'SELL']
        
        print(f"   Acquisti: {len(buy_orders)}")
        print(f"   Vendite: {len(sell_orders)}")
        
        # Risk Management Status
        print(f"\n🛡️  RISK MANAGEMENT:")
        print(f"   Stop Loss: 10%")
        print(f"   Take Profit: 15% (vendita 50% posizione)")

        print("="*70 + "\n")

    def save_to_json(self, filename='paper_trading_state.json'):
        state = {
            'balance': float(self.balance),
            'initial_balance': float(self.initial_balance),
            'portfolio': {k: float(v) for k, v in self.portfolio.items()},
            'orders_history': [{**o, 'timestamp': o['timestamp'].isoformat()} for o in self.orders_history],
            'order_id': self.order_id,
            'total_fees': float(self.total_fees),
            'saved_at': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"💾 Stato salvato in: {filename}")

    def load_from_json(self, filename='paper_trading_state.json'):
        try:
            with open(filename, 'r') as f:
                state = json.load(f)
            
            self.balance = Decimal(str(state['balance']))
            self.initial_balance = Decimal(str(state['initial_balance']))
            self.portfolio = {k: Decimal(str(v)) for k, v in state['portfolio'].items()}
            self.order_id = state['order_id']
            self.total_fees = Decimal(str(state['total_fees']))
            self.orders_history = [
                {**o, 'timestamp': datetime.fromisoformat(o['timestamp'])}
                for o in state['orders_history']
            ]
            
            print(f"📂 Stato caricato da: {filename}")
            return True
        except FileNotFoundError:
            print(f"⚠️  File non trovato: {filename}")
            return False
        except Exception as e:
            print(f"❌ Errore caricando stato: {e}")
            return False

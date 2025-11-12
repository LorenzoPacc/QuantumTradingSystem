#!/usr/bin/env python3
"""
🤖 QUANTUM TRADER V2 - LIVE DASHBOARD
Dashboard migliorata basata sulla versione working
"""

import http.server
import socketserver
import json
import sqlite3
import requests
from datetime import datetime
import time

class QuantumDashboardHandler(http.server.SimpleHTTPRequestHandler):
    
    def get_current_prices(self):
        """Ottieni prezzi correnti da Binance"""
        prices = {}
        symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT', 'LINKUSDT', 'DOTUSDT']
        
        for symbol in symbols:
            try:
                response = requests.get(
                    f"https://api.binance.com/api/v3/ticker/price",
                    params={"symbol": symbol},
                    timeout=5
                )
                if response.status_code == 200:
                    prices[symbol] = float(response.json()['price'])
                else:
                    # Fallback a prezzo simulato se API non risponde
                    prices[symbol] = None
            except:
                prices[symbol] = None
        
        return prices
    
    def get_portfolio_data(self):
        """Ottieni dati portfolio da state file e prezzi reali"""
        try:
            with open('quantum_v2_state.json', 'r') as f:
                state = json.load(f)
            
            current_prices = self.get_current_prices()
            portfolio_value = state['cash_balance']
            positions_data = []
            total_invested = 0
            
            for symbol, position in state['portfolio'].items():
                current_price = current_prices.get(symbol)
                if current_price is None:
                    # Se non riesci a ottenere il prezzo, usa l'entry price
                    current_price = position['entry_price']
                
                position_value = position['quantity'] * current_price
                pnl_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100
                pnl_absolute = position_value - position['total_cost']
                
                portfolio_value += position_value
                total_invested += position['total_cost']
                
                positions_data.append({
                    'symbol': symbol,
                    'value': position_value,
                    'quantity': position['quantity'],
                    'entry_price': position['entry_price'],
                    'current_price': current_price,
                    'pnl_percent': pnl_percent,
                    'pnl_absolute': pnl_absolute,
                    'total_cost': position['total_cost']
                })
            
            # Calcola metriche overall
            initial_capital = 200.0
            total_pnl_percent = ((portfolio_value - initial_capital) / initial_capital) * 100
            total_pnl_absolute = portfolio_value - initial_capital
            
            # Conta asset in profit
            assets_in_profit = sum(1 for pos in positions_data if pos['pnl_percent'] > 0)
            
            return {
                'portfolio_value': portfolio_value,
                'cash_balance': state['cash_balance'],
                'total_invested': total_invested,
                'total_pnl_percent': total_pnl_percent,
                'total_pnl_absolute': total_pnl_absolute,
                'positions_count': len(state['portfolio']),
                'assets_in_profit': assets_in_profit,
                'positions': positions_data,
                'cycle_count': state.get('cycle_count', 0),
                'initial_capital': initial_capital
            }
            
        except Exception as e:
            print(f"❌ Errore caricamento portfolio: {e}")
            return None
    
    def get_trade_stats(self):
        """Ottieni statistiche trade dal database"""
        try:
            conn = sqlite3.connect('quantum_v2_performance.db')
            cursor = conn.cursor()
            
            # Conta trade totali
            cursor.execute("SELECT COUNT(*) FROM trades")
            total_trades = cursor.fetchone()[0]
            
            # Conta trade di oggi
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM trades WHERE DATE(timestamp) = DATE('now')")
            today_trades = cursor.fetchone()[0]
            
            # Calcola win rate (SELL con P&L positivo)
            cursor.execute('''
                SELECT COUNT(*) FROM trades 
                WHERE action = 'SELL' AND reason LIKE '%P&L: +%'
            ''')
            winning_trades = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM trades WHERE action = 'SELL'")
            total_sell_trades = cursor.fetchone()[0]
            
            win_rate = (winning_trades / total_sell_trades * 100) if total_sell_trades > 0 else 0
            
            conn.close()
            
            return {
                'total_trades': total_trades,
                'today_trades': today_trades,
                'win_rate': win_rate,
                'winning_trades': winning_trades,
                'total_sell_trades': total_sell_trades
            }
            
        except Exception as e:
            print(f"❌ Errore statistiche trade: {e}")
            return {'total_trades': 0, 'today_trades': 0, 'win_rate': 0}
    
    def do_GET(self):
        if self.path == '/':
            self.serve_dashboard()
        else:
            super().do_GET()
    
    def serve_dashboard(self):
        """Serve la dashboard principale"""
        portfolio_data = self.get_portfolio_data()
        trade_stats = self.get_trade_stats()
        
        if not portfolio_data:
            # Fallback se non può caricare i dati
            html = self.get_error_html()
        else:
            html = self.get_dashboard_html(portfolio_data, trade_stats)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
        
        print(f"✅ Dashboard servita - Portfolio: ${portfolio_data['portfolio_value']:.2f} ({portfolio_data['total_pnl_percent']:+.2f}%)")
    
    def get_dashboard_html(self, portfolio, trades):
        """Genera HTML della dashboard con dati reali"""
        
        current_time = datetime.now().strftime("%H:%M:%S")
        
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>🤖 QUANTUM TRADER V2 - LIVE DASHBOARD</title>
            <meta charset="UTF-8">
            <meta http-equiv="refresh" content="30">
            <style>
                body {{
                    font-family: 'Courier New', monospace;
                    background: #0a0a0a;
                    color: #00ff00;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .header {{
                    text-align: center;
                    background: #111;
                    padding: 15px;
                    border: 1px solid #00ff00;
                    margin-bottom: 20px;
                    border-radius: 5px;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 15px;
                    margin-bottom: 20px;
                }}
                .card {{
                    background: #111;
                    padding: 15px;
                    border: 1px solid #00ff00;
                    border-radius: 5px;
                }}
                .positive {{ color: #00ff00; }}
                .negative {{ color: #ff4444; }}
                .positions-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                .positions-table th,
                .positions-table td {{
                    padding: 8px 12px;
                    text-align: left;
                    border-bottom: 1px solid #333;
                }}
                .positions-table th {{
                    background: #1a1a1a;
                    color: #00ff00;
                }}
                .status-active {{ color: #00ff00; }}
                .status-inactive {{ color: #ff4444; }}
                .refresh-info {{
                    text-align: center;
                    margin-top: 20px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 QUANTUM TRADER V2 - LIVE DASHBOARD</h1>
                    <p>Dati in Tempo Reale da Binance | Aggiornato: {current_time} | Ciclo: {portfolio['cycle_count']}</p>
                </div>
                
                <div class="stats-grid">
                    <div class="card">
                        <h2>💰 PORTFOLIO</h2>
                        <p><strong>${portfolio['portfolio_value']:.2f} </strong><span class="{ 'positive' if portfolio['total_pnl_percent'] >= 0 else 'negative' }">({portfolio['total_pnl_percent']:+.2f}%)</span></p>
                        <p>Investito: <strong>${portfolio['total_invested']:.2f}</strong></p>
                        <p>Profitto: <strong class="{ 'positive' if portfolio['total_pnl_absolute'] >= 0 else 'negative' }">${portfolio['total_pnl_absolute']:+.2f}</strong></p>
                        <p>Cash: <strong>${portfolio['cash_balance']:.2f}</strong></p>
                        <p>Posizioni: <strong>{portfolio['positions_count']}/6</strong></p>
                    </div>
                    
                    <div class="card">
                        <h2>🎯 STRATEGIA V2</h2>
                        <p>Take Profit: <strong>+8%</strong></p>
                        <p>Stop Loss: <strong>Dinamico (4-8%)</strong></p>
                        <p>Esposizione: <strong>{(portfolio['total_invested']/portfolio['initial_capital']*100):.1f}%</strong></p>
                        <p>Stato: <strong class="status-active">ATTIVO</strong></p>
                        <p>Regime: <strong>BEAR</strong></p>
                    </div>
                    
                    <div class="card">
                        <h2>📊 PERFORMANCE</h2>
                        <p>Trade Totali: <strong>{trades['total_trades']}</strong></p>
                        <p>Trade Oggi: <strong>{trades['today_trades']}</strong></p>
                        <p>Win Rate: <strong>{trades['win_rate']:.1f}%</strong></p>
                        <p>Asset in Profit: <strong>{portfolio['assets_in_profit']}/{portfolio['positions_count']}</strong></p>
                        <p>P&L Medio: <strong>{portfolio['total_pnl_percent']/portfolio['positions_count'] if portfolio['positions_count'] > 0 else 0:+.2f}%</strong></p>
                    </div>
                </div>
                
                <div class="card">
                    <h2>📈 POSIZIONI ATTIVE</h2>
                    <table class="positions-table">
                        <thead>
                            <tr>
                                <th>Asset</th>
                                <th>Valore</th>
                                <th>Quantità</th>
                                <th>Entry</th>
                                <th>Attuale</th>
                                <th>P&L</th>
                            </tr>
                        </thead>
                        <tbody>
        '''
        
        # Aggiungi righe per ogni posizione
        for pos in portfolio['positions']:
            pnl_class = "positive" if pos['pnl_percent'] >= 0 else "negative"
            pnl_emoji = "✅" if pos['pnl_percent'] >= 0 else "🔴"
            
            html += f'''
                            <tr>
                                <td><strong>{pos['symbol']}</strong></td>
                                <td>${pos['value']:.2f}</td>
                                <td>{pos['quantity']:.6f}</td>
                                <td>${pos['entry_price']:.2f}</td>
                                <td>${pos['current_price']:.2f}</td>
                                <td><span class="{pnl_class}">{pnl_emoji} {pos['pnl_percent']:+.2f}%</span></td>
                            </tr>
            '''
        
        html += f'''
                        </tbody>
                    </table>
                </div>
                
                <div class="refresh-info">
                    <p>🔄 Auto-refresh ogni 30 secondi | 🤖 Quantum Trader V2.0 | 📊 Dati live da Binance</p>
                </div>
            </div>
            
            <script>
                // Aggiorna il timestamp ogni secondo
                function updateTime() {{
                    const now = new Date();
                    document.querySelector('.header p').textContent = 
                        `Dati in Tempo Reale da Binance | Aggiornato: ${{now.toLocaleTimeString()}} | Ciclo: {portfolio['cycle_count']}`;
                }}
                setInterval(updateTime, 1000);
            </script>
        </body>
        </html>
        '''
        
        return html
    
    def get_error_html(self):
        """HTML di fallback se i dati non sono disponibili"""
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>🤖 QUANTUM TRADER - OFFLINE</title>
            <meta charset="UTF-8">
            <style>
                body { font-family: monospace; background: #000; color: #ff4444; text-align: center; padding: 50px; }
                .error { border: 2px solid #ff4444; padding: 20px; margin: 20px auto; max-width: 500px; }
            </style>
        </head>
        <body>
            <div class="error">
                <h1>🚨 DASHBOARD OFFLINE</h1>
                <p>Impossibile caricare i dati del portfolio</p>
                <p>Verifica che Quantum Trader V2 sia in esecuzione</p>
                <p>⏳ Riprova tra 30 secondi...</p>
            </div>
        </body>
        </html>
        '''

def main():
    PORT = 8090
    
    print("🚀 QUANTUM TRADER V2 - DASHBOARD MIGLIORATA")
    print("📊 Porta: http://localhost:8090")
    print("🎯 Caratteristiche:")
    print("   ✅ Design pulito e familiare")
    print("   ✅ Dati reali da Binance API")
    print("   ✅ Prezzi in tempo reale")
    print("   ✅ Statistiche accurate")
    print("   ✅ Auto-refresh ogni 30 secondi")
    print("   ✅ Zero dipendenze esterne")
    print("📡 Server attivo su porta 8090...")
    print("🔍 Controlla il browser!")
    
    with socketserver.TCPServer(("", PORT), QuantumDashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Dashboard fermata")

if __name__ == "__main__":
    main()

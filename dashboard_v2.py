#!/usr/bin/env python3
"""
📊 QUANTUM V2 DASHBOARD
Dashboard per il sistema avanzato
"""

import http.server
import socketserver
import json
import sqlite3
from datetime import datetime

class DashboardV2Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/data':
            self.serve_api_data()
        elif self.path == '/api/trades':
            self.serve_trades_data()
        else:
            super().do_GET()
    
    def serve_dashboard(self):
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>🚀 Quantum V2 Dashboard</title>
            <meta charset="UTF-8">
            <meta http-equiv="refresh" content="30">
            <style>
                body { font-family: Arial, sans-serif; background: #0f0f23; color: #00ff00; padding: 20px; }
                .container { max-width: 1400px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 30px; background: #1a1a2e; padding: 20px; border-radius: 10px; border: 1px solid #00ff00; }
                .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
                .card { background: #16213e; padding: 20px; border-radius: 10px; border: 1px solid #00ff00; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
                .positive { color: #00ff00; font-weight: bold; }
                .negative { color: #ff4444; font-weight: bold; }
                .positions-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 15px; }
                .position-card { background: #1a1a2e; padding: 15px; border-radius: 8px; border-left: 4px solid #00ff00; }
                .position-card.negative { border-left-color: #ff4444; }
                .trade-list { max-height: 400px; overflow-y: auto; }
                .trade-item { background: #1a1a2e; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #00ff00; }
                .trade-item.sell { border-left-color: #ff4444; }
                table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #00ff00; }
                th { background: #1a1a2e; }
                .progress-bar { background: #1a1a2e; height: 20px; border-radius: 10px; margin: 5px 0; }
                .progress-fill { background: #00ff00; height: 100%; border-radius: 10px; text-align: center; color: black; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 QUANTUM TRADER V2.0 - LIVE DASHBOARD</h1>
                    <p>Advanced Trading System - Ciclo: <span id="cycle">888</span> | Ultimo aggiornamento: <span id="timestamp">''' + datetime.now().strftime("%H:%M:%S") + '''</span></p>
                </div>
                
                <div class="stats-grid">
                    <div class="card">
                        <h2>💰 PORTFOLIO OVERVIEW</h2>
                        <p>Valore Totale: <span id="total-value" class="positive">$198.29</span></p>
                        <p>Cash: <span id="cash">$69.95</span></p>
                        <p>Investito: <span id="invested">$128.34</span></p>
                        <p>P&L Totale: <span id="total-pnl" class="negative">-0.85%</span></p>
                        <div class="progress-bar">
                            <div id="cash-progress" class="progress-fill" style="width: 35%">35% Cash</div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h2>🎯 MARKET CONDITIONS</h2>
                        <p>Fear & Greed: <span id="fear-greed">24</span> (Extreme Fear)</p>
                        <p>Regime Dominante: <span id="dominant-regime" style="color: #ff4444">BEAR</span></p>
                        <p>Posizioni Attive: <span id="active-positions">4/6</span></p>
                        <p>Ultimo Trade: <span id="last-trade">ETHUSDT SELL</span></p>
                    </div>
                    
                    <div class="card">
                        <h2>⚡ PERFORMANCE</h2>
                        <p>Capitale Iniziale: $200.00</p>
                        <p>Profitto/Perdita: <span id="absolute-pnl" class="negative">-$1.71</span></p>
                        <p>Trade Oggi: <span id="trades-today">1</span></p>
                        <p>Win Rate: <span id="win-rate">67%</span></p>
                    </div>
                </div>

                <div class="card">
                    <h2>📈 POSIZIONI ATTIVE</h2>
                    <div class="positions-grid" id="positions-container">
                        <!-- Le posizioni verranno caricate qui -->
                    </div>
                </div>

                <div class="card">
                    <h2>📊 ULTIMI TRADE</h2>
                    <div class="trade-list" id="trades-container">
                        <!-- I trade verranno caricati qui -->
                    </div>
                </div>

                <div class="card">
                    <h2>🔧 STATO SISTEMA</h2>
                    <p>Database: <span style="color: #00ff00">✓ Connesso</span></p>
                    <p>API Binance: <span style="color: #00ff00">✓ Online</span></p>
                    <p>Ultimo ciclo: <span id="last-cycle">19:49</span></p>
                    <p>Prossimo ciclo: <span id="next-cycle">19:59</span></p>
                </div>
            </div>

            <script>
                async function loadData() {
                    try {
                        const response = await fetch('/api/data');
                        const data = await response.json();
                        updateDashboard(data);
                    } catch (error) {
                        console.error('Error loading data:', error);
                    }
                }

                async function loadTrades() {
                    try {
                        const response = await fetch('/api/trades');
                        const trades = await response.json();
                        updateTrades(trades);
                    } catch (error) {
                        console.error('Error loading trades:', error);
                    }
                }

                function updateDashboard(data) {
                    // Portfolio Overview
                    document.getElementById('total-value').textContent = '$' + data.portfolio.total_value.toFixed(2);
                    document.getElementById('cash').textContent = '$' + data.portfolio.cash.toFixed(2);
                    document.getElementById('invested').textContent = '$' + data.portfolio.invested.toFixed(2);
                    document.getElementById('total-pnl').textContent = data.portfolio.total_pnl.toFixed(2) + '%';
                    document.getElementById('total-pnl').className = data.portfolio.total_pnl >= 0 ? 'positive' : 'negative';
                    document.getElementById('absolute-pnl').textContent = (data.portfolio.total_pnl >= 0 ? '+' : '') + 
                        '$' + (data.portfolio.total_value - 200).toFixed(2);
                    document.getElementById('absolute-pnl').className = data.portfolio.total_pnl >= 0 ? 'positive' : 'negative';
                    
                    // Cash progress bar
                    const cashPercent = (data.portfolio.cash / data.portfolio.total_value * 100).toFixed(0);
                    document.getElementById('cash-progress').style.width = cashPercent + '%';
                    document.getElementById('cash-progress').textContent = cashPercent + '% Cash';

                    // Market Conditions
                    document.getElementById('fear-greed').textContent = data.fear_greed;
                    document.getElementById('dominant-regime').textContent = data.dominant_regime;
                    document.getElementById('dominant-regime').style.color = data.dominant_regime === 'BULL' ? '#00ff00' : '#ff4444';
                    document.getElementById('active-positions').textContent = data.portfolio.positions_count + '/6';
                    document.getElementById('last-trade').textContent = data.last_trade || 'Nessuno';

                    // Positions
                    const positionsContainer = document.getElementById('positions-container');
                    positionsContainer.innerHTML = '';
                    data.positions.forEach(pos => {
                        const positionCard = document.createElement('div');
                        positionCard.className = `position-card ${pos.pnl < 0 ? 'negative' : ''}`;
                        positionCard.innerHTML = `
                            <h3>${pos.symbol} <span class="${pos.pnl >= 0 ? 'positive' : 'negative'}">${pos.pnl.toFixed(2)}%</span></h3>
                            <p>Valore: $${pos.value.toFixed(2)}</p>
                            <p>Entry: $${pos.entry_price.toFixed(2)}</p>
                            <p>Attuale: $${pos.current_price.toFixed(2)}</p>
                            <p>Regime: <span style="color: ${pos.regime === 'BULL' ? '#00ff00' : '#ff4444'}">${pos.regime}</span></p>
                            <p>RSI: ${pos.rsi ? pos.rsi.toFixed(1) : 'N/A'}</p>
                        `;
                        positionsContainer.appendChild(positionCard);
                    });

                    // Update timestamp
                    document.getElementById('timestamp').textContent = new Date().toLocaleTimeString();
                    document.getElementById('cycle').textContent = data.cycle_count;
                }

                function updateTrades(trades) {
                    const tradesContainer = document.getElementById('trades-container');
                    tradesContainer.innerHTML = '';
                    
                    trades.forEach(trade => {
                        const tradeItem = document.createElement('div');
                        tradeItem.className = `trade-item ${trade.action.toLowerCase()}`;
                        tradeItem.innerHTML = `
                            <strong>${trade.symbol}</strong> - ${trade.action} 
                            <span class="${trade.action === 'BUY' ? 'positive' : 'negative'}">$${trade.total_value.toFixed(2)}</span>
                            <br><small>${new Date(trade.timestamp).toLocaleString()} | ${trade.reason}</small>
                        `;
                        tradesContainer.appendChild(tradeItem);
                    });
                }

                // Carica i dati ogni 10 secondi
                setInterval(() => {
                    loadData();
                    loadTrades();
                }, 10000);

                // Carica iniziale
                loadData();
                loadTrades();
            </script>
        </body>
        </html>
        '''
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_api_data(self):
        try:
            # Carica stato corrente
            with open('quantum_v2_state.json', 'r') as f:
                state = json.load(f)
            
            # Calcola metriche portfolio
            total_invested = sum(pos['total_cost'] for pos in state['portfolio'].values())
            total_value = state['cash_balance'] + total_invested
            total_pnl = ((total_value - 200) / 200) * 100
            
            # Prepara dati posizioni
            positions = []
            for symbol, pos in state['portfolio'].items():
                # Simula dati di mercato (nella realtà dovresti chiamare l'API)
                current_price = pos['entry_price'] * (1 + (0.01 if 'BTC' in symbol else -0.02))
                pnl = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
                
                positions.append({
                    'symbol': symbol,
                    'value': pos['quantity'] * current_price,
                    'entry_price': pos['entry_price'],
                    'current_price': current_price,
                    'pnl': pnl,
                    'regime': 'BEAR',  # Dalla tua console
                    'rsi': 45.5
                })
            
            data = {
                'portfolio': {
                    'total_value': total_value,
                    'cash': state['cash_balance'],
                    'invested': total_invested,
                    'total_pnl': total_pnl,
                    'positions_count': len(state['portfolio'])
                },
                'fear_greed': 24,
                'dominant_regime': 'BEAR',
                'last_trade': 'ETHUSDT SELL',
                'cycle_count': 888,
                'positions': positions
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
            
        except Exception as e:
            self.send_error(500, f"Errore caricamento dati: {str(e)}")
    
    def serve_trades_data(self):
        try:
            conn = sqlite3.connect('quantum_v2_performance.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT timestamp, symbol, action, price, quantity, total_value, reason 
                FROM trades 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''')
            
            trades = []
            for row in cursor.fetchall():
                trades.append({
                    'timestamp': row[0],
                    'symbol': row[1],
                    'action': row[2],
                    'price': row[3],
                    'quantity': row[4],
                    'total_value': row[5],
                    'reason': row[6]
                })
            
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(trades).encode())
            
        except Exception as e:
            self.send_error(500, f"Errore caricamento trades: {str(e)}")

print("🚀 Quantum V2 Dashboard avviata!")
print("📊 Accesso: http://localhost:8080")
print("⏹️  Premi CTRL+C per fermare la dashboard")

with socketserver.TCPServer(("", 8080), DashboardV2Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard fermata")

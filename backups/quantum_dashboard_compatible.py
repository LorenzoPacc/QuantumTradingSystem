import http.server
import socketserver
import threading
import json
import time
import sqlite3
import socket
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# 📊 DASHBOARD COMPATIBILE CON ENTRAMBE LE VERSIONI
# =============================================================================

class QuantumDashboardCompatible:
    """DASHBOARD CHE FUNZIONA SIA CON VECCHIO CHE NUOVO TRADER"""
    
    def __init__(self, port=8081, trading_engine=None):
        self.port = self._find_free_port(port)
        self.trading_engine = trading_engine
        self.stats_cache = {}
        self.cache_timeout = 10
        
    def _find_free_port(self, start_port=8081, max_attempts=10):
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        return start_port + max_attempts
    
    def _check_engine_alive(self):
        if not self.trading_engine:
            return False
        try:
            _ = getattr(self.trading_engine, 'cycle_count', 0)
            return True
        except:
            return False
    
    def get_live_stats(self):
        current_time = time.time()
        
        if 'stats' in self.stats_cache:
            cached_time, stats = self.stats_cache['stats']
            if current_time - cached_time < self.cache_timeout:
                return stats
        
        engine_online = self._check_engine_alive()
        
        stats = {
            'timestamp': datetime.now().isoformat(),
            'system_status': 'ONLINE' if engine_online else 'OFFLINE',
            'cycle_count': getattr(self.trading_engine, 'cycle_count', 0) if engine_online else 0,
            'performance': self._get_performance_data() if engine_online else {'error': 'Bot offline'},
            'portfolio': self._get_portfolio_data() if engine_online else {'error': 'Bot offline'},
            'market_data': self._get_market_data() if engine_online else {'error': 'Bot offline'},
            'recent_trades': self._get_recent_trades() if engine_online else [],
            'risk_metrics': self._get_risk_metrics() if engine_online else {'error': 'Bot offline'},
            'engine_online': engine_online
        }
        
        self.stats_cache['stats'] = (current_time, stats)
        return stats
    
    def _get_performance_data(self):
        try:
            conn = sqlite3.connect('trading_performance.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*), AVG(pnl_percent),
                SUM(CASE WHEN pnl_percent > 0 THEN 1 ELSE 0 END),
                SUM(CASE WHEN pnl_percent <= 0 THEN 1 ELSE 0 END)
                FROM trade_performance
            ''')
            result = cursor.fetchone()
            
            if result and result[0] > 0:
                total_trades, avg_pnl, wins, losses = result
                win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
            else:
                total_trades, avg_pnl, win_rate = 0, 0, 0
            
            cursor.execute('''
                SELECT DATE(timestamp), AVG(pnl_percent)
                FROM trade_performance 
                WHERE timestamp >= datetime('now', '-7 days')
                GROUP BY DATE(timestamp)
                ORDER BY DATE(timestamp)
            ''')
            weekly_results = cursor.fetchall()
            
            chart_data = {
                'labels': [row[0] for row in weekly_results],
                'data': [float(row[1]) for row in weekly_results],
                'cumulative': self._calculate_cumulative([float(row[1]) for row in weekly_results])
            }
            
            conn.close()
            
            return {
                'total_trades': total_trades,
                'avg_pnl': round(avg_pnl, 2),
                'win_rate': round(win_rate, 1),
                'chart_data': chart_data
            }
            
        except Exception as e:
            return {'error': f'Database: {str(e)}'}
    
    def _calculate_cumulative(self, data):
        cumulative = []
        total = 0
        for value in data:
            total += value
            cumulative.append(round(total, 2))
        return cumulative
    
    def _get_portfolio_data(self):
        if not self.trading_engine:
            return {'error': 'Trading engine not connected'}
        
        try:
            # 🎯 COMPATIBILITÀ: supporta sia vecchio che nuovo trader
            trader = self.trading_engine
            
            # Metodo 1: Nuovo trader (QuantumTraderUltimateFixed)
            if hasattr(trader, 'get_portfolio_value'):
                portfolio_value = trader.get_portfolio_value()
                cash = getattr(trader, 'cash_balance', 0)
                portfolio_dict = getattr(trader, 'portfolio', {})
            # Metodo 2: Vecchio trader (QuantumAITraderUltimate)  
            elif hasattr(trader, 'portfolio_manager'):
                portfolio_manager = trader.portfolio_manager
                portfolio_value = portfolio_manager.get_portfolio_value()
                cash = float(portfolio_manager.cash_balance)
                portfolio_dict = portfolio_manager.portfolio
            else:
                return {'error': 'Trader structure not recognized'}
            
            positions = []
            for symbol, position in portfolio_dict.items():
                try:
                    current_price = trader.market_data.get_real_price(symbol)
                    if current_price:
                        # 🎯 COMPATIBILITÀ: strutture diverse
                        if 'quantity' in position:
                            quantity = position['quantity']
                            entry_price = position.get('entry_price', 0)
                            total_cost = position.get('total_cost', quantity * entry_price)
                        else:
                            quantity = position['quantity']
                            entry_price = position['entry_price']
                            total_cost = position['total_cost']
                        
                        value = quantity * current_price
                        pnl_pct = ((current_price - entry_price) / entry_price) * 100
                        
                        # Calcola giorni holding
                        first_entry = position.get('first_entry', time.time())
                        if isinstance(first_entry, (int, float)):
                            holding_days = (time.time() - first_entry) / (24 * 3600)
                        else:
                            holding_days = 0
                        
                        positions.append({
                            'symbol': symbol,
                            'quantity': float(quantity),
                            'entry_price': entry_price,
                            'current_price': current_price,
                            'value': round(value, 2),
                            'pnl_pct': round(pnl_pct, 2),
                            'holding_days': round(holding_days, 1)
                        })
                except Exception as e:
                    print(f"⚠️  Errore posizione {symbol}: {e}")
                    continue
            
            # Calcola esposizione
            if portfolio_value > 0:
                exposure = (portfolio_value - cash) / portfolio_value
            else:
                exposure = 0
            
            return {
                'total_value': round(portfolio_value, 2),
                'cash': round(cash, 2),
                'exposure_pct': round(exposure * 100, 1),
                'positions': positions,
                'position_count': len(positions)
            }
            
        except Exception as e:
            return {'error': f'Portfolio: {str(e)}'}
    
    def _get_market_data(self):
        if not self.trading_engine:
            return {'error': 'Trading engine not connected'}
        
        try:
            market_data = self.trading_engine.market_data
            assets = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT']
            
            prices = {}
            for symbol in assets:
                try:
                    price = market_data.get_real_price(symbol)
                    if price:
                        prices[symbol] = round(price, 2)
                except Exception:
                    prices[symbol] = None
            
            fgi = market_data.get_fear_greed_index()
            btc_dominance = market_data.get_btc_dominance()
            
            return {
                'prices': prices,
                'fear_greed': fgi,
                'btc_dominance': round(btc_dominance, 1),
                'market_sentiment': self._get_sentiment_label(fgi)
            }
            
        except Exception as e:
            return {'error': f'Market data: {str(e)}'}
    
    def _get_recent_trades(self):
        if not self.trading_engine:
            return []
        
        try:
            # 🎯 COMPATIBILITÀ: cerca trade history in diverse posizioni
            trader = self.trading_engine
            
            # Metodo 1: Nuovo trader
            if hasattr(trader, 'portfolio'):
                # Per nuovo trader, simula trade history
                trades = []
                for symbol, position in trader.portfolio.items():
                    trades.append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'symbol': symbol,
                        'action': 'BUY',
                        'quantity': round(position['quantity'], 6),
                        'price': position['entry_price'],
                        'amount': position['total_cost'],
                        'profit_pct': 0.0,
                        'reason': 'AGGRESSIVE_BUY'
                    })
                return trades[-10:]  # Ultimi 10
                
            # Metodo 2: Vecchio trader
            elif hasattr(trader, 'portfolio_manager'):
                portfolio_manager = trader.portfolio_manager
                recent_trades = getattr(portfolio_manager, 'trade_history', [])[-10:]
                
                formatted_trades = []
                for trade in reversed(recent_trades):
                    try:
                        formatted_trades.append({
                            'timestamp': trade['timestamp'].strftime('%H:%M:%S') if hasattr(trade['timestamp'], 'strftime') else str(trade['timestamp']),
                            'symbol': trade['symbol'],
                            'action': trade['action'],
                            'quantity': round(trade.get('quantity', 0), 6),
                            'price': round(trade.get('price', 0), 2),
                            'amount': round(trade.get('amount', 0), 2),
                            'profit_pct': round(trade.get('profit_pct', 0), 2) if 'profit_pct' in trade else None,
                            'reason': trade.get('reason', 'N/A')[:50]
                        })
                    except Exception as e:
                        continue
                
                return formatted_trades
            else:
                return []
            
        except Exception as e:
            return [{'error': f'Trades: {str(e)}'}]
    
    def _get_risk_metrics(self):
        if not self.trading_engine:
            return {'error': 'Trading engine not connected'}
        
        try:
            trader = self.trading_engine
            
            # 🎯 COMPATIBILITÀ: parametri da diverse posizioni
            if hasattr(trader, 'learning_engine'):
                params = trader.learning_engine.optimal_params
            else:
                # Default se non trovato
                params = {
                    'max_portfolio_exposure': 0.4,
                    'position_size_base': 0.15,
                    'take_profit_base': 8.0,
                    'stop_loss_base': -4.0
                }
            
            # Calcola esposizione corrente
            portfolio_data = self._get_portfolio_data()
            current_exposure = portfolio_data.get('exposure_pct', 0) / 100 if 'error' not in portfolio_data else 0
            
            return {
                'current_exposure': round(current_exposure * 100, 1),
                'max_exposure': params['max_portfolio_exposure'] * 100,
                'position_size_base': params['position_size_base'] * 100,
                'max_position_size': params.get('max_position_size', 45),
                'take_profit': params['take_profit_base'],
                'stop_loss': params['stop_loss_base']
            }
            
        except Exception as e:
            return {'error': f'Risk metrics: {str(e)}'}
    
    def _get_sentiment_label(self, fgi):
        if fgi < 25: return "Extreme Fear"
        elif fgi < 40: return "Fear" 
        elif fgi < 60: return "Neutral"
        elif fgi < 75: return "Greed"
        else: return "Extreme Greed"
    
    def start_dashboard(self):
        handler = self._create_handler()
        
        try:
            with socketserver.TCPServer(("", self.port), handler) as httpd:
                print(f"📊 QUANTUM DASHBOARD COMPATIBILE: http://localhost:{self.port}")
                print("🔄 Dashboard in esecuzione... Premi Ctrl+C per fermare")
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Dashboard fermata")
    
    def _create_handler(self):
        dashboard = self
        
        class DashboardHandler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                status_code = str(args[1]) if len(args) > 1 else ""
                if status_code.startswith('4') or status_code.startswith('5'):
                    super().log_message(format, *args)
            
            def do_GET(self):
                try:
                    if self.path == '/api/stats':
                        self._send_stats()
                    elif self.path == '/api/chart-data':
                        self._send_chart_data()
                    elif self.path == '/':
                        self._send_dashboard()
                    else:
                        super().do_GET()
                except Exception as e:
                    self._send_error(f"Server error: {str(e)}")
            
            def _send_stats(self):
                stats = dashboard.get_live_stats()
                self._send_json_response(stats)
            
            def _send_chart_data(self):
                stats = dashboard.get_live_stats()
                chart_data = stats.get('performance', {}).get('chart_data', {})
                self._send_json_response(chart_data)
            
            def _send_dashboard(self):
                self.path = '/dashboard_compatible.html'
                try:
                    super().do_GET()
                except FileNotFoundError:
                    self._send_error("Dashboard HTML non trovata")
            
            def _send_json_response(self, data):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            
            def _send_error(self, message, code=500):
                self.send_response(code)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': message}).encode())
        
        return DashboardHandler

def create_compatible_dashboard_html():
    html_content = '''
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantum AI Trader - Dashboard Compatibile</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%); color: #ffffff; min-height: 100vh; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; padding: 20px; background: rgba(255, 255, 255, 0.05); border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }
        .header h1 { font-size: 2.5em; background: linear-gradient(45deg, #00ff88, #00ccff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }
        .card h2 { color: #00ff88; margin-bottom: 15px; font-size: 1.3em; border-bottom: 2px solid #00ff88; padding-bottom: 5px; }
        .stat-item { display: flex; justify-content: space-between; margin-bottom: 10px; padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
        .stat-value { font-weight: bold; color: #00ccff; }
        .positive { color: #00ff88; } .negative { color: #ff4444; } .neutral { color: #ffaa00; }
        .chart-container { background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; margin-bottom: 30px; height: 400px; }
        .positions-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
        .position-card { background: rgba(255, 255, 255, 0.03); border-radius: 10px; padding: 15px; border-left: 4px solid #00ff88; }
        .position-card.negative { border-left-color: #ff4444; }
        .refresh-info { text-align: center; margin-top: 20px; color: #888; font-size: 0.9em; }
        .market-sentiment { display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; margin-left: 10px; }
        .sentiment-fear { background: #ff4444; color: white; } .sentiment-greed { background: #00ff88; color: black; } .sentiment-neutral { background: #ffaa00; color: black; }
        .error-banner { position: fixed; top: 0; left: 0; right: 0; background: #ff4444; color: white; padding: 15px; text-align: center; z-index: 9999; font-weight: bold; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
        .loading { animation: pulse 1.5s infinite; }
    </style>
</head>
<body>
    <div id="errorBanner" style="display: none;"></div>
    <div class="container">
        <div class="header">
            <h1>🤖 QUANTUM AI TRADER</h1>
            <p>Dashboard Compatibile - Monitoraggio in Tempo Reale</p>
            <div id="lastUpdate" class="refresh-info"></div>
        </div>
        
        <div class="stats-grid">
            <div class="card"><h2>📈 Performance</h2><div id="performanceStats"><div class="loading">Caricamento...</div></div></div>
            <div class="card"><h2>💰 Portfolio</h2><div id="portfolioStats"><div class="loading">Caricamento...</div></div></div>
            <div class="card"><h2>🌐 Mercato</h2><div id="marketStats"><div class="loading">Caricamento...</div></div></div>
            <div class="card"><h2>🛡️ Risk Management</h2><div id="riskStats"><div class="loading">Caricamento...</div></div></div>
        </div>
        
        <div class="chart-container">
            <h2>📊 Performance Cumulative</h2>
            <canvas id="performanceChart"></canvas>
        </div>
        
        <div class="card"><h2>🎯 Posizioni Attive</h2><div id="activePositionsContainer" class="positions-grid"><div class="loading">Caricamento...</div></div></div>
        <div class="card"><h2>🔄 Ultimi Trade</h2><div id="recentTradesContainer"><div class="loading">Caricamento...</div></div></div>
    </div>

    <script>
        let updateInterval, chart, consecutiveErrors = 0;
        const MAX_ERRORS = 3;
        
        function initializeChart() {
            const ctx = document.getElementById('performanceChart').getContext('2d');
            chart = new Chart(ctx, {
                type: 'line', data: { labels: [], datasets: [{
                    label: 'P&L Cumulative (%)', data: [], borderColor: '#00ff88',
                    backgroundColor: 'rgba(0, 255, 136, 0.1)', borderWidth: 2, fill: true, tension: 0.4
                }]}, options: { responsive: true, maintainAspectRatio: false }
            });
        }
        
        function updateDashboard() {
            fetch('/api/stats').then(r => r.ok ? r.json() : Promise.reject('HTTP ' + r.status))
            .then(data => {
                consecutiveErrors = 0; hideErrorBanner();
                updatePerformance(data.performance, data.cycle_count);
                updatePortfolio(data.portfolio);
                updateMarket(data.market_data);
                updateRisk(data.risk_metrics);
                updatePositions(data.portfolio.positions);
                updateRecentTrades(data.recent_trades);
                updateSystemInfo(data);
                
                if (data.performance?.chart_data) {
                    chart.data.labels = data.performance.chart_data.labels;
                    chart.data.datasets[0].data = data.performance.chart_data.cumulative;
                    chart.update('none');
                }
                
                document.getElementById('lastUpdate').textContent = 'Ultimo aggiornamento: ' + new Date().toLocaleTimeString();
            })
            .catch(e => {
                console.error('Errore:', e); consecutiveErrors++;
                showErrorBanner('Errore connessione: ' + e);
                document.getElementById('systemStatus').textContent = 'OFFLINE';
                document.getElementById('systemStatus').className = 'stat-value negative';
                if (consecutiveErrors >= MAX_ERRORS) {
                    showErrorBanner('❌ Connessione persa - Ricarica la pagina');
                    clearInterval(updateInterval);
                }
            });
        }
        
        function updatePerformance(perf, cycles) {
            const container = document.getElementById('performanceStats');
            if (perf?.error) { container.innerHTML = `<div class="stat-item"><span>Errore:</span><span class="negative">${perf.error}</span></div>`; return; }
            container.innerHTML = `
                <div class="stat-item"><span>Trade Totali:</span><span class="stat-value">${perf.total_trades || 0}</span></div>
                <div class="stat-item"><span>P&L Medio:</span><span class="stat-value ${(perf.avg_pnl || 0) >= 0 ? 'positive' : 'negative'}">${perf.avg_pnl || 0}%</span></div>
                <div class="stat-item"><span>Win Rate:</span><span class="stat-value">${perf.win_rate || 0}%</span></div>
                <div class="stat-item"><span>Cicli Eseguiti:</span><span class="stat-value">${cycles || 0}</span></div>
            `;
        }
        
        function updatePortfolio(port) {
            const container = document.getElementById('portfolioStats');
            if (port?.error) { container.innerHTML = `<div class="stat-item"><span>Errore:</span><span class="negative">${port.error}</span></div>`; return; }
            container.innerHTML = `
                <div class="stat-item"><span>Valore Totale:</span><span class="stat-value">$${port.total_value || 0}</span></div>
                <div class="stat-item"><span>Cash Disponibile:</span><span class="stat-value">$${port.cash || 0}</span></div>
                <div class="stat-item"><span>Esposizione:</span><span class="stat-value">${port.exposure_pct || 0}%</span></div>
                <div class="stat-item"><span>Posizioni Attive:</span><span class="stat-value">${port.position_count || 0}</span></div>
            `;
        }
        
        function updateMarket(market) {
            const container = document.getElementById('marketStats');
            if (market?.error) { container.innerHTML = `<div class="stat-item"><span>Errore:</span><span class="negative">${market.error}</span></div>`; return; }
            const sentiment = market.market_sentiment || 'Neutral';
            container.innerHTML = `
                <div class="stat-item"><span>Fear & Greed:</span><span class="stat-value">${market.fear_greed || 0}</span></div>
                <div class="stat-item"><span>Sentiment:</span><span class="market-sentiment sentiment-${sentiment.toLowerCase().includes('fear')?'fear':sentiment.toLowerCase().includes('greed')?'greed':'neutral'}">${sentiment}</span></div>
                <div class="stat-item"><span>BTC Dominance:</span><span class="stat-value">${market.btc_dominance || 0}%</span></div>
                <div class="stat-item"><span>Stato Sistema:</span><span class="stat-value positive" id="systemStatus">ONLINE</span></div>
            `;
        }
        
        function updateRisk(risk) {
            const container = document.getElementById('riskStats');
            if (risk?.error) { container.innerHTML = `<div class="stat-item"><span>Errore:</span><span class="negative">${risk.error}</span></div>`; return; }
            container.innerHTML = `
                <div class="stat-item"><span>Esposizione Attuale:</span><span class="stat-value">${risk.current_exposure || 0}%</span></div>
                <div class="stat-item"><span>Esposizione Max:</span><span class="stat-value">${risk.max_exposure || 0}%</span></div>
                <div class="stat-item"><span>Take Profit:</span><span class="stat-value">${risk.take_profit || 0}%</span></div>
                <div class="stat-item"><span>Stop Loss:</span><span class="stat-value">${risk.stop_loss || 0}%</span></div>
            `;
        }
        
        function updatePositions(positions) {
            const container = document.getElementById('activePositionsContainer');
            if (!positions || positions.length === 0) { container.innerHTML = '<div class="position-card">Nessuna posizione attiva</div>'; return; }
            container.innerHTML = positions.map(p => `
                <div class="position-card ${(p.pnl_pct || 0) < 0 ? 'negative' : ''}">
                    <div style="font-weight: bold; margin-bottom: 8px;">${p.symbol}</div>
                    <div style="font-size: 0.9em;">
                        <div>Quantità: ${p.quantity}</div><div>Entry: $${p.entry_price}</div>
                        <div>Current: $${p.current_price}</div><div>Valore: $${p.value}</div>
                        <div>P&L: <span class="${(p.pnl_pct || 0) >= 0 ? 'positive' : 'negative'}">${p.pnl_pct}%</span></div>
                        <div>Giorni: ${p.holding_days}</div>
                    </div>
                </div>
            `).join('');
        }
        
        function updateRecentTrades(trades) {
            const container = document.getElementById('recentTradesContainer');
            if (!trades || trades.length === 0) { container.innerHTML = '<div>Nessun trade recente</div>'; return; }
            container.innerHTML = trades.map(t => `
                <div style="border-bottom: 1px solid rgba(255,255,255,0.1); padding: 8px 0;">
                    <strong>${t.timestamp}</strong> - ${t.symbol} - 
                    <span class="${t.action === 'BUY' ? 'positive' : 'negative'}">${t.action}</span> - 
                    $${t.amount} - ${t.reason}
                </div>
            `).join('');
        }
        
        function updateSystemInfo(data) {
            document.getElementById('systemStatus').textContent = data.system_status;
            document.getElementById('systemStatus').className = 'stat-value ' + (data.system_status === 'ONLINE' ? 'positive' : 'negative');
        }
        
        function showErrorBanner(msg) { const b = document.getElementById('errorBanner'); b.textContent = msg; b.className = 'error-banner'; b.style.display = 'block'; }
        function hideErrorBanner() { document.getElementById('errorBanner').style.display = 'none'; }
        
        document.addEventListener('DOMContentLoaded', function() {
            initializeChart();
            updateDashboard();
            updateInterval = setInterval(updateDashboard, 5000);
        });
    </script>
</body>
</html>
    '''
    
    with open('dashboard_compatible.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("✅ Dashboard compatibile creata!")

def start_compatible_dashboard(trading_engine=None, port=8081):
    create_compatible_dashboard_html()
    dashboard = QuantumDashboardCompatible(port=port, trading_engine=trading_engine)
    dashboard_thread = threading.Thread(target=dashboard.start_dashboard, daemon=True)
    dashboard_thread.start()
    return dashboard

if __name__ == "__main__":
    print("🚀 Avvio Quantum Dashboard Compatibile...")
    start_compatible_dashboard(port=8082)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Dashboard fermata")

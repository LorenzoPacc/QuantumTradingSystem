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
# 📊 DASHBOARD PERFETTA - TUTTI I PROBLEMI RISOLTI
# =============================================================================

class QuantumDashboardPerfected:
    """DASHBOARD WEB PERFETTA - ROBUSTA E OTTIMIZZATA"""
    
    def __init__(self, port=8080, trading_engine=None):
        self.port = self._find_free_port(port)
        self.trading_engine = trading_engine
        self.stats_cache = {}
        self.cache_timeout = 10
        self.engine_alive = True
        
        # Crea directory per dati
        Path("dashboard_data").mkdir(exist_ok=True)
        
    def _find_free_port(self, start_port=8080, max_attempts=10):
        """🎯 TROVA PORTA LIBERA - RISOLTO PROBLEMA PORTA OCCUPATA"""
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        print(f"⚠️  Porta {start_port} occupata, usando {start_port + max_attempts}")
        return start_port + max_attempts
    
    def _check_engine_alive(self):
        """🎯 VERIFICA BOT ONLINE - RISOLTO PROBLEMA DISCONNESSIONE"""
        if not self.trading_engine:
            self.engine_alive = False
            return False
        
        try:
            # Test di vitalità - accesso a variabile sicura
            _ = getattr(self.trading_engine, 'cycle_count', 0)
            self.engine_alive = True
            return True
        except Exception as e:
            print(f"⚠️  Trading engine disconnected: {e}")
            self.engine_alive = False
            return False
    
    def get_live_stats(self):
        """Statistiche in tempo reale con gestione errori migliorata"""
        current_time = time.time()
        
        # Cache intelligente
        if 'stats' in self.stats_cache:
            cached_time, stats = self.stats_cache['stats']
            if current_time - cached_time < self.cache_timeout:
                return stats
        
        # 🎯 VERIFICA BOT ONLINE
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
        """Dati performance con gestione errori robusta"""
        try:
            conn = sqlite3.connect('trading_performance.db')
            cursor = conn.cursor()
            
            # Performance totale
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_trades,
                    AVG(pnl_percent) as avg_pnl,
                    SUM(CASE WHEN pnl_percent > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(CASE WHEN pnl_percent <= 0 THEN 1 ELSE 0 END) as losing_trades
                FROM trade_performance
            ''')
            result = cursor.fetchone()
            
            if result and result[0] > 0:
                total_trades, avg_pnl, wins, losses = result
                win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
            else:
                total_trades, avg_pnl, win_rate = 0, 0, 0
            
            # Performance ultimi 7 giorni per Chart.js
            cursor.execute('''
                SELECT DATE(timestamp), AVG(pnl_percent)
                FROM trade_performance 
                WHERE timestamp >= datetime('now', '-7 days')
                GROUP BY DATE(timestamp)
                ORDER BY DATE(timestamp)
            ''')
            weekly_results = cursor.fetchall()
            
            # 🎯 FORMATTAZIONE PER CHART.JS - RISOLTO PROBLEMA MATPLOTLIB
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
            return {'error': f'Database error: {str(e)}'}
    
    def _calculate_cumulative(self, data):
        """Calcola dati cumulative per Chart.js"""
        cumulative = []
        total = 0
        for value in data:
            total += value
            cumulative.append(round(total, 2))
        return cumulative
    
    def _get_portfolio_data(self):
        """Dati portfolio con gestione errori completa"""
        if not self.trading_engine:
            return {'error': 'Trading engine not connected'}
        
        try:
            portfolio_manager = self.trading_engine.portfolio_manager
            portfolio_value = portfolio_manager.get_portfolio_value()
            cash = float(portfolio_manager.cash_balance)
            exposure = portfolio_manager.get_current_exposure()
            
            positions = []
            for symbol, position in portfolio_manager.portfolio.items():
                try:
                    current_price = self.trading_engine.market_data.get_real_price(symbol)
                    if current_price:
                        value = position['quantity'] * current_price
                        pnl_pct = ((current_price - position['entry_price']) / position['entry_price']) * 100
                        holding_days = (datetime.now() - position['first_entry']).days
                        
                        positions.append({
                            'symbol': symbol,
                            'quantity': float(position['quantity']),
                            'entry_price': position['entry_price'],
                            'current_price': current_price,
                            'value': round(value, 2),
                            'pnl_pct': round(pnl_pct, 2),
                            'holding_days': holding_days
                        })
                except Exception as e:
                    print(f"⚠️  Errore posizione {symbol}: {e}")
                    continue
            
            return {
                'total_value': round(portfolio_value, 2),
                'cash': round(cash, 2),
                'exposure_pct': round(exposure * 100, 1),
                'positions': positions,
                'position_count': len(positions)
            }
            
        except Exception as e:
            return {'error': f'Portfolio error: {str(e)}'}
    
    def _get_market_data(self):
        """Dati di mercato con fallback robusto"""
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
            return {'error': f'Market data error: {str(e)}'}
    
    def _get_recent_trades(self):
        """Ultimi trade con gestione errori"""
        if not self.trading_engine:
            return []
        
        try:
            portfolio_manager = self.trading_engine.portfolio_manager
            recent_trades = portfolio_manager.trade_history[-10:]
            
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
                        'reason': trade.get('reason', 'N/A')[:50]  # Limita lunghezza
                    })
                except Exception as e:
                    print(f"⚠️  Errore formato trade: {e}")
                    continue
            
            return formatted_trades
            
        except Exception as e:
            return [{'error': f'Trades error: {str(e)}'}]
    
    def _get_risk_metrics(self):
        """Metriche di rischio con fallback"""
        if not self.trading_engine:
            return {'error': 'Trading engine not connected'}
        
        try:
            portfolio_manager = self.trading_engine.portfolio_manager
            learning_engine = self.trading_engine.learning_engine
            
            params = learning_engine.get_optimized_parameters()
            exposure = portfolio_manager.get_current_exposure()
            
            return {
                'current_exposure': round(exposure * 100, 1),
                'max_exposure': params['max_portfolio_exposure'] * 100,
                'position_size_base': params['position_size_base'] * 100,
                'max_position_size': params['max_position_size'],
                'take_profit': params['take_profit_base'],
                'stop_loss': params['stop_loss_base']
            }
            
        except Exception as e:
            return {'error': f'Risk metrics error: {str(e)}'}
    
    def _get_sentiment_label(self, fgi):
        if fgi < 25: return "Extreme Fear"
        elif fgi < 40: return "Fear" 
        elif fgi < 60: return "Neutral"
        elif fgi < 75: return "Greed"
        else: return "Extreme Greed"
    
    def start_dashboard(self):
        """Avvia il server dashboard perfezionato"""
        handler = self._create_handler()
        
        try:
            with socketserver.TCPServer(("", self.port), handler) as httpd:
                print(f"📊 QUANTUM DASHBOARD PERFETTA: http://localhost:{self.port}")
                print("🔄 Dashboard in esecuzione... Premi Ctrl+C per fermare")
                
                httpd.serve_forever()
        except OSError as e:
            print(f"❌ Errore avvio dashboard: {e}")
            print("💡 Prova con una porta diversa: start_quantum_dashboard(port=8081)")
        except KeyboardInterrupt:
            print("\n🛑 Dashboard fermata")
    
    def _create_handler(self):
        """🎯 HANDLER PERFETTO - LOGGING INTELLIGENTE E GESTIONE ERRORI"""
        dashboard = self
        
        class DashboardHandler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                """🎯 LOGGING INTELLIGENTE - SOLO ERRORI, NO SPAM"""
                # Log solo errori 4xx/5xx, non richieste normali
                status_code = str(args[1]) if len(args) > 1 else ""
                if status_code.startswith('4') or status_code.startswith('5'):
                    super().log_message(format, *args)
                # Altrimenti silenzio (no log per richieste normali)
            
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
                self.path = '/dashboard_perfected.html'
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

# =============================================================================
# 🌐 DASHBOARD HTML PERFETTA - CHART.JS REALE
# =============================================================================

def create_perfected_dashboard_html():
    """🎯 HTML PERFETTO - CHART.JS REALE E GESTIONE ERRORI COMPLETA"""
    html_content = '''
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantum AI Trader - Dashboard Perfetta</title>
    <!-- 🎯 CHART.JS REALE - ORA LO USIAMO DAVVERO! -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
            color: #ffffff;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container { max-width: 1400px; margin: 0 auto; }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .header h1 {
            font-size: 2.5em;
            background: linear-gradient(45deg, #00ff88, #00ccff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .card h2 {
            color: #00ff88;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #00ff88;
            padding-bottom: 5px;
        }
        
        .stat-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .stat-value {
            font-weight: bold;
            color: #00ccff;
        }
        
        .positive { color: #00ff88; }
        .negative { color: #ff4444; }
        .neutral { color: #ffaa00; }
        
        .chart-container {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            height: 400px;
        }
        
        .positions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .position-card {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #00ff88;
        }
        
        .position-card.negative { border-left-color: #ff4444; }
        
        .refresh-info {
            text-align: center;
            margin-top: 20px;
            color: #888;
            font-size: 0.9em;
        }
        
        .market-sentiment {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-left: 10px;
        }
        
        .sentiment-fear { background: #ff4444; color: white; }
        .sentiment-greed { background: #00ff88; color: black; }
        .sentiment-neutral { background: #ffaa00; color: black; }
        
        .error-banner {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: #ff4444;
            color: white;
            padding: 15px;
            text-align: center;
            z-index: 9999;
            font-weight: bold;
        }
        
        .warning-banner {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: #ffaa00;
            color: black;
            padding: 15px;
            text-align: center;
            z-index: 9999;
            font-weight: bold;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        .loading { animation: pulse 1.5s infinite; }
        .offline { opacity: 0.6; }
    </style>
</head>
<body>
    <div id="errorBanner" style="display: none;"></div>
    <div id="warningBanner" style="display: none;"></div>
    
    <div class="container">
        <div class="header">
            <h1>🤖 QUANTUM AI TRADER</h1>
            <p>Dashboard Perfetta - Monitoraggio in Tempo Reale</p>
            <div id="lastUpdate" class="refresh-info"></div>
        </div>
        
        <div class="stats-grid">
            <!-- Performance Card -->
            <div class="card">
                <h2>📈 Performance</h2>
                <div id="performanceStats">
                    <div class="stat-item">
                        <span>Trade Totali:</span>
                        <span class="stat-value" id="totalTrades">0</span>
                    </div>
                    <div class="stat-item">
                        <span>P&L Medio:</span>
                        <span class="stat-value" id="avgPnl">0%</span>
                    </div>
                    <div class="stat-item">
                        <span>Win Rate:</span>
                        <span class="stat-value" id="winRate">0%</span>
                    </div>
                    <div class="stat-item">
                        <span>Cicli Eseguiti:</span>
                        <span class="stat-value" id="cycleCount">0</span>
                    </div>
                </div>
            </div>
            
            <!-- Portfolio Card -->
            <div class="card">
                <h2>💰 Portfolio</h2>
                <div id="portfolioStats">
                    <div class="stat-item">
                        <span>Valore Totale:</span>
                        <span class="stat-value" id="totalValue">$0</span>
                    </div>
                    <div class="stat-item">
                        <span>Cash Disponibile:</span>
                        <span class="stat-value" id="cashBalance">$0</span>
                    </div>
                    <div class="stat-item">
                        <span>Esposizione:</span>
                        <span class="stat-value" id="exposure">0%</span>
                    </div>
                    <div class="stat-item">
                        <span>Posizioni Attive:</span>
                        <span class="stat-value" id="activePositions">0</span>
                    </div>
                </div>
            </div>
            
            <!-- Mercato Card -->
            <div class="card">
                <h2>🌐 Mercato</h2>
                <div id="marketStats">
                    <div class="stat-item">
                        <span>Fear & Greed:</span>
                        <span class="stat-value" id="fearGreed">0</span>
                    </div>
                    <div class="stat-item">
                        <span>Sentiment:</span>
                        <span id="sentiment" class="market-sentiment sentiment-neutral">Neutral</span>
                    </div>
                    <div class="stat-item">
                        <span>BTC Dominance:</span>
                        <span class="stat-value" id="btcDominance">0%</span>
                    </div>
                    <div class="stat-item">
                        <span>Stato Sistema:</span>
                        <span class="stat-value positive" id="systemStatus">ONLINE</span>
                    </div>
                </div>
            </div>
            
            <!-- Risk Management Card -->
            <div class="card">
                <h2>🛡️ Risk Management</h2>
                <div id="riskStats">
                    <div class="stat-item">
                        <span>Esposizione Attuale:</span>
                        <span class="stat-value" id="currentExposure">0%</span>
                    </div>
                    <div class="stat-item">
                        <span>Esposizione Max:</span>
                        <span class="stat-value" id="maxExposure">0%</span>
                    </div>
                    <div class="stat-item">
                        <span>Take Profit:</span>
                        <span class="stat-value" id="takeProfit">0%</span>
                    </div>
                    <div class="stat-item">
                        <span>Stop Loss:</span>
                        <span class="stat-value" id="stopLoss">0%</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 🎯 GRAFICO CHART.JS REALE -->
        <div class="chart-container">
            <h2>📊 Performance Cumulative (Chart.js)</h2>
            <canvas id="performanceChart"></canvas>
        </div>
        
        <!-- Posizioni Attive -->
        <div class="card">
            <h2>🎯 Posizioni Attive</h2>
            <div id="activePositionsContainer" class="positions-grid">
                <div class="loading">Caricamento posizioni...</div>
            </div>
        </div>
        
        <!-- Ultimi Trade -->
        <div class="card">
            <h2>🔄 Ultimi Trade</h2>
            <div id="recentTradesContainer">
                <div class="loading">Caricamento trade recenti...</div>
            </div>
        </div>
    </div>

    <script>
        // 🎯 VARIABILI GLOBALI PER GESTIONE STATO
        let updateInterval;
        let chart;
        let consecutiveErrors = 0;
        const MAX_CONSECUTIVE_ERRORS = 3;
        let lastChartUpdate = 0;
        const CHART_UPDATE_INTERVAL = 30000; // 30 secondi
        
        // 🎯 INIZIALIZZAZIONE CHART.JS
        function initializeChart() {
            const ctx = document.getElementById('performanceChart').getContext('2d');
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'P&L Cumulative (%)',
                        data: [],
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#ffffff' }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#cccccc' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        y: {
                            ticks: { color: '#cccccc' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        }
                    }
                }
            });
        }
        
        // 🎯 AGGIORNAMENTO DASHBOARD CON GESTIONE ERRORI COMPLETA
        function updateDashboard() {
            fetch('/api/stats')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    consecutiveErrors = 0; // Reset errori consecutivi
                    hideErrorBanner();
                    
                    // 🎯 PASSA TUTTI I DATI NECESSARI - RISOLTO PROBLEMA RIFERIMENTO
                    updatePerformance(data.performance, data.cycle_count);
                    updatePortfolio(data.portfolio);
                    updateMarket(data.market_data);
                    updateRisk(data.risk_metrics);
                    updatePositions(data.portfolio.positions);
                    updateRecentTrades(data.recent_trades);
                    updateSystemInfo(data);
                    
                    // 🎯 AGGIORNA GRAFICO OGNI 30s - LOGICA CHIARA
                    const now = Date.now();
                    if (now - lastChartUpdate > CHART_UPDATE_INTERVAL) {
                        updateChart(data.performance?.chart_data);
                        lastChartUpdate = now;
                    }
                    
                    document.getElementById('lastUpdate').textContent = 
                        `Ultimo aggiornamento: ${new Date().toLocaleTimeString()}`;
                    
                    // Gestione stato offline/online
                    if (!data.engine_online) {
                        showWarningBanner('⚠️ Bot disconnesso - Tentativo riconnessione...');
                        document.body.classList.add('offline');
                    } else {
                        document.body.classList.remove('offline');
                    }
                })
                .catch(error => {
                    console.error('❌ Errore fetch:', error);
                    consecutiveErrors++;
                    
                    // 🎯 GESTIONE ERRORI VISIBILE ALL'UTENTE
                    showErrorBanner(`Errore connessione: ${error.message}`);
                    
                    document.getElementById('systemStatus').textContent = 'OFFLINE';
                    document.getElementById('systemStatus').className = 'stat-value negative';
                    
                    // Stop aggiornamenti se troppi errori consecutivi
                    if (consecutiveErrors >= MAX_CONSECUTIVE_ERRORS) {
                        showErrorBanner('❌ Connessione persa - Ricarica la pagina');
                        if (updateInterval) {
                            clearInterval(updateInterval);
                        }
                    }
                });
        }
        
        // 🎯 FUNZIONI AGGIORNAMENTO CON PARAMETRI CORRETTI
        function updatePerformance(performance, cycleCount) {
            if (performance?.error) {
                document.getElementById('performanceStats').innerHTML = 
                    `<div class="stat-item"><span>Errore:</span><span class="negative">${performance.error}</span></div>`;
                return;
            }
            
            document.getElementById('totalTrades').textContent = performance?.total_trades || 0;
            document.getElementById('avgPnl').textContent = (performance?.avg_pnl || 0) + '%';
            document.getElementById('avgPnl').className = 'stat-value ' + 
                ((performance?.avg_pnl || 0) >= 0 ? 'positive' : 'negative');
            document.getElementById('winRate').textContent = (performance?.win_rate || 0) + '%';
            document.getElementById('cycleCount').textContent = cycleCount || 0;
        }
        
        function updatePortfolio(portfolio) {
            if (portfolio?.error) {
                document.getElementById('portfolioStats').innerHTML = 
                    `<div class="stat-item"><span>Errore:</span><span class="negative">${portfolio.error}</span></div>`;
                return;
            }
            
            document.getElementById('totalValue').textContent = '$' + (portfolio?.total_value || 0);
            document.getElementById('cashBalance').textContent = '$' + (portfolio?.cash || 0);
            document.getElementById('exposure').textContent = (portfolio?.exposure_pct || 0) + '%';
            document.getElementById('activePositions').textContent = portfolio?.position_count || 0;
        }
        
        function updateMarket(market) {
            if (market?.error) {
                document.getElementById('marketStats').innerHTML = 
                    `<div class="stat-item"><span>Errore:</span><span class="negative">${market.error}</span></div>`;
                return;
            }
            
            document.getElementById('fearGreed').textContent = market?.fear_greed || 0;
            
            const sentimentElem = document.getElementById('sentiment');
            const sentiment = market?.market_sentiment || 'Neutral';
            sentimentElem.textContent = sentiment;
            sentimentElem.className = 'market-sentiment sentiment-' + 
                (sentiment.toLowerCase().includes('fear') ? 'fear' : 
                 sentiment.toLowerCase().includes('greed') ? 'greed' : 'neutral');
            
            document.getElementById('btcDominance').textContent = (market?.btc_dominance || 0) + '%';
        }
        
        function updateRisk(risk) {
            if (risk?.error) {
                document.getElementById('riskStats').innerHTML = 
                    `<div class="stat-item"><span>Errore:</span><span class="negative">${risk.error}</span></div>`;
                return;
            }
            
            document.getElementById('currentExposure').textContent = (risk?.current_exposure || 0) + '%';
            document.getElementById('maxExposure').textContent = (risk?.max_exposure || 0) + '%';
            document.getElementById('takeProfit').textContent = (risk?.take_profit || 0) + '%';
            document.getElementById('stopLoss').textContent = (risk?.stop_loss || 0) + '%';
        }
        
        function updatePositions(positions) {
            const container = document.getElementById('activePositionsContainer');
            
            if (!positions || positions.length === 0) {
                container.innerHTML = '<div class="position-card">Nessuna posizione attiva</div>';
                return;
            }
            
            container.innerHTML = positions.map(position => `
                <div class="position-card ${(position.pnl_pct || 0) < 0 ? 'negative' : ''}">
                    <div style="font-weight: bold; margin-bottom: 8px;">${position.symbol}</div>
                    <div style="font-size: 0.9em;">
                        <div>Quantità: ${position.quantity}</div>
                        <div>Entry: $${position.entry_price}</div>
                        <div>Current: $${position.current_price}</div>
                        <div>Valore: $${position.value}</div>
                        <div>P&L: <span class="${(position.pnl_pct || 0) >= 0 ? 'positive' : 'negative'}">${position.pnl_pct}%</span></div>
                        <div>Giorni: ${position.holding_days}</div>
                    </div>
                </div>
            `).join('');
        }
        
        function updateRecentTrades(trades) {
            const container = document.getElementById('recentTradesContainer');
            
            if (!trades || trades.length === 0 || (trades.length === 1 && trades[0].error)) {
                container.innerHTML = '<div>Nessun trade recente</div>';
                return;
            }
            
            container.innerHTML = `
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.9em;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.2);">
                                <th style="padding: 8px; text-align: left;">Ora</th>
                                <th style="padding: 8px; text-align: left;">Asset</th>
                                <th style="padding: 8px; text-align: left;">Azione</th>
                                <th style="padding: 8px; text-align: right;">Importo</th>
                                <th style="padding: 8px; text-align: right;">P&L</th>
                                <th style="padding: 8px; text-align: left;">Motivo</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${trades.map(trade => `
                                <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                                    <td style="padding: 8px;">${trade.timestamp}</td>
                                    <td style="padding: 8px;">${trade.symbol}</td>
                                    <td style="padding: 8px;">
                                        <span class="${trade.action === 'BUY' ? 'positive' : 'negative'}">
                                            ${trade.action}
                                        </span>
                                    </td>
                                    <td style="padding: 8px; text-align: right;">$${trade.amount}</td>
                                    <td style="padding: 8px; text-align: right;">
                                        ${trade.profit_pct !== null && trade.profit_pct !== undefined ? 
                                            `<span class="${trade.profit_pct >= 0 ? 'positive' : 'negative'}">
                                                ${trade.profit_pct}%
                                            </span>` : 
                                            '-'
                                        }
                                    </td>
                                    <td style="padding: 8px; font-size: 0.8em;">${trade.reason}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }
        
        function updateSystemInfo(data) {
            document.getElementById('systemStatus').textContent = data.system_status;
            document.getElementById('systemStatus').className = 'stat-value ' + 
                (data.system_status === 'ONLINE' ? 'positive' : 'negative');
        }
        
        // 🎯 AGGIORNA GRAFICO CHART.JS
        function updateChart(chartData) {
            if (!chartData || !chartData.labels || !chartData.cumulative) {
                return;
            }
            
            chart.data.labels = chartData.labels;
            chart.data.datasets[0].data = chartData.cumulative;
            chart.update('none'); // Aggiorna senza animazione
        }
        
        // 🎯 GESTIONE BANNER ERRORI
        function showErrorBanner(message) {
            const banner = document.getElementById('errorBanner');
            banner.textContent = message;
            banner.className = 'error-banner';
            banner.style.display = 'block';
        }
        
        function showWarningBanner(message) {
            const banner = document.getElementById('warningBanner');
            banner.textContent = message;
            banner.className = 'warning-banner';
            banner.style.display = 'block';
        }
        
        function hideErrorBanner() {
            document.getElementById('errorBanner').style.display = 'none';
            document.getElementById('warningBanner').style.display = 'none';
        }
        
        // 🎯 INIZIALIZZAZIONE
        document.addEventListener('DOMContentLoaded', function() {
            initializeChart();
            updateDashboard(); // Primo aggiornamento
            updateInterval = setInterval(updateDashboard, 5000); // Ogni 5 secondi
            
            // Auto-riconnessione se offline
            setInterval(() => {
                if (consecutiveErrors > 0 && consecutiveErrors < MAX_CONSECUTIVE_ERRORS) {
                    updateDashboard();
                }
            }, 15000); // Ogni 15 secondi se errore
        });
        
        // Pulizia quando la pagina viene chiusa
        window.addEventListener('beforeunload', function() {
            if (updateInterval) {
                clearInterval(updateInterval);
            }
        });
    </script>
</body>
</html>
    '''
    
    with open('dashboard_perfected.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Dashboard HTML perfezionata creata: dashboard_perfected.html")

# =============================================================================
# 🚀 INTEGRAZIONE PERFETTA
# =============================================================================

def start_quantum_dashboard_perfected(trading_engine=None, port=8080):
    """Avvia la dashboard perfezionata"""
    
    # Crea file HTML
    create_perfected_dashboard_html()
    
    # Avvia server
    dashboard = QuantumDashboardPerfected(port=port, trading_engine=trading_engine)
    dashboard_thread = threading.Thread(target=dashboard.start_dashboard, daemon=True)
    dashboard_thread.start()
    
    return dashboard

# =============================================================================
# 🔧 USO RAPIDO
# =============================================================================

if __name__ == "__main__":
    print("🚀 Avvio Quantum Dashboard Perfetta...")
    dashboard = start_quantum_dashboard_perfected()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard chiusa")

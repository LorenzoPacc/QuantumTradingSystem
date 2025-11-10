#!/usr/bin/env python3
"""
🤖 QUANTUM TRADER - DASHBOARD PROFESSIONALE
✅ Design moderno
✅ Dati in tempo reale  
✅ Nessun carattere corrotto
"""

import http.server
import socketserver
import time
from quantum_real_perfect import RealBinanceAPI

class ProfessionalDashboard(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Ottieni dati REALI
            api = RealBinanceAPI()
            
            # Dati portfolio
            entries = {
                'BTCUSDT': 101727.24, 'ETHUSDT': 3384.81, 
                'SOLUSDT': 157.43, 'AVAXUSDT': 17.29, 
                'LINKUSDT': 15.33, 'DOTUSDT': 3.172
            }
            
            quantities = {
                'BTCUSDT': 0.000442359, 'ETHUSDT': 0.013294690,
                'SOLUSDT': 0.273550149, 'AVAXUSDT': 1.515618999, 
                'LINKUSDT': 1.040167935, 'DOTUSDT': 3.152585120
            }
            
            # Calcola valori
            positions_data = []
            total_value = 14.78  # Cash iniziale
            
            for symbol in entries.keys():
                current_price = api.get_real_price(symbol)
                if current_price:
                    entry = entries[symbol]
                    quantity = quantities[symbol]
                    pnl_pct = ((current_price - entry) / entry) * 100
                    position_value = quantity * current_price
                    total_value += position_value
                    
                    positions_data.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'position_value': position_value,
                        'pnl_pct': pnl_pct,
                        'quantity': quantity
                    })
            
            # Calcola performance
            profit = total_value - 200
            profit_pct = (profit / 200) * 100
            
            # Genera HTML professionale
            html = self.generate_html(positions_data, total_value, profit_pct)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
    
    def generate_html(self, positions, total_value, profit_pct):
        # Header con CSS moderno
        html = '''<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Quantum Trader Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
            color: #ffffff;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        
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
        
        .portfolio-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .portfolio-value {
            font-size: 2.2em;
            font-weight: bold;
            text-align: center;
            margin-bottom: 15px;
        }
        
        .profit-positive { color: #00ff88; }
        .profit-negative { color: #ff4444; }
        
        .positions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .position-card {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid #00ff88;
            transition: transform 0.2s;
        }
        
        .position-card:hover {
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.05);
        }
        
        .position-card.near-tp {
            border-left-color: #ffaa00;
            background: rgba(255, 170, 0, 0.1);
        }
        
        .position-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .symbol { 
            font-size: 1.3em; 
            font-weight: bold;
            color: #00ccff;
        }
        
        .pnl { 
            font-size: 1.2em; 
            font-weight: bold;
        }
        
        .position-details {
            font-size: 0.9em;
            color: #cccccc;
        }
        
        .detail-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
        }
        
        .refresh-info {
            text-align: center;
            margin-top: 20px;
            color: #888;
            font-size: 0.9em;
        }
        
        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .status-profit { background: #00ff88; color: #000; }
        .status-near-tp { background: #ffaa00; color: #000; }
        .status-hold { background: #00ccff; color: #000; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 QUANTUM TRADER</h1>
            <p>Dashboard Professionale - Dati in Tempo Reale</p>
        </div>
        
        <div class="portfolio-card">
            <div class="portfolio-value ''' + ('profit-positive' if profit_pct >= 0 else 'profit-negative') + '''">
                💎 $''' + f"{total_value:.2f}" + ''' (''' + f"{profit_pct:+.2f}" + '''%)
            </div>
            <div style="text-align: center; color: #cccccc;">
                💰 Cash: $14.78 | 📊 6 Posizioni Attive
            </div>
        </div>
        
        <div class="portfolio-card">
            <h2 style="margin-bottom: 20px; color: #00ccff;">📈 Posizioni Attive</h2>
            <div class="positions-grid">
'''
        
        # Aggiungi ogni posizione
        for pos in positions:
            status_class = ""
            status_badge = ""
            
            if pos['pnl_pct'] >= 7:
                status_class = "near-tp"
                status_badge = '<span class="status-badge status-near-tp">🎯 VICINO TP!</span>'
            elif pos['pnl_pct'] >= 0:
                status_badge = '<span class="status-badge status-profit">✅ PROFIT</span>'
            else:
                status_badge = '<span class="status-badge status-hold">📊 HOLD</span>'
            
            html += f'''
                <div class="position-card {status_class}">
                    <div class="position-header">
                        <div class="symbol">{pos['symbol']}</div>
                        <div class="pnl {'profit-positive' if pos['pnl_pct'] >= 0 else 'profit-negative'}">
                            {pos['pnl_pct']:+.2f}%
                        </div>
                    </div>
                    {status_badge}
                    <div class="position-details">
                        <div class="detail-row">
                            <span>Prezzo:</span>
                            <span>${pos['current_price']:,.2f}</span>
                        </div>
                        <div class="detail-row">
                            <span>Valore:</span>
                            <span>${pos['position_value']:.2f}</span>
                        </div>
                        <div class="detail-row">
                            <span>Quantità:</span>
                            <span>{pos['quantity']:.6f}</span>
                        </div>
                    </div>
                </div>
'''
        
        # Footer
        html += f'''
            </div>
        </div>
        
        <div class="refresh-info">
            🔄 Ultimo aggiornamento: {time.strftime('%H:%M:%S')} - Prossimo aggiornamento automatico in 30 secondi
            <br>🎯 Take Profit: +8% | 🛡️ Stop Loss: -4%
        </div>
    </div>
    
    <script>
        // Auto-refresh ogni 30 secondi
        setTimeout(function() {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>'''
        
        return html

# Avvia il server
PORT = 8084
print(f"🎨 DASHBOARD PROFESSIONALE: http://localhost:{PORT}")
print("✅ Design moderno - Nessun carattere corrotto")
print("🔄 Aggiornamento automatico ogni 30 secondi")

with socketserver.TCPServer(("", PORT), ProfessionalDashboard) as httpd:
    httpd.serve_forever()

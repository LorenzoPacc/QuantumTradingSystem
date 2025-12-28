#!/usr/bin/env python3
"""
🚀 QUANTUM TRADER - DASHBOARD PRO COMPLETA
✅ Tutti i colori originali 
✅ Stati avanzati (VENDUTO, VICINO TP, ecc.)
✅ Design moderno ma funzionale
"""

import http.server
import socketserver
import time
from quantum_real_perfect import RealBinanceAPI

class QuantumProDashboard(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            try:
                # Ottieni dati REALI
                api = RealBinanceAPI()
                
                # Dati portfolio ORIGINALI
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
                
                # Calcola valori con logica ORIGINALE
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
                        
                        # LOGICA COLORI ORIGINALE - IMPORTANTE!
                        if pnl_pct >= 8:
                            status = '🎯 VENDUTO +8%'
                            status_class = 'sold'
                            badge = '🟢 VENDUTO'
                        elif pnl_pct >= 6:
                            status = f'🟢 +{pnl_pct:.1f}% (Vicino TP!)'
                            status_class = 'near-tp'
                            badge = '🎯 VICINO TP'
                        elif pnl_pct >= 0:
                            status = f'✅ +{pnl_pct:.1f}%'
                            status_class = 'profit'
                            badge = '✅ PROFIT'
                        else:
                            status = f'🔴 {pnl_pct:.1f}%'
                            status_class = 'loss'
                            badge = '📊 IN LOSS'
                        
                        positions_data.append({
                            'symbol': symbol,
                            'current_price': current_price,
                            'position_value': position_value,
                            'pnl_pct': pnl_pct,
                            'quantity': quantity,
                            'status': status,
                            'status_class': status_class,
                            'badge': badge
                        })
                
                # Calcola performance
                profit = total_value - 200
                profit_pct = (profit / 200) * 100
                
                # Genera HTML con tutti i colori originali
                html = self.generate_pro_html(positions_data, total_value, profit_pct)
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
                
            except Exception as e:
                print(f"❌ Errore dashboard: {e}")
                self.send_error(500, f"Errore interno: {e}")
    
    def generate_pro_html(self, positions, total_value, profit_pct):
        html = '''<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Quantum Trader PRO Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Courier New', monospace;
            background: #0a0a0a;
            color: #ffffff;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        
        .header { 
            text-align: center; 
            margin-bottom: 30px;
            padding: 20px;
            background: #111111;
            border-radius: 10px;
            border: 1px solid #333;
        }
        .header h1 { 
            font-size: 2.2em; 
            color: #00ff00;
            margin-bottom: 10px;
            text-shadow: 0 0 10px #00ff00;
        }
        
        .portfolio-summary {
            background: #111111;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #333;
            text-align: center;
        }
        
        .total-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .profit-positive { color: #00ff00; }
        .profit-negative { color: #ff0000; }
        
        .positions-container {
            background: #111111;
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #333;
        }
        
        .position-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            background: #1a1a1a;
            border-left: 5px solid #333;
            transition: all 0.3s;
        }
        
        .position-row:hover {
            background: #222222;
            transform: translateX(5px);
        }
        
        /* COLORI ORIGINALI */
        .position-row.sold {
            border-left-color: #00ff00;
            background: rgba(0, 255, 0, 0.1);
        }
        
        .position-row.near-tp {
            border-left-color: #ffff00;
            background: rgba(255, 255, 0, 0.1);
        }
        
        .position-row.profit {
            border-left-color: #00ff00;
        }
        
        .position-row.loss {
            border-left-color: #ff0000;
            background: rgba(255, 0, 0, 0.1);
        }
        
        .symbol-section {
            flex: 1;
        }
        
        .symbol {
            font-size: 1.3em;
            font-weight: bold;
            color: #00ccff;
        }
        
        .status {
            font-size: 1.1em;
            margin-top: 5px;
        }
        
        .values-section {
            flex: 1;
            text-align: right;
        }
        
        .pnl {
            font-size: 1.3em;
            font-weight: bold;
        }
        
        .position-value {
            color: #cccccc;
            margin-top: 5px;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            margin-top: 5px;
        }
        
        .badge-sold { background: #00ff00; color: #000; }
        .badge-near-tp { background: #ffff00; color: #000; }
        .badge-profit { background: #00aa00; color: #fff; }
        .badge-loss { background: #ff0000; color: #fff; }
        
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 0.9em;
        }
        
        .cash-info {
            background: #111111;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: center;
            border: 1px solid #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 QUANTUM TRADER PRO</h1>
            <p>Dashboard Live - Prezzi Real-Time Binance</p>
        </div>
        
        <div class="portfolio-summary">
            <div class="total-value ''' + ('profit-positive' if profit_pct >= 0 else 'profit-negative') + '''">
                💎 Portfolio Totale: $''' + f"{total_value:.2f}" + ''' (''' + f"{profit_pct:+.2f}" + '''%)
            </div>
        </div>
        
        <div class="cash-info">
            💰 Cash Disponibile: <strong>$14.78</strong> | 📊 Posizioni Attive: <strong>6</strong>
        </div>
        
        <div class="positions-container">
            <h2 style="margin-bottom: 20px; color: #00ccff; text-align: center;">
                📈 STATO POSIZIONI LIVE
            </h2>
'''
        
        # Aggiungi ogni posizione con colori ORIGINALI
        for pos in positions:
            badge_class = f"badge-{pos['status_class']}"
            
            html += f'''
            <div class="position-row {pos['status_class']}">
                <div class="symbol-section">
                    <div class="symbol">{pos['symbol']}</div>
                    <div class="status">{pos['status']}</div>
                    <span class="badge {badge_class}">{pos['badge']}</span>
                </div>
                <div class="values-section">
                    <div class="pnl {'profit-positive' if pos['pnl_pct'] >= 0 else 'profit-negative'}">
                        {pos['pnl_pct']:+.2f}%
                    </div>
                    <div class="position-value">
                        Valore: ${pos['position_value']:.2f}
                    </div>
                    <div style="font-size: 0.9em; color: #888;">
                        Qty: {pos['quantity']:.6f}
                    </div>
                </div>
            </div>
'''
        
        # Footer
        html += f'''
        </div>
        
        <div class="footer">
            🔄 Ultimo aggiornamento: {time.strftime('%H:%M:%S')} - Auto-refresh ogni 30s<br>
            🎯 Take Profit: +8% | 🛡️ Stop Loss: -4%<br>
            <span style="color: #00ff00;">🟢 VENDUTO</span> | 
            <span style="color: #ffff00;">🎯 VICINO TP</span> | 
            <span style="color: #00ff00;">✅ PROFIT</span> | 
            <span style="color: #ff0000;">📊 IN LOSS</span>
        </div>
    </div>
    
    <script>
        setTimeout(function() {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>'''
        
        return html

# Avvia il server
PORT = 8085
print(f"🚀 QUANTUM TRADER PRO DASHBOARD: http://localhost:{PORT}")
print("✅ Tutti i colori originali ripristinati")
print("🎯 Stati avanzati: VENDUTO, VICINO TP, PROFIT, IN LOSS")
print("🔄 Aggiornamento automatico ogni 30 secondi")

try:
    with socketserver.TCPServer(("", PORT), QuantumProDashboard) as httpd:
        print(f"📊 Server attivo sulla porta {PORT}...")
        httpd.serve_forever()
except Exception as e:
    print(f"❌ Errore avvio server: {e}")

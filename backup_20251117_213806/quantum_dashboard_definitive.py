#!/usr/bin/env python3
"""
DASHBOARD QUANTUM DEFINITIVA
Monitoraggio sistema in tempo reale
"""
from flask import Flask, render_template_string
import sqlite3
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def get_system_data():
    """Recupera dati sistema aggiornati"""
    try:
        conn = sqlite3.connect('quantum_definitive.db')
        cursor = conn.cursor()
        
        # Balance attuale
        cursor.execute("""
            SELECT total_balance, available_balance, portfolio_value, timestamp 
            FROM balance_history 
            ORDER BY timestamp DESC LIMIT 1
        """)
        balance_data = cursor.fetchone()
        
        # Ultimi trade
        cursor.execute("""
            SELECT symbol, side, quantity, entry_price, confluence_score, confidence, timestamp 
            FROM trades 
            ORDER BY timestamp DESC LIMIT 10
        """)
        trades = cursor.fetchall()
        
        # Performance
        cursor.execute("""
            SELECT total_value, pnl, pnl_percent, trade_count, timestamp
            FROM performance 
            ORDER BY timestamp DESC LIMIT 1
        """)
        performance = cursor.fetchone()
        
        # Ultime analisi confluence
        cursor.execute("""
            SELECT symbol, confluence_score, confidence, signal, timestamp
            FROM confluence_logs 
            ORDER BY timestamp DESC LIMIT 15
        """)
        confluence_logs = cursor.fetchall()
        
        conn.close()
        
        return balance_data, trades, performance, confluence_logs
    except Exception as e:
        print(f"Errore database: {e}")
        return None, [], None, []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Quantum Trading Dashboard - DEFINITIVA</title>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="30">
    <style>
        body { font-family: 'Arial', sans-serif; margin: 20px; background: #0f0f23; color: #00ff00; }
        .container { max-width: 1400px; margin: 0 auto; }
        .card { background: #1a1a2e; padding: 20px; margin: 15px 0; border-radius: 10px; border: 1px solid #00ff00; }
        .header { text-align: center; background: linear-gradient(45deg, #00ff00, #008800); color: black; padding: 15px; border-radius: 10px; }
        .balance { font-size: 28px; font-weight: bold; color: #00ff00; text-align: center; }
        .positive { color: #00ff00; }
        .negative { color: #ff4444; }
        .neutral { color: #ffff00; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
        th { background: #2a2a4e; color: #00ff00; }
        .trade-buy { color: #00ff00; background: #1a331a; }
        .trade-sell { color: #ff4444; background: #331a1a; }
        .signal-buy { color: #00ff00; font-weight: bold; }
        .signal-sell { color: #ff4444; font-weight: bold; }
        .signal-hold { color: #ffff00; }
        .confluence-good { color: #00ff00; }
        .confluence-medium { color: #ffff00; }
        .confluence-poor { color: #ff4444; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 QUANTUM TRADING DASHBOARD - DEFINITIVA</h1>
            <p>Strategia Multi-Fattore • Dati Reali Binance • Balance Virtuale</p>
            <p>Ultimo aggiornamento: {{ current_time }}</p>
        </div>
        
        {% if balance_data %}
        <div class="card">
            <h2>💰 BALANCE & PERFORMANCE</h2>
            <div class="balance">
                ${{ "%.2f"|format(balance_data[0]) }} USDT
            </div>
            <div style="text-align: center;">
                Disponibile: ${{ "%.2f"|format(balance_data[1]) }} | 
                Portfolio: ${{ "%.2f"|format(balance_data[2]) }} |
                Aggiornato: {{ balance_data[3][:19] }}
            </div>
            
            {% if performance %}
            <div style="text-align: center; margin-top: 10px;">
                <strong>📈 PERFORMANCE:</strong>
                Valore Totale: ${{ "%.2f"|format(performance[0]) }} | 
                P&L: ${{ "%.2f"|format(performance[1]) }} | 
                P&L%: {{ "%.2f"|format(performance[2]) }}% |
                Trade: {{ performance[3] }}
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        <div class="card">
            <h2>📊 ULTIMI TRADE</h2>
            <table>
                <tr>
                    <th>Symbol</th>
                    <th>Side</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Confluence</th>
                    <th>Confidence</th>
                    <th>Time</th>
                </tr>
                {% for trade in trades %}
                <tr class="trade-{{ trade[1].lower() }}">
                    <td><strong>{{ trade[0] }}</strong></td>
                    <td class="signal-{{ trade[1].lower() }}">{{ trade[1] }}</td>
                    <td>{{ "%.4f"|format(trade[2]) }}</td>
                    <td>${{ "%.2f"|format(trade[3]) }}</td>
                    <td class="confluence-{% if trade[4] >= 3.0 %}good{% elif trade[4] >= 2.5 %}medium{% else %}poor{% endif %}">
                        {{ "%.2f"|format(trade[4]) }}/4.0
                    </td>
                    <td>{{ "%.1f"|format(trade[5]*100) }}%</td>
                    <td>{{ trade[6][:19] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        
        <div class="card">
            <h2>🎯 ULTIME ANALISI CONFLUENCE</h2>
            <table>
                <tr>
                    <th>Symbol</th>
                    <th>Confluence</th>
                    <th>Confidence</th>
                    <th>Signal</th>
                    <th>Time</th>
                </tr>
                {% for analysis in confluence_logs %}
                <tr>
                    <td><strong>{{ analysis[0] }}</strong></td>
                    <td class="confluence-{% if analysis[1] >= 3.0 %}good{% elif analysis[1] >= 2.5 %}medium{% else %}poor{% endif %}">
                        {{ "%.2f"|format(analysis[1]) }}/4.0
                    </td>
                    <td>{{ "%.1f"|format(analysis[2]*100) }}%</td>
                    <td class="signal-{{ analysis[3].lower() }}">{{ analysis[3] }}</td>
                    <td>{{ analysis[4][:19] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        
        <div class="card">
            <h2>⚙️ INFORMAZIONI SISTEMA</h2>
            <p><strong>🎯 Strategia:</strong> Multi-Fattore Confluence (Macro 30%, Price Action 30%, On-Chain 25%, Cycles 15%)</p>
            <p><strong>📈 Parametri:</strong> Min Confluence 2.6/4.0 • Min Confidence 70% • Risk/Trade 7%</p>
            <p><strong>💰 Balance Virtuale:</strong> $10,000 iniziali • Trading simulato con prezzi reali</p>
            <p><strong>🔄 Ciclo:</strong> Analisi ogni 5 minuti • Max 20 cicli</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    balance_data, trades, performance, confluence_logs = get_system_data()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template_string(HTML_TEMPLATE, 
                                balance_data=balance_data,
                                trades=trades,
                                performance=performance,
                                confluence_logs=confluence_logs,
                                current_time=current_time)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)

#!/usr/bin/env python3
"""
QUANTUM TRADER v3.3 ULTIMATE EDITION
Combina: Prezzi Live + Alert System + Export + Grafici Avanzati
"""
import streamlit as st
import json
import os
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import ccxt

# ==================== CONFIGURAZIONE ====================
st.set_page_config(
    page_title="Quantum Trader v3.3 ULTIMATE",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

STATE_FILE = "qv33_ultimate_final_state.json"

# ==================== STILE ====================
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    .stMetric {font-size: 1.2em;}
    div[data-testid="stMetricValue"] {font-size: 2em; font-weight: bold;}
    
    /* Dataframe copiabile */
    .stDataFrame {
        user-select: text !important;
        -webkit-user-select: text !important;
    }
    
    /* Colori PnL */
    .pnl-positive {color: #00ff88; font-weight: bold;}
    .pnl-negative {color: #ff4444; font-weight: bold;}
    .pnl-neutral {color: #ffaa00; font-weight: bold;}
    
    /* Live price indicator */
    .live-price {
        background: linear-gradient(90deg, #00ff88 0%, #00d4ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNZIONI ====================

@st.cache_data(ttl=10, show_spinner=False)
def load_state():
    """Carica stato bot"""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
        required = ["capital", "positions", "trade_history"]
        if not all(k in data for k in required):
            return None
        return data
    except Exception as e:
        st.error(f"❌ Errore lettura state: {e}")
        return None

@st.cache_data(ttl=5, show_spinner=False)
def get_current_price(symbol):
    """Fetch prezzo LIVE da Binance"""
    try:
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker(symbol)
        return float(ticker["last"])
    except Exception as e:
        return None

@st.cache_data(ttl=10, show_spinner=False)
def get_multiple_prices(symbols):
    """Fetch prezzi multipli in batch"""
    prices = {}
    try:
        exchange = ccxt.binance()
        for symbol in symbols:
            ticker = exchange.fetch_ticker(symbol)
            prices[symbol] = float(ticker["last"])
    except:
        pass
    return prices

def format_pnl(pnl):
    """Formatta P&L con colore"""
    pnl = float(pnl)
    if pnl > 0:
        return f"<span class='pnl-positive'>+${pnl:.2f}</span>"
    elif pnl < 0:
        return f"<span class='pnl-negative'>${pnl:.2f}</span>"
    return f"<span class='pnl-neutral'>${pnl:.2f}</span>"

def calculate_position_pnl(position, current_price=None):
    """Calcola P&L posizione con prezzo live"""
    try:
        entry_price = float(position.get("entry_price", 0))
        amount = float(position.get("amount", 0))
        
        if current_price is None:
            current_price = entry_price
        else:
            current_price = float(current_price)
        
        current_value = current_price * amount
        entry_value = entry_price * amount
        return current_value - entry_value
    except:
        return 0.0

def check_alerts(state, current_prices):
    """Sistema alert avanzato"""
    alerts = []
    
    capital = float(state.get("capital", 0))
    total_pnl = float(state.get("total_pnl", 0))
    positions = state.get("positions", {})
    
    # Calcola P&L totale incluse posizioni aperte
    unrealized_pnl = 0
    for symbol, pos in positions.items():
        price = current_prices.get(symbol)
        if price:
            unrealized_pnl += calculate_position_pnl(pos, price)
    
    total_pnl_with_unrealized = total_pnl + unrealized_pnl
    
    # Alert drawdown
    if total_pnl_with_unrealized < -30:
        alerts.append(("🚨 High Drawdown", f"Total P&L: ${total_pnl_with_unrealized:.2f}"))
    
    # Alert capitale basso
    if capital < 100:
        alerts.append(("💰 Low Capital", f"${capital:.2f} remaining"))
    
    # Alert concentrazione
    for symbol, pos in positions.items():
        try:
            price = current_prices.get(symbol, pos.get("entry_price", 0))
            value = float(price) * float(pos.get("amount", 0))
            
            if capital > 0 and value > capital * 0.4:
                pct = (value / capital) * 100
                alerts.append(("⚠️ Concentration", f"{symbol}: {pct:.0f}% of capital"))
        except:
            continue
    
    # Alert profit target (se unrealized > 10%)
    if unrealized_pnl > 20:
        alerts.append(("🎯 Profit Target", f"Unrealized: +${unrealized_pnl:.2f}"))
    
    return alerts

def create_pnl_chart(trade_history):
    """Grafico P&L cumulativo"""
    if not trade_history or len(trade_history) < 2:
        return None
    
    try:
        df = pd.DataFrame(trade_history)
        if "pnl" not in df.columns:
            return None
        
        df["pnl"] = pd.to_numeric(df["pnl"], errors='coerce').fillna(0)
        df["cumulative"] = df["pnl"].cumsum()
        
        fig = go.Figure()
        
        # Linea principale
        colors = ['#ff4444' if x < 0 else '#00ff88' for x in df["cumulative"]]
        
        fig.add_trace(go.Scatter(
            y=df["cumulative"],
            mode='lines+markers',
            name='Cumulative P&L',
            line=dict(color='#00d4ff', width=2),
            marker=dict(color=colors, size=8),
            fill='tozeroy',
            fillcolor='rgba(0, 212, 255, 0.1)',
            hovertemplate='Trade %{x}<br>P&L: $%{y:.2f}<extra></extra>'
        ))
        
        fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3)
        
        fig.update_layout(
            title="📈 Cumulative P&L",
            xaxis_title="Trade #",
            yaxis_title="P&L ($)",
            height=300,
            template="plotly_dark",
            showlegend=False
        )
        return fig
    except Exception as e:
        return None

def create_win_loss_chart(state):
    """Grafico Win/Loss"""
    try:
        wins = int(state.get("winning_trades", 0))
        losses = int(state.get("losing_trades", 0))
        
        if wins + losses == 0:
            return None
        
        win_rate = (wins / (wins + losses)) * 100
        
        fig = go.Figure(data=[go.Pie(
            labels=['Wins', 'Losses'],
            values=[wins, losses],
            hole=.5,
            marker_colors=['#00ff88', '#ff4444'],
            textinfo='label+percent',
            hovertemplate='%{label}: %{value} trades<br>%{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title=f"🎯 Win Rate: {win_rate:.1f}% ({wins}W / {losses}L)",
            height=300,
            template="plotly_dark",
            annotations=[dict(text=f'{win_rate:.1f}%', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        return fig
    except:
        return None

# ==================== HEADER ====================
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.title("🚀 QUANTUM TRADER v3.3 ULTIMATE")
with col2:
    st.metric("🕐 Time", datetime.now().strftime('%H:%M:%S'))
with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bot.png", width=80)
    st.header("⚙️ Control Panel")
    
    auto_refresh = st.checkbox("Auto Refresh", value=True)
    if auto_refresh:
        refresh_interval = st.slider("Interval (sec)", 5, 120, 20)
    
    st.markdown("---")
    st.subheader("🤖 Bot Status")
    
    if os.path.exists(STATE_FILE):
        st.success("🟢 RUNNING")
        last_mod = datetime.fromtimestamp(os.path.getmtime(STATE_FILE))
        st.caption(f"Updated: {last_mod.strftime('%H:%M:%S')}")
        
        age = (datetime.now() - last_mod).total_seconds()
        if age > 300:
            st.warning(f"⚠️ Stale ({age/60:.0f}m)")
    else:
        st.error("🔴 OFFLINE")
        st.stop()
    
    st.markdown("---")
    st.subheader("📊 Settings")
    show_charts = st.checkbox("Show Charts", value=True)
    show_history = st.checkbox("Show History", value=True)
    show_live_prices = st.checkbox("Live Prices", value=True)
    trade_limit = st.slider("Recent Trades", 5, 50, 20)
    
    st.markdown("---")
    st.caption("💡 Live prices from Binance")

# ==================== CARICA STATO ====================
state = load_state()
if not state:
    st.error("❌ State file non disponibile")
    st.stop()

# ==================== FETCH PREZZI LIVE ====================
positions = state.get("positions", {})
current_prices = {}

if show_live_prices and positions:
    with st.spinner("🔄 Fetching live prices..."):
        symbols = list(positions.keys())
        current_prices = get_multiple_prices(symbols)

# ==================== ALERT ====================
alerts = check_alerts(state, current_prices)
if alerts:
    for alert_type, alert_msg in alerts:
        st.warning(f"{alert_type}: {alert_msg}")
    st.markdown("---")

# ==================== ESTRAI DATI ====================
capital = float(state.get("capital", 0))
total_invested = float(state.get("total_invested", 0))
total_trades = int(state.get("total_trades", 0))
winning_trades = int(state.get("winning_trades", 0))
losing_trades = int(state.get("losing_trades", 0))
cycle_count = int(state.get("cycle_count", 0))
total_pnl = float(state.get("total_pnl", 0))
total_fees = float(state.get("total_fees_paid", 0))
trade_history = state.get("trade_history", [])
max_portfolio = float(state.get("max_portfolio_value", 0))

# ==================== CALCOLA PORTFOLIO CON PREZZI LIVE ====================
portfolio_value = capital
unrealized_pnl = 0.0
position_details = []

for symbol, pos in positions.items():
    try:
        entry_price = float(pos.get("entry_price", 0))
        amount = float(pos.get("amount", 0))
        
        # Usa prezzo live se disponibile
        current_price = current_prices.get(symbol, entry_price)
        
        current_value = amount * current_price
        entry_value = amount * entry_price
        pnl = current_value - entry_value
        
        portfolio_value += current_value
        unrealized_pnl += pnl
        
        position_details.append({
            "symbol": symbol,
            "amount": amount,
            "entry": entry_price,
            "current": current_price,
            "value": current_value,
            "pnl": pnl,
            "is_live": symbol in current_prices
        })
    except:
        continue

# P&L totale (realized + unrealized)
total_pnl_with_unrealized = total_pnl + unrealized_pnl

win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

# ==================== METRICHE PRINCIPALI ====================
st.subheader("💎 Portfolio Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    portfolio_change = ((portfolio_value / total_invested - 1) * 100) if total_invested > 0 else 0
    st.metric(
        "Portfolio Value" + (" 🔴" if show_live_prices and current_prices else ""),
        f"${portfolio_value:,.2f}",
        delta=f"{portfolio_change:+.2f}%"
    )

with col2:
    st.metric("Cash", f"${capital:,.2f}")

with col3:
    st.metric("Positions", len(positions))

with col4:
    st.metric(
        "Total P&L",
        f"${total_pnl_with_unrealized:+,.2f}",
        delta=f"Unrealized: ${unrealized_pnl:+.2f}"
    )

with col5:
    st.metric("Win Rate", f"{win_rate:.1f}%", delta=f"{winning_trades}W/{losing_trades}L")

# ==================== STATS SECONDARIE ====================
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🔄 Cycles", f"{cycle_count:,}")

with col2:
    fees_pct = (total_fees / total_invested * 100) if total_invested > 0 else 0
    st.metric("💸 Fees", f"${total_fees:.4f}", delta=f"{fees_pct:.3f}%")

with col3:
    st.metric("📊 Max Portfolio", f"${max_portfolio:.2f}")

with col4:
    roi = ((portfolio_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
    st.metric("📈 ROI", f"{roi:+.2f}%")

# ==================== GRAFICI ====================
if show_charts and len(trade_history) >= 2:
    st.markdown("---")
    st.subheader("📊 Performance Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        pnl_chart = create_pnl_chart(trade_history)
        if pnl_chart:
            st.plotly_chart(pnl_chart, use_container_width=True)
    
    with col2:
        wl_chart = create_win_loss_chart(state)
        if wl_chart:
            st.plotly_chart(wl_chart, use_container_width=True)

# ==================== POSIZIONI ATTIVE ====================
st.markdown("---")
st.subheader("🎯 Active Positions" + (" 🔴 LIVE PRICES" if current_prices else ""))

if position_details:
    for pos_detail in position_details:
        symbol = pos_detail["symbol"]
        amount = pos_detail["amount"]
        entry = pos_detail["entry"]
        current = pos_detail["current"]
        value = pos_detail["value"]
        pnl = pos_detail["pnl"]
        is_live = pos_detail["is_live"]
        
        pnl_pct = (pnl / (entry * amount) * 100) if entry * amount > 0 else 0
        
        status = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "🟡"
        live_indicator = " 🔴 LIVE" if is_live else ""
        
        with st.expander(f"{status} **{symbol}**{live_indicator} — Value: ${value:.2f} | P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)"):
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                st.write(f"**Entry:** ${entry:.8f}")
                st.write(f"**Amount:** {amount:.8f}")
            
            with c2:
                if is_live:
                    st.markdown(f"**Current:** <span class='live-price'>${current:.2f}</span>", unsafe_allow_html=True)
                else:
                    st.write(f"**Current:** ${current:.2f}")
                st.write(f"**Value:** ${value:.2f}")
            
            with c3:
                st.markdown(f"**P&L:** {format_pnl(pnl)}", unsafe_allow_html=True)
                st.write(f"**P&L %:** {pnl_pct:+.2f}%")
            
            with c4:
                pos = positions[symbol]
                st.write(f"**Fear:** {pos.get('entry_fear', 'N/A')}")
                
                if is_live:
                    price_change = ((current / entry - 1) * 100)
                    st.write(f"**Change:** {price_change:+.2f}%")
else:
    st.info("📭 No active positions")

# ==================== TRADE HISTORY ====================
if show_history and trade_history:
    st.markdown("---")
    st.subheader(f"📈 Trade History (Last {min(trade_limit, len(trade_history))})")
    
    try:
        recent = trade_history[-trade_limit:]
        df = pd.DataFrame(recent)
        
        if not df.empty:
            cols = []
            for c in ["symbol", "action", "price", "amount", "pnl", "fee", "timestamp"]:
                if c in df.columns:
                    cols.append(c)
            
            if cols:
                display = df[cols].iloc[::-1].reset_index(drop=True)
                
                # Formatta
                if "price" in display.columns:
                    display["price"] = display["price"].apply(lambda x: f"${float(x):.6f}" if pd.notna(x) and x != 0 else "N/A")
                if "pnl" in display.columns:
                    display["pnl"] = display["pnl"].apply(lambda x: f"${float(x):+.2f}" if pd.notna(x) else "$0.00")
                if "fee" in display.columns:
                    display["fee"] = display["fee"].apply(lambda x: f"${float(x):.4f}" if pd.notna(x) else "$0.00")
                if "amount" in display.columns:
                    display["amount"] = display["amount"].apply(lambda x: f"{float(x):.8f}" if pd.notna(x) else "0")
                
                st.dataframe(display, use_container_width=True, height=400)
                
                # Export
                csv = df[cols].to_csv(index=False)
                st.download_button(
                    "📥 Export Full History CSV",
                    csv,
                    f"quantum_trades_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv",
                    use_container_width=True
                )
    except Exception as e:
        st.error(f"Error: {e}")

# ==================== FOOTER ====================
st.markdown("---")
c1, c2, c3 = st.columns(3)

with c1:
    st.caption(f"🤖 Quantum v3.3 ULTIMATE | Invested: ${total_invested:.2f}")
with c2:
    st.caption(f"📊 {total_trades} trades | 🔴 Live Prices: {'ON' if current_prices else 'OFF'}")
with c3:
    file_size = os.path.getsize(STATE_FILE) / 1024
    st.caption(f"⚡ State: {file_size:.1f}KB | Mode: LIVE")

# ==================== AUTO-REFRESH ====================
if auto_refresh:
    import time
    time.sleep(refresh_interval)
    st.rerun()

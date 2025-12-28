import streamlit as st
import json
import os
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

# ==================== CONFIGURAZIONE ====================
st.set_page_config(
    page_title="Quantum Trader Pro",
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
    
    /* FIX: Dataframe copiabile */
    .stDataFrame {
        user-select: text !important;
        -webkit-user-select: text !important;
    }
    
    /* Colori PnL */
    .pnl-positive {color: #00ff88; font-weight: bold;}
    .pnl-negative {color: #ff4444; font-weight: bold;}
    
    /* Alert styling */
    .stAlert {border-left: 4px solid #764ba2;}
</style>
""", unsafe_allow_html=True)

# ==================== FUNZIONI ====================

@st.cache_data(ttl=10, show_spinner=False)
def load_state():
    """Carica stato con cache"""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
        
        # Validazione
        required = ["capital", "positions", "trade_history"]
        if not all(k in data for k in required):
            st.error(f"❌ Chiavi mancanti nel state file")
            return None
        
        return data
    except Exception as e:
        st.error(f"❌ Errore lettura: {e}")
        return None

def format_pnl(pnl):
    """Formatta PnL con colore"""
    pnl = float(pnl)
    if pnl > 0:
        return f"<span class='pnl-positive'>+${pnl:.2f}</span>"
    elif pnl < 0:
        return f"<span class='pnl-negative'>${pnl:.2f}</span>"
    return f"${pnl:.2f}"

def calculate_position_pnl(position, current_price=None):
    """Calcola P&L posizione"""
    try:
        entry_price = float(position.get("entry_price", 0))
        amount = float(position.get("amount", 0))
        price = float(current_price) if current_price else entry_price
        return (price * amount) - (entry_price * amount)
    except:
        return 0.0

def check_alerts(state):
    """Sistema alert"""
    alerts = []
    capital = float(state.get("capital", 0))
    total_pnl = float(state.get("total_pnl", 0))
    positions = state.get("positions", {})
    
    # Alert drawdown
    if total_pnl < -20:
        alerts.append(("🚨 Drawdown Alert", f"P&L: ${total_pnl:.2f}"))
    
    # Alert capitale basso
    if capital < 100:
        alerts.append(("💰 Low Capital", f"${capital:.2f} remaining"))
    
    # Alert concentrazione
    for sym, pos in positions.items():
        try:
            value = float(pos.get("entry_price", 0)) * float(pos.get("amount", 0))
            if capital > 0 and value > capital * 0.4:
                pct = (value/capital)*100
                alerts.append(("⚠️ Concentration", f"{sym}: {pct:.0f}%"))
        except:
            continue
    
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
        fig.add_trace(go.Scatter(
            y=df["cumulative"],
            mode='lines+markers',
            name='Cumulative P&L',
            line=dict(color='#00d4ff', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 212, 255, 0.1)'
        ))
        
        fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3)
        
        fig.update_layout(
            title="📈 Cumulative P&L",
            xaxis_title="Trade #",
            yaxis_title="P&L ($)",
            height=300,
            template="plotly_dark"
        )
        return fig
    except Exception as e:
        st.error(f"Errore grafico: {e}")
        return None

def create_win_loss_chart(state):
    """Grafico Win/Loss"""
    try:
        wins = int(state.get("winning_trades", 0))
        losses = int(state.get("losing_trades", 0))
        
        if wins + losses == 0:
            return None
        
        fig = go.Figure(data=[go.Pie(
            labels=['Wins', 'Losses'],
            values=[wins, losses],
            hole=.4,
            marker_colors=['#00ff88', '#ff4444'],
            textinfo='label+percent'
        )])
        
        fig.update_layout(
            title=f"🎯 Win/Loss ({wins}W / {losses}L)",
            height=300,
            template="plotly_dark"
        )
        return fig
    except:
        return None

# ==================== HEADER ====================
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.title("🚀 QUANTUM TRADER PRO v3.3")
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
    
    auto_refresh = st.checkbox("Auto Refresh", value=False)
    if auto_refresh:
        refresh_interval = st.slider("Interval (sec)", 10, 120, 30)
    
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
    show_charts = st.checkbox("Show Charts", value=True)
    show_history = st.checkbox("Show History", value=True)
    trade_limit = st.slider("Recent Trades", 5, 50, 20)

# ==================== CARICA STATO ====================
state = load_state()
if not state:
    st.error("❌ State file non disponibile")
    st.stop()

# ==================== ALERT ====================
alerts = check_alerts(state)
if alerts:
    for alert_type, alert_msg in alerts:
        st.warning(f"{alert_type}: {alert_msg}")
    st.markdown("---")

# ==================== ESTRAI DATI ====================
capital = float(state.get("capital", 0))
total_invested = float(state.get("total_invested", 0))
positions = state.get("positions", {})
total_trades = int(state.get("total_trades", 0))
winning_trades = int(state.get("winning_trades", 0))
losing_trades = int(state.get("losing_trades", 0))
cycle_count = int(state.get("cycle_count", 0))
total_pnl = float(state.get("total_pnl", 0))
total_fees = float(state.get("total_fees_paid", 0))
trade_history = state.get("trade_history", [])
max_portfolio = float(state.get("max_portfolio_value", 0))
max_drawdown = float(state.get("max_drawdown", 0))

# Calcola portfolio value
portfolio_value = capital
for pos in positions.values():
    try:
        portfolio_value += float(pos.get("entry_price", 0)) * float(pos.get("amount", 0))
    except:
        continue

win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

# ==================== METRICHE PRINCIPALI ====================
st.subheader("💎 Portfolio Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    portfolio_change = ((portfolio_value / total_invested - 1) * 100) if total_invested > 0 else 0
    st.metric(
        "Portfolio Value",
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
        f"${total_pnl:+,.2f}",
        delta=f"{(total_pnl/total_invested*100):+.2f}%" if total_invested > 0 else None
    )

with col5:
    st.metric("Win Rate", f"{win_rate:.1f}%", delta=f"{winning_trades}W/{losing_trades}L")

# ==================== STATS SECONDARIE ====================
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🔄 Cycles", f"{cycle_count:,}")

with col2:
    st.metric("💸 Total Fees", f"${total_fees:.4f}")

with col3:
    st.metric("📊 Max Portfolio", f"${max_portfolio:.2f}")

with col4:
    st.metric("📉 Max Drawdown", f"${max_drawdown:.2f}")

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

# ==================== POSIZIONI ====================
st.markdown("---")
st.subheader("🎯 Active Positions")

if positions:
    for symbol, pos in positions.items():
        try:
            entry_price = float(pos.get("entry_price", 0))
            amount = float(pos.get("amount", 0))
            highest = float(pos.get("highest_price", entry_price))
            entry_fear = pos.get("entry_fear", "N/A")
            entry_time = pos.get("entry_time", "N/A")
            
            value = entry_price * amount
            pnl = calculate_position_pnl(pos)
            pnl_pct = (pnl / value * 100) if value > 0 else 0
            
            status = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "🟡"
            
            with st.expander(f"{status} **{symbol}** — Value: ${value:.2f} | P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)"):
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.write(f"**Entry:** ${entry_price:.8f}")
                    st.write(f"**Amount:** {amount:.8f}")
                
                with c2:
                    st.write(f"**Value:** ${value:.2f}")
                    st.markdown(f"**P&L:** {format_pnl(pnl)}", unsafe_allow_html=True)
                
                with c3:
                    st.write(f"**Fear Index:** {entry_fear}")
                    st.write(f"**Highest:** ${highest:.2f}")
        except Exception as e:
            st.error(f"Error {symbol}: {e}")
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
            # Seleziona colonne disponibili
            cols = []
            for c in ["symbol", "action", "price", "amount", "pnl", "fee", "timestamp"]:
                if c in df.columns:
                    cols.append(c)
            
            if cols:
                display = df[cols].iloc[::-1].reset_index(drop=True)
                
                # Formatta
                if "price" in display.columns:
                    display["price"] = display["price"].apply(lambda x: f"${float(x):.6f}" if pd.notna(x) else "N/A")
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
                    "📥 Export CSV",
                    csv,
                    f"quantum_trades_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv",
                    use_container_width=True
                )
    except Exception as e:
        st.error(f"Error trade history: {e}")

# ==================== FOOTER ====================
st.markdown("---")
c1, c2, c3 = st.columns(3)

with c1:
    st.caption(f"🤖 Quantum Trader v3.3 | Invested: ${total_invested:.2f}")
with c2:
    st.caption(f"📊 Trades: {total_trades} | Fees: ${total_fees:.4f}")
with c3:
    file_size = os.path.getsize(STATE_FILE) / 1024
    st.caption(f"⚡ State: {file_size:.1f}KB")

# ==================== AUTO-REFRESH ====================
if auto_refresh:
    import time
    time.sleep(refresh_interval)
    st.rerun()

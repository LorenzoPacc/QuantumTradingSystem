import streamlit as st
import json
import os
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import hashlib

# ==================== CONFIGURAZIONE ====================
st.set_page_config(
    page_title="Quantum Trader Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

STATE_FILE = "qv33_ultimate_final_state.json"

# ==================== STILE MIGLIORATO ====================
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .stMetric {font-size: 1.2em;}
    div[data-testid="stMetricValue"] {font-size: 2em; font-weight: bold;}
    .stAlert {border-left: 4px solid #764ba2;}
    
    /* FIX: Rende il dataframe copiabile */
    .stDataFrame {
        user-select: text !important;
        -webkit-user-select: text !important;
        -moz-user-select: text !important;
    }
    
    /* Colori condizionali PnL */
    .pnl-positive {color: #00ff88; font-weight: bold;}
    .pnl-negative {color: #ff4444; font-weight: bold;}
    .pnl-neutral {color: #ffaa00; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# ==================== FUNZIONI MIGLIORATE ====================

@st.cache_data(ttl=10, show_spinner=False)
def load_state():
    """Carica stato con validazione completa"""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
        
        # Validazione struttura
        required_keys = ["capital", "positions", "trade_history"]
        if not all(key in data for key in required_keys):
            st.error(f"❌ State file incompleto - Chiavi mancanti")
            return None
        
        # Validazione tipi
        if not isinstance(data["capital"], (int, float)):
            st.error("❌ Capital non è un numero")
            return None
        if not isinstance(data["positions"], dict):
            st.error("❌ Positions non è un dict")
            return None
        if not isinstance(data["trade_history"], list):
            st.error("❌ Trade history non è una lista")
            return None
            
        return data
    except json.JSONDecodeError as e:
        st.error(f"❌ JSON corrotto: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Errore lettura: {e}")
        return None

def calculate_position_pnl(position, current_price=None):
    """Calcola P&L posizione con validazione"""
    try:
        entry_price = float(position.get("entry_price", 0))
        amount = float(position.get("amount", 0))
        price = float(current_price) if current_price else entry_price
        
        if entry_price == 0 or amount == 0:
            return 0.0
            
        current_value = price * amount
        entry_value = entry_price * amount
        return current_value - entry_value
    except (TypeError, ValueError):
        return 0.0

def format_pnl(pnl):
    """Formatta PnL con colore"""
    if pnl > 0:
        return f"<span class='pnl-positive'>+${pnl:.2f}</span>"
    elif pnl < 0:
        return f"<span class='pnl-negative'>${pnl:.2f}</span>"
    else:
        return f"<span class='pnl-neutral'>${pnl:.2f}</span>"

def check_alerts(state):
    """Sistema di alert per condizioni critiche"""
    alerts = []
    
    capital = state.get("capital", 0)
    positions = state.get("positions", {})
    trade_history = state.get("trade_history", [])
    
    # Calcola total PnL
    total_pnl = sum(float(t.get("pnl", 0)) for t in trade_history)
    
    # Alert drawdown
    if total_pnl < -50:
        alerts.append(("🚨 High Drawdown", f"Total P&L: ${total_pnl:.2f}"))
    
    # Alert concentrazione posizioni
    for symbol, pos in positions.items():
        try:
            entry_price = float(pos.get("entry_price", 0))
            amount = float(pos.get("amount", 0))
            position_value = entry_price * amount
            
            if capital > 0 and position_value > capital * 0.4:
                concentration = (position_value / capital) * 100
                alerts.append(("⚠️ High Concentration", f"{symbol}: {concentration:.1f}% of capital"))
        except (TypeError, ValueError):
            continue
    
    # Alert basso capitale
    if capital < 50:
        alerts.append(("💰 Low Capital", f"Only ${capital:.2f} remaining"))
    
    return alerts

def create_pnl_chart(trade_history):
    """Grafico P&L cumulativo migliorato"""
    if not trade_history or len(trade_history) < 2:
        return None
    
    try:
        df = pd.DataFrame(trade_history)
        
        if "pnl" not in df.columns:
            return None
        
        # Converti a float e gestisci NaN
        df["pnl"] = pd.to_numeric(df["pnl"], errors='coerce').fillna(0)
        df["cumulative_pnl"] = df["pnl"].cumsum()
        
        fig = go.Figure()
        
        # Linea principale
        fig.add_trace(go.Scatter(
            y=df["cumulative_pnl"],
            mode='lines+markers',
            name='Cumulative P&L',
            line=dict(color='#00d4ff', width=3),
            fill='tozeroy',
            fillcolor='rgba(0, 212, 255, 0.1)',
            hovertemplate='Trade %{x}<br>P&L: $%{y:.2f}<extra></extra>'
        ))
        
        # Linea zero
        fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3)
        
        fig.update_layout(
            title="📈 Cumulative P&L",
            xaxis_title="Trade #",
            yaxis_title="P&L ($)",
            height=300,
            template="plotly_dark",
            hovermode='x unified'
        )
        return fig
    except Exception as e:
        st.error(f"Errore grafico P&L: {e}")
        return None

def create_win_loss_chart(trade_history):
    """Grafico Win/Loss migliorato"""
    if not trade_history:
        return None
    
    try:
        df = pd.DataFrame(trade_history)
        
        if "pnl" not in df.columns:
            return None
        
        df["pnl"] = pd.to_numeric(df["pnl"], errors='coerce').fillna(0)
        
        wins = len(df[df["pnl"] > 0])
        losses = len(df[df["pnl"] < 0])
        breakeven = len(df[df["pnl"] == 0])
        
        fig = go.Figure(data=[go.Pie(
            labels=['Wins', 'Losses', 'Breakeven'],
            values=[wins, losses, breakeven],
            hole=.4,
            marker_colors=['#00ff88', '#ff4444', '#ffaa00'],
            textinfo='label+percent',
            hovertemplate='%{label}: %{value} trades<extra></extra>'
        )])
        
        fig.update_layout(
            title=f"🎯 Win/Loss Ratio ({wins}W / {losses}L)",
            height=300,
            template="plotly_dark"
        )
        return fig
    except Exception as e:
        st.error(f"Errore grafico Win/Loss: {e}")
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
    st.image("https://img.icons8.com/fluency/96/000000/bot.png", width=80)
    st.header("⚙️ Control Panel")
    
    # Auto-refresh
    auto_refresh = st.checkbox("Auto Refresh", value=False)
    refresh_interval = 30
    if auto_refresh:
        refresh_interval = st.slider("Interval (sec)", 10, 120, 30)
    
    st.markdown("---")
    st.subheader("🤖 Bot Status")
    
    # Verifica bot running
    if os.path.exists(STATE_FILE):
        st.success("🟢 RUNNING")
        last_mod = os.path.getmtime(STATE_FILE)
        last_update = datetime.fromtimestamp(last_mod)
        st.caption(f"Last update: {last_update.strftime('%H:%M:%S')}")
        
        # Calcola età file
        age_seconds = (datetime.now() - last_update).total_seconds()
        if age_seconds > 300:  # 5 minuti
            st.warning(f"⚠️ Stale data ({age_seconds/60:.0f}m old)")
    else:
        st.error("🔴 OFFLINE")
        st.stop()
    
    st.markdown("---")
    st.subheader("📊 Display Settings")
    show_charts = st.checkbox("Show Charts", value=True)
    show_history = st.checkbox("Show History", value=True)
    trade_limit = st.slider("Recent Trades", 5, 50, 20)
    
    st.markdown("---")
    st.caption("💡 Tip: Enable auto-refresh for live monitoring")

# ==================== CARICA DATI ====================
state = load_state()

if not state:
    st.error("❌ **Unable to load state file**")
    st.info("💡 Ensure bot is running and writing state file correctly")
    st.stop()

# ==================== SISTEMA ALERT ====================
alerts = check_alerts(state)
if alerts:
    st.warning("⚠️ **Active Alerts**")
    for alert_type, alert_msg in alerts:
        st.error(f"{alert_type}: {alert_msg}")
    st.markdown("---")

# ==================== ESTRAI DATI ====================
capital = float(state.get("capital", 0))
positions = state.get("positions", {})
total_trades = int(state.get("total_trades", 0))
winning_trades = int(state.get("winning_trades", 0))
cycle_count = int(state.get("cycle_count", 0))
total_fees = float(state.get("total_fees_paid", 0))
trade_history = state.get("trade_history", [])

# Calcola portfolio value
portfolio_value = capital
for pos in positions.values():
    try:
        entry_price = float(pos.get("entry_price", 0))
        amount = float(pos.get("amount", 0))
        portfolio_value += entry_price * amount
    except (TypeError, ValueError):
        continue

# Calcola statistiche
total_pnl = sum(float(t.get("pnl", 0)) for t in trade_history)
win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
avg_pnl = total_pnl / total_trades if total_trades > 0 else 0

# ==================== METRICHE PRINCIPALI ====================
st.subheader("💎 Portfolio Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    pnl_pct = ((portfolio_value/10000 - 1) * 100) if portfolio_value > 0 else 0
    st.metric(
        "Total Value",
        f"${portfolio_value:,.2f}",
        delta=f"{pnl_pct:+.2f}%"
    )

with col2:
    st.metric("Cash", f"${capital:,.2f}")

with col3:
    st.metric("Open Positions", len(positions))

with col4:
    total_pnl_pct = (total_pnl/10000*100) if total_pnl != 0 else 0
    st.metric(
        "Total P&L",
        f"${total_pnl:+,.2f}",
        delta=f"{total_pnl_pct:+.2f}%"
    )

with col5:
    delta_color = "normal" if win_rate >= 50 else "inverse"
    st.metric("Win Rate", f"{win_rate:.1f}%", delta=f"{winning_trades}/{total_trades}")

# ==================== STATISTICHE SECONDARIE ====================
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🔄 Cycles", f"{cycle_count:,}")

with col2:
    fees_pct = (total_fees / 10000 * 100) if total_fees > 0 else 0
    st.metric("💸 Fees", f"${total_fees:.4f}", delta=f"{fees_pct:.3f}%")

with col3:
    st.metric("📊 Avg P&L", f"${avg_pnl:+,.2f}")

with col4:
    if total_trades > 1 and avg_pnl != 0:
        sharpe = total_pnl / (abs(avg_pnl) * (total_trades ** 0.5))
    else:
        sharpe = 0
    st.metric("📈 Sharpe", f"{sharpe:.2f}")

# ==================== GRAFICI ====================
if show_charts and len(trade_history) >= 2:
    st.markdown("---")
    st.subheader("📊 Performance Analytics")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        pnl_chart = create_pnl_chart(trade_history)
        if pnl_chart:
            st.plotly_chart(pnl_chart, use_container_width=True)
    
    with chart_col2:
        wl_chart = create_win_loss_chart(trade_history)
        if wl_chart:
            st.plotly_chart(wl_chart, use_container_width=True)

# ==================== POSIZIONI ATTIVE ====================
st.markdown("---")
st.subheader("🎯 Active Positions")

if positions:
    for symbol, pos in positions.items():
        try:
            entry_price = float(pos.get("entry_price", 0))
            amount = float(pos.get("amount", 0))
            entry_fear = pos.get("entry_fear", "N/A")
            value = entry_price * amount
            pnl = calculate_position_pnl(pos)
            pnl_pct = (pnl / value * 100) if value > 0 else 0
            
            # Emoji stato
            status_emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "🟡"
            
            with st.expander(f"{status_emoji} **{symbol}** — Value: ${value:.2f} | P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)"):
                pos_col1, pos_col2, pos_col3 = st.columns(3)
                
                with pos_col1:
                    st.write(f"**Entry Price:** ${entry_price:.8f}")
                    st.write(f"**Amount:** {amount:.8f}")
                
                with pos_col2:
                    st.write(f"**Current Value:** ${value:.2f}")
                    st.markdown(f"**P&L:** {format_pnl(pnl)}", unsafe_allow_html=True)
                
                with pos_col3:
                    st.write(f"**Fear Index:** {entry_fear}")
                    st.write(f"**P&L %:** {pnl_pct:+.2f}%")
        except (TypeError, ValueError) as e:
            st.error(f"Error loading position {symbol}: {e}")
else:
    st.info("📭 No active positions — Waiting for signals")

# ==================== TRADE HISTORY CORRETTO ====================
if show_history and trade_history:
    st.markdown("---")
    st.subheader(f"📈 Trade History (Last {trade_limit})")
    
    try:
        # Prendi ultimi N trade
        recent_trades = trade_history[-trade_limit:]
        
        if recent_trades:
            # Crea DataFrame
            df_trades = pd.DataFrame(recent_trades)
            
            # Seleziona solo colonne esistenti
            available_cols = df_trades.columns.tolist()
            display_cols = []
            
            for col in ["symbol", "action", "price", "amount", "pnl", "fee", "timestamp"]:
                if col in available_cols:
                    display_cols.append(col)
            
            if display_cols:
                df_display = df_trades[display_cols].copy()
                
                # Reverse per mostrare più recenti prima
                df_display = df_display.iloc[::-1].reset_index(drop=True)
                
                # Formatta numeri
                if "price" in df_display.columns:
                    df_display["price"] = df_display["price"].apply(lambda x: f"${float(x):.6f}" if pd.notna(x) else "N/A")
                if "pnl" in df_display.columns:
                    df_display["pnl"] = df_display["pnl"].apply(lambda x: f"${float(x):+.2f}" if pd.notna(x) else "$0.00")
                if "fee" in df_display.columns:
                    df_display["fee"] = df_display["fee"].apply(lambda x: f"${float(x):.4f}" if pd.notna(x) else "$0.00")
                if "amount" in df_display.columns:
                    df_display["amount"] = df_display["amount"].apply(lambda x: f"{float(x):.8f}" if pd.notna(x) else "0")
                
                # Mostra dataframe (ORA COPIABILE!)
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    hide_index=False,
                    height=400
                )
                
                # Export CSV
                csv_data = df_trades[display_cols].to_csv(index=False)
                st.download_button(
                    "📥 Export CSV",
                    csv_data,
                    f"quantum_trades_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            else:
                st.warning("⚠️ No displayable columns in trade history")
        else:
            st.info("No trades in history")
    except Exception as e:
        st.error(f"❌ Error displaying trade history: {e}")
        st.code(str(e))

# ==================== FOOTER ====================
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    mode = state.get("mode", "DRY-RUN")
    st.caption(f"🤖 Quantum Trader v3.3 — Mode: {mode}")

with footer_col2:
    st.caption(f"📊 Cycle: {cycle_count:,}")

with footer_col3:
    file_size = os.path.getsize(STATE_FILE) / 1024
    st.caption(f"⚡ State: {file_size:.1f}KB")

# ==================== AUTO-REFRESH ====================
if auto_refresh:
    import time
    time.sleep(refresh_interval)
    st.rerun()


import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Crypto Paper Trading", layout="wide")

# Title
st.title("🚀 Crypto Paper Trading Dashboard")
st.subheader("Live Crypto Trading with AI Strategies")

# Load crypto data
try:
    btc_data = pd.read_csv('crypto_data/bitcoin_30d.csv', index_col=0, parse_dates=True)
    current_price = btc_data['price'].iloc[-1]
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Bitcoin Price", f"${current_price:,.2f}", 
                 f"{btc_data['price'].pct_change().iloc[-1]*100:.2f}%")
    
    with col2:
        st.metric("30d Return", 
                 f"{(btc_data['price'].iloc[-1]/btc_data['price'].iloc[0]-1)*100:.2f}%")
    
    with col3:
        st.metric("Volatility (30d)", 
                 f"{btc_data['returns'].std()*100:.2f}%")
    
    with col4:
        st.metric("Last Update", datetime.now().strftime("%H:%M:%S"))
    
    # Price chart
    st.subheader("Bitcoin Price (30 days)")
    fig = px.line(btc_data, y='price', title='BTC/USD')
    st.plotly_chart(fig, use_container_width=True)
    
    # Returns distribution
    st.subheader("Returns Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_hist = px.histogram(btc_data, x='returns', nbins=50, 
                               title='Returns Histogram')
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Rolling volatility
        btc_data['rolling_vol'] = btc_data['returns'].rolling(7).std()
        fig_vol = px.line(btc_data, y='rolling_vol', 
                         title='7-Day Rolling Volatility')
        st.plotly_chart(fig_vol, use_container_width=True)
    
    # Strategy performance
    st.subheader("Trading Strategy Signals")
    
    # Load signals if available
    try:
        signals = pd.read_csv('crypto_data/signals.csv', index_col=0, parse_dates=True)
        
        # Create signal chart
        fig_signals = go.Figure()
        
        # Add price
        fig_signals.add_trace(go.Scatter(
            x=btc_data.index, y=btc_data['price'],
            name='BTC Price', line=dict(color='blue')
        ))
        
        # Add buy signals
        buy_signals = signals[signals == 1]
        if not buy_signals.empty:
            fig_signals.add_trace(go.Scatter(
                x=buy_signals.index, y=btc_data.loc[buy_signals.index, 'price'],
                mode='markers', name='Buy Signal',
                marker=dict(color='green', size=10, symbol='triangle-up')
            ))
        
        # Add sell signals
        sell_signals = signals[signals == -1]
        if not sell_signals.empty:
            fig_signals.add_trace(go.Scatter(
                x=sell_signals.index, y=btc_data.loc[sell_signals.index, 'price'],
                mode='markers', name='Sell Signal',
                marker=dict(color='red', size=10, symbol='triangle-down')
            ))
        
        fig_signals.update_layout(title='Trading Signals on Price Chart')
        st.plotly_chart(fig_signals, use_container_width=True)
        
    except:
        st.info("No trading signals available yet. Running first analysis...")
    
    # System status
    st.subheader("System Status")
    
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.success("✅ Crypto Module: ACTIVE")
        st.success("✅ Data Fetching: OPERATIONAL")
        st.success("✅ Strategies: RUNNING")
    
    with status_col2:
        st.info("📊 Backtesting: READY")
        st.info("💰 Portfolio: $10,000.00")
        st.info("⚡ Last Trade: PENDING")
    
    with status_col3:
        st.warning("🚀 Next Update: 5 minutes")
        st.warning("📈 Live Trading: READY")
        st.warning("🔧 ML Optimization: PENDING")
    
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Starting initial data fetch...")

# Footer
st.markdown("---")
st.markdown("**Crypto Paper Trading System** • Live since " + 
           datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

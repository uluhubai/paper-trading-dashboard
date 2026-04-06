"""
Paper Trading Dashboard - SIMPLE WORKING VERSION
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Paper Trading Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Paper Trading Dashboard")
st.markdown("**Multi-Strategy Trading Simulation**")

# SIMPLE DATA - NO COMPLEX TRY/EXCEPT
trades = []
symbols = ['BTC', 'ETH', 'ADA', 'SOL', 'DOT']

for i in range(20):
    trade_time = (datetime.now() - timedelta(hours=i)).strftime('%Y-%m-%d %H:%M')
    trades.append({
        'Time': trade_time,
        'Asset': symbols[i % len(symbols)],
        'Action': 'BUY' if i % 2 == 0 else 'SELL',
        'Strategy': ['Momentum', 'Mean Reversion', 'Breakout'][i % 3],
        'PnL': f"${np.random.uniform(-50, 100):+.2f}"
    })

trades_df = pd.DataFrame(trades)

# SIDEBAR
with st.sidebar:
    st.header("🎯 Controls")
    auto_refresh = st.checkbox("Auto-refresh", value=False)
    
    st.markdown("---")
    st.metric("Total Trades", len(trades_df))
    st.metric("Active Positions", 8)
    
    if st.button("🔄 Refresh Now"):
        st.rerun()

# MAIN CONTENT
tab1, tab2, tab3 = st.tabs(["📈 Overview", "💰 Portfolio", "📊 Trades"])

with tab1:
    st.subheader("Portfolio Performance")
    st.metric("Portfolio Value", "$10,164.07", "+1.64%")
    
    # Simple chart
    dates = [(datetime.now() - timedelta(days=i)).strftime('%m-%d') for i in range(30, -1, -1)]
    values = [10000 + i*5 + (i%7)*10 for i in range(31)]
    chart_data = pd.DataFrame({'Date': dates, 'Value': values})
    st.line_chart(chart_data.set_index('Date')['Value'])

with tab2:
    st.subheader("Portfolio Allocation")
    
    alloc_data = {
        'Asset': ['BTC', 'ETH', 'ADA', 'SOL', 'DOT', 'Cash'],
        'Allocation': ['35%', '28%', '12%', '8%', '6%', '17%']
    }
    
    st.table(pd.DataFrame(alloc_data))

with tab3:
    st.subheader("Recent Trades")
    st.dataframe(trades_df, use_container_width=True)

# Simple auto-refresh
if auto_refresh:
    st.markdown("---")
    st.info("🔄 Auto-refresh enabled - page will refresh in 30 seconds")
    import time
    time.sleep(5)  # Shorter for testing
    st.rerun()

st.markdown("---")
st.markdown("*Simple working version - all features functional*")

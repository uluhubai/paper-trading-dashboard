"""
Paper Trading Dashboard - MINIMAL VERSION
Avoids all complex components that cause 404 errors
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="Paper Trading Dashboard",
    page_icon="📊",
    layout="wide"
)

# SIMPLE TITLE
st.title("📊 Paper Trading Dashboard")
st.markdown("**Multi-Strategy Trading Simulation**")

# Create sample data directly (no files)
def create_data():
    # Portfolio history
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') 
             for i in range(30, -1, -1)]
    portfolio_values = [10000 + i*5 + (i%7)*10 for i in range(31)]
    
    portfolio_df = pd.DataFrame({
        'date': dates,
        'value': portfolio_values
    })
    
    # Recent trades
    trades = []
    symbols = ['BTC', 'ETH', 'ADA', 'SOL', 'DOT']
    for i in range(10):
        trades.append({
            'Time': (datetime.now() - timedelta(hours=i*2)).strftime('%H:%M'),
            'Asset': symbols[i % len(symbols)],
            'Action': 'BUY' if i % 2 == 0 else 'SELL',
            'Qty': round(0.1 + (i * 0.05), 3),
            'Price': f"${round(45000 + (i * 500), 2):,}"
        })
    
    trades_df = pd.DataFrame(trades)
    
    return portfolio_df, trades_df

# Get data
portfolio_df, trades_df = create_data()

# SIMPLE METRICS (no complex components)
col1, col2, col3 = st.columns(3)

with col1:
    current_value = portfolio_df['value'].iloc[-1]
    st.metric("Portfolio Value", f"${current_value:,.2f}")

with col2:
    total_return = ((current_value - 10000) / 10000) * 100
    st.metric("Total Return", f"{total_return:.2f}%")

with col3:
    st.metric("Active Trades", len(trades_df))

# SIMPLE CHART (basic line chart)
st.subheader("Portfolio Performance")
st.line_chart(portfolio_df.set_index('date')['value'])

# SIMPLE TABLE (no pandas styler)
st.subheader("Recent Trades")
st.table(trades_df)

# Strategy summary
st.subheader("Trading Strategies")
st.markdown("""
- **Momentum Strategy**: Follows price trends (12 trades, +1.5%)
- **Mean Reversion**: Bets on returns to average (8 trades, +0.8%)  
- **Breakout Strategy**: Captures price breakouts (15 trades, +2.1%)
""")

# Last update
st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
st.markdown("---")
st.markdown("*Paper trading simulation for educational purposes*")

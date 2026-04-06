"""
Paper Trading Dashboard - Streamlit Cloud Optimized
Simple, reliable version for cloud deployment
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="Paper Trading Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("📊 Paper Trading Dashboard")
st.markdown("Multi-Strategy Trading Simulation")

def create_sample_data():
    """Create sample data for demonstration"""
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    # Create strategies data - FIXED: Added total_pnl key
    strategies = {
        'momentum': {
            'performance': 1.5,
            'trades': 12,
            'win_rate': 58.3,
            'sharpe_ratio': 1.2,
            'max_drawdown': -4.2,
            'total_pnl': 150.25  # ADDED THIS KEY
        },
        'mean_reversion': {
            'performance': 0.8,
            'trades': 8,
            'win_rate': 62.5,
            'sharpe_ratio': 0.9,
            'max_drawdown': -3.1,
            'total_pnl': 80.50  # ADDED THIS KEY
        },
        'breakout': {
            'performance': 2.1,
            'trades': 15,
            'win_rate': 53.3,
            'sharpe_ratio': 1.5,
            'max_drawdown': -5.8,
            'total_pnl': 210.75  # ADDED THIS KEY
        }
    }
    
    with open(os.path.join(data_dir, 'strategies.json'), 'w') as f:
        json.dump(strategies, f, indent=2)
    
    # Create portfolio history
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') 
             for i in range(30, -1, -1)]
    portfolio_values = [10000 + i*5 + (i%7)*10 for i in range(31)]
    
    portfolio_df = pd.DataFrame({
        'date': dates,
        'portfolio_value': portfolio_values,
        'cash': [5000 - i*3 for i in range(31)]
    })
    
    portfolio_df.to_csv(os.path.join(data_dir, 'portfolio_history.csv'), index=False)
    
    # Create recent trades
    trades = []
    symbols = ['BTC', 'ETH', 'ADA', 'SOL', 'DOT']
    for i in range(15):
        trades.append({
            'timestamp': (datetime.now() - timedelta(hours=i*2)).strftime('%Y-%m-%d %H:%M'),
            'symbol': symbols[i % len(symbols)],
            'action': 'BUY' if i % 2 == 0 else 'SELL',
            'quantity': round(0.1 + (i * 0.05), 3),
            'price': round(45000 + (i * 500), 2),
            'strategy': ['momentum', 'mean_reversion', 'breakout'][i % 3],
            'pnl': round((i % 5) * 25.5 - 10, 2)
        })
    
    trades_df = pd.DataFrame(trades)
    trades_df.to_csv(os.path.join(data_dir, 'recent_trades.csv'), index=False)
    
    return strategies, portfolio_df, trades_df

# Create or load data
try:
    strategies_file = 'data/strategies.json'
    if os.path.exists(strategies_file):
        with open(strategies_file, 'r') as f:
            strategies = json.load(f)
        portfolio_df = pd.read_csv('data/portfolio_history.csv')
        trades_df = pd.read_csv('data/recent_trades.csv')
    else:
        strategies, portfolio_df, trades_df = create_sample_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    # Fallback: create fresh data
    strategies, portfolio_df, trades_df = create_sample_data()

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🎯 Strategies", "💰 Portfolio", "🔄 Recent Trades"])

with tab1:
    st.header("Dashboard Overview")
    
    # Key metrics - FIXED: Use .get() for safe access
    col1, col2, col3, col4 = st.columns(4)
    
    total_portfolio = portfolio_df['portfolio_value'].iloc[-1]
    total_return = ((total_portfolio - 10000) / 10000) * 100
    
    with col1:
        st.metric("Total Portfolio", f"${total_portfolio:,.2f}", f"{total_return:.2f}%")
    
    with col2:
        total_trades = sum(s.get('trades', 0) for s in strategies.values())
        st.metric("Total Trades", total_trades)
    
    with col3:
        win_rates = [s.get('win_rate', 0) for s in strategies.values()]
        avg_win_rate = np.mean(win_rates) if win_rates else 0
        st.metric("Avg Win Rate", f"{avg_win_rate:.1f}%")
    
    with col4:
        total_pnl = sum(s.get('total_pnl', 0) for s in strategies.values())  # FIXED: using .get()
        st.metric("Total P&L", f"${total_pnl:,.2f}")
    
    # Portfolio chart
    st.subheader("Portfolio Value Over Time")
    st.line_chart(portfolio_df.set_index('date')['portfolio_value'])

with tab2:
    st.header("Strategy Performance")
    
    for strategy_name, metrics in strategies.items():
        st.subheader(f"{strategy_name.title()} Strategy")
        
        cols = st.columns(5)
        with cols[0]:
            st.metric("Performance", f"{metrics.get('performance', 0)}%")
        with cols[1]:
            st.metric("Win Rate", f"{metrics.get('win_rate', 0)}%")
        with cols[2]:
            st.metric("Trades", metrics.get('trades', 0))
        with cols[3]:
            st.metric("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0)}")
        with cols[4]:
            st.metric("Max Drawdown", f"{metrics.get('max_drawdown', 0)}%")
        
        win_rate = metrics.get('win_rate', 0)
        if win_rate > 0:
            st.progress(win_rate / 100)
        st.markdown("---")

with tab3:
    st.header("Portfolio Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Allocation")
        
        # Sample allocation
        allocation_data = {
            'Asset': ['BTC', 'ETH', 'ADA', 'SOL', 'Cash'],
            'Value': [3500, 2800, 1200, 800, 1700],
            'Percentage': [35, 28, 12, 8, 17]
        }
        
        allocation_df = pd.DataFrame(allocation_data)
        st.dataframe(allocation_df, use_container_width=True)
    
    with col2:
        st.subheader("Performance Metrics")
        
        metrics_data = {
            'Metric': ['Total Return', 'Daily Avg Return', 'Volatility', 'Sharpe Ratio', 'Sortino Ratio'],
            'Value': [f'{total_return:.2f}%', '0.15%', '2.3%', '1.4', '1.8']
        }
        
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, use_container_width=True)

with tab4:
    st.header("Recent Trading Activity")
    
    # Show recent trades
    st.dataframe(trades_df, use_container_width=True)
    
    # Trade statistics
    st.subheader("Trade Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        buy_trades = len(trades_df[trades_df['action'] == 'BUY'])
        st.metric("Buy Trades", buy_trades)
    
    with col2:
        sell_trades = len(trades_df[trades_df['action'] == 'SELL'])
        st.metric("Sell Trades", sell_trades)
    
    with col3:
        total_volume = trades_df['quantity'].sum()
        st.metric("Total Volume", f"{total_volume:.3f}")

# Sidebar info
with st.sidebar:
    st.header("ℹ️ Info")
    st.markdown("""
    **Paper Trading Dashboard**
    
    Simulates 3 trading strategies:
    
    1. **Momentum** - Follows trends
    2. **Mean Reversion** - Bets on returns to average  
    3. **Breakout** - Captures price breakouts
    
    Data updates daily with simulated trades.
    """)
    
    st.markdown("---")
    st.markdown("**Last Updated:**")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()

# Footer
st.markdown("---")
st.markdown("*Paper trading simulation for educational purposes*")

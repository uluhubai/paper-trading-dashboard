"""
Paper Trading Dashboard - Streamlit Cloud Deployment
Final version with dark mode fix and better styling
"""

import streamlit as st
import sys
import os
import json
import pandas as pd
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set page config with light theme
st.set_page_config(
    page_title="Paper Trading Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force light theme
st.markdown("""
<style>
    /* Force light theme */
    .stApp {
        background-color: white !important;
        color: black !important;
    }
    
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #00ff88 0%, #00ccff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    /* Sidebar styling */
    .stSidebar {
        background-color: #f8f9fa !important;
        color: black !important;
    }
    
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar p {
        color: black !important;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Force all text to be visible */
    * {
        color: black !important;
    }
    
    /* Specific fix for Streamlit Cloud dark mode issue */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #333333 !important;
    }
</style>

<div class="main-header">📊 Paper Trading Dashboard</div>
""", unsafe_allow_html=True)

def create_initial_data_if_missing():
    """Create initial data files if they don't exist"""
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    # Check if strategy data exists
    strategies_file = os.path.join(data_dir, 'strategies.json')
    if not os.path.exists(strategies_file):
        strategies = {
            'momentum': {
                'performance': 1.5,
                'trades': 12,
                'win_rate': 58.3,
                'sharpe_ratio': 1.2,
                'max_drawdown': -4.2
            },
            'mean_reversion': {
                'performance': 0.8,
                'trades': 8,
                'win_rate': 62.5,
                'sharpe_ratio': 0.9,
                'max_drawdown': -3.1
            },
            'breakout': {
                'performance': 2.1,
                'trades': 15,
                'win_rate': 53.3,
                'sharpe_ratio': 1.5,
                'max_drawdown': -5.8
            }
        }
        with open(strategies_file, 'w') as f:
            json.dump(strategies, f, indent=2)
    
    # Check if portfolio history exists
    portfolio_file = os.path.join(data_dir, 'portfolio_history.csv')
    if not os.path.exists(portfolio_file):
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S') 
                 for i in range(30, -1, -1)]
        portfolio_values = [10000 + i*5 + (i%7)*10 for i in range(31)]
        
        portfolio_df = pd.DataFrame({
            'timestamp': dates,
            'portfolio_value': portfolio_values,
            'cash_balance': [5000 - i*3 for i in range(31)]
        })
        portfolio_df.to_csv(portfolio_file, index=False)
    
    # Check if recent trades exists
    trades_file = os.path.join(data_dir, 'recent_trades.csv')
    if not os.path.exists(trades_file):
        trades = []
        symbols = ['BTC', 'ETH', 'ADA', 'SOL', 'DOT']
        for i in range(10):
            trades.append({
                'timestamp': (datetime.now() - timedelta(hours=i*3)).strftime('%Y-%m-%d %H:%M:%S'),
                'symbol': symbols[i % len(symbols)],
                'action': 'BUY' if i % 2 == 0 else 'SELL',
                'quantity': 0.1 + (i * 0.05),
                'price': 45000 + (i * 500),
                'strategy': ['momentum', 'mean_reversion', 'breakout'][i % 3]
            })
        
        trades_df = pd.DataFrame(trades)
        trades_df.to_csv(trades_file, index=False)
    
    return True

# Create initial data if missing
create_initial_data_if_missing()

# Sidebar with strategy selection - FORCE VISIBLE TEXT
with st.sidebar:
    st.markdown("""
    <style>
    .sidebar-content * {
        color: #333333 !important;
        font-weight: bold !important;
    }
    </style>
    <div class="sidebar-content">
    """, unsafe_allow_html=True)
    
    st.header("🎯 Trading Strategies")
    
    # Strategy selection
    selected_strategy = st.selectbox(
        "Select Strategy to View:",
        ["All Strategies", "Momentum", "Mean Reversion", "Breakout"],
        index=0
    )
    
    st.markdown("---")
    
    # Display strategy metrics
    st.subheader("Strategy Performance")
    
    try:
        with open('data/strategies.json', 'r') as f:
            strategies = json.load(f)
        
        for strategy_name, metrics in strategies.items():
            with st.container():
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <h4 style="color: white !important;">{strategy_name.title()} Strategy</h4>
                <p style="color: white !important;">📈 Performance: {metrics['performance']}%</p>
                <p style="color: white !important;">🎯 Win Rate: {metrics['win_rate']}%</p>
                <p style="color: white !important;">🔄 Trades: {metrics['trades']}</p>
                </div>
                """, unsafe_allow_html=True)
    except:
        st.info("Loading strategy data...")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Import and run the main dashboard
try:
    # Try to import dashboard_v2
    from dashboard_v2 import main as dashboard_main
    
    # Run the dashboard
    dashboard_main()
    
except Exception as e:
    st.error(f"Error loading dashboard: {str(e)}")
    
    # Fallback to basic display with visible text
    st.markdown("""
    <style>
    .fallback-content * {
        color: #333333 !important;
    }
    </style>
    <div class="fallback-content">
    """, unsafe_allow_html=True)
    
    # Display sample data
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Portfolio Value", "$10,150.75", "+1.51%")
    
    with col2:
        st.metric("Active Positions", "3", "+1")
    
    with col3:
        st.metric("Total Return", "1.51%", "+0.25%")
    
    # Show recent trades
    st.subheader("Recent Trades")
    try:
        trades_df = pd.read_csv('data/recent_trades.csv')
        st.dataframe(trades_df, use_container_width=True)
    except:
        st.info("No trade data available yet")
    
    # Show portfolio history chart
    st.subheader("Portfolio History")
    try:
        portfolio_df = pd.read_csv('data/portfolio_history.csv')
        st.line_chart(portfolio_df.set_index('timestamp')['portfolio_value'])
    except:
        st.info("No portfolio history available yet")
    
    st.markdown("</div>", unsafe_allow_html=True)

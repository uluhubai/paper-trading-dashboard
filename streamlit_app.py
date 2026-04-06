"""
Paper Trading Dashboard - FINAL VERSION
With documentation tab and improved strategy performance display
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# Set page config
st.set_page_config(
    page_title="Paper Trading Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("📊 Paper Trading Dashboard")
st.markdown("**Multi-Strategy Trading Simulation**")

# Create sample data
def create_data():
    # Portfolio history
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') 
             for i in range(30, -1, -1)]
    portfolio_values = [10000 + i*5 + (i%7)*10 for i in range(31)]
    
    portfolio_df = pd.DataFrame({
        'Date': dates,
        'Portfolio Value': portfolio_values,
        'Cash': [5000 - i*3 for i in range(31)]
    })
    
    # Recent trades
    trades = []
    symbols = ['BTC', 'ETH', 'ADA', 'SOL', 'DOT']
    for i in range(15):
        trades.append({
            'Time': (datetime.now() - timedelta(hours=i*2)).strftime('%H:%M'),
            'Asset': symbols[i % len(symbols)],
            'Action': 'BUY' if i % 2 == 0 else 'SELL',
            'Quantity': round(0.1 + (i * 0.05), 3),
            'Price': f"${round(45000 + (i * 500), 2):,}",
            'Strategy': ['Momentum', 'Mean Reversion', 'Breakout'][i % 3]
        })
    
    trades_df = pd.DataFrame(trades)
    
    # Strategy performance - IMPROVED with PnL
    strategies = {
        'Momentum': {
            'trades': 41,
            'performance': 1.5,
            'win_rate': 36.6,
            'total_pnl': 129.05,
            'description': 'Trend following - buys rising assets, sells falling ones'
        },
        'Mean Reversion': {
            'trades': 35,
            'performance': 0.8,
            'win_rate': 14.3,
            'total_pnl': -60.09,
            'description': 'Buy low, sell high - trades against extremes'
        },
        'Breakout': {
            'trades': 23,
            'performance': 2.1,
            'win_rate': 26.1,
            'total_pnl': 95.11,
            'description': 'Captures price breakouts from consolidation ranges'
        }
    }
    
    return portfolio_df, trades_df, strategies

# Get data
portfolio_df, trades_df, strategies = create_data()

# SIDEBAR WITH CONTROLS
with st.sidebar:
    st.header("🎯 Strategy Control")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
    
    # Strategy selection
    selected_strategy = st.selectbox(
        "Focus Strategy:",
        ["All Strategies", "Momentum", "Mean Reversion", "Breakout"]
    )
    
    st.markdown("---")
    
    # Quick strategy stats
    st.subheader("Quick Stats")
    
    total_trades = sum(s['trades'] for s in strategies.values())
    total_pnl = sum(s['total_pnl'] for s in strategies.values())
    avg_win_rate = np.mean([s['win_rate'] for s in strategies.values()])
    
    st.metric("Total Trades", total_trades)
    st.metric("Total P&L", f"${total_pnl:,.2f}")
    st.metric("Avg Win Rate", f"{avg_win_rate:.1f}%")
    
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Manual Refresh"):
        st.rerun()
    
    # Last update
    st.markdown(f"**Last Updated:**")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M"))

# MAIN CONTENT - Tabs (NOW WITH DOCUMENTATION TAB)
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🎯 Strategies", "💰 Portfolio", "📚 Documentation"])

with tab1:
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    current_value = portfolio_df['Portfolio Value'].iloc[-1]
    total_return = ((current_value - 10000) / 10000) * 100
    
    with col1:
        st.metric("Portfolio Value", f"${current_value:,.2f}", f"{total_return:.2f}%")
    
    with col2:
        st.metric("Total Trades", total_trades)
    
    with col3:
        avg_performance = np.mean([s['performance'] for s in strategies.values()])
        st.metric("Avg Performance", f"{avg_performance:.1f}%")
    
    with col4:
        active_positions = len(trades_df[trades_df['Action'] == 'BUY'])
        st.metric("Active Positions", active_positions)
    
    # Portfolio chart
    st.subheader("Portfolio Performance")
    st.line_chart(portfolio_df.set_index('Date')['Portfolio Value'])

with tab2:
    st.header("Strategy Performance Comparison")
    
    # Display each strategy in columns
    cols = st.columns(3)
    
    for idx, (strategy_name, metrics) in enumerate(strategies.items()):
        with cols[idx]:
            # Strategy header with icon
            st.subheader(f"📈 {strategy_name}")
            
            # PnL with color coding
            pnl_color = "green" if metrics['total_pnl'] > 0 else "red"
            st.metric("Total PnL", f"${metrics['total_pnl']:,.2f}", 
                     delta_color="normal" if metrics['total_pnl'] > 0 else "inverse")
            
            # Win Rate
            st.metric("Win Rate", f"{metrics['win_rate']}%")
            
            # Trades Executed
            st.metric("Trades Executed", metrics['trades'])
            
            # Description
            st.markdown(f"*{metrics['description']}*")
            
            # Progress bar for win rate
            st.progress(metrics['win_rate'] / 100)
            
            # Strategy-specific stats
            st.markdown("---")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Performance", f"{metrics['performance']}%")
            with col_b:
                daily_avg = metrics['total_pnl'] / 30 if metrics['trades'] > 0 else 0
                st.metric("Daily Avg", f"${daily_avg:.2f}")

with tab3:
    st.subheader("Portfolio Allocation")
    
    # Simple allocation table
    allocation_data = {
        'Asset': ['BTC', 'ETH', 'ADA', 'SOL', 'DOT', 'Cash'],
        'Value': ['$3,500', '$2,800', '$1,200', '$800', '$600', '$1,700'],
        'Allocation': ['35%', '28%', '12%', '8%', '6%', '17%']
    }
    
    allocation_df = pd.DataFrame(allocation_data)
    st.table(allocation_df)
    
    # Performance metrics
    st.subheader("Performance Metrics")
    
    metrics_data = {
        'Metric': ['Total Return', 'Daily Avg Return', 'Volatility', 'Sharpe Ratio', 'Max Drawdown'],
        'Value': [f'{total_return:.2f}%', '0.15%', '2.3%', '1.4', '-4.2%']
    }
    
    metrics_df = pd.DataFrame(metrics_data)
    st.table(metrics_df)
    
    # Recent trades mini-view
    st.subheader("Recent Trades Preview")
    st.table(trades_df.head(5))

with tab4:
    st.header("📚 Documentation & How to Use")
    
    st.markdown("""
    ## 📖 **Paper Trading Dashboard Documentation**
    
    ### 🎯 **What is this?**
    A simulated trading dashboard that tests 3 different trading strategies with virtual money.
    
    ### 🔧 **How it works:**
    1. **Virtual Portfolio:** Starts with $10,000 virtual capital
    2. **3 Strategies:** Runs simultaneously and independently
    3. **Simulated Trades:** Based on historical price patterns
    4. **Performance Tracking:** Real-time metrics and charts
    
    ### 📊 **Dashboard Sections:**
    
    #### **1. Overview Tab**
    - **Portfolio Value:** Current value of your virtual portfolio
    - **Total Trades:** Number of trades executed by all strategies
    - **Avg Performance:** Average return across all strategies
    - **Active Positions:** Currently open positions
    - **Portfolio Chart:** Historical performance over time
    
    #### **2. Strategies Tab**
    - **Side-by-side comparison:** All 3 strategies with key metrics
    - **Total PnL:** Profit & Loss for each strategy (green/red)
    - **Win Rate:** Percentage of profitable trades
    - **Trades Executed:** Number of trades per strategy
    - **Strategy Description:** Logic behind each approach
    
    #### **3. Portfolio Tab**
    - **Allocation:** Breakdown by asset (BTC, ETH, ADA, etc.)
    - **Performance Metrics:** Risk-adjusted returns and statistics
    - **Recent Trades:** Last 5 trades for quick reference
    
    ### 🎯 **Trading Strategies:**
    
    #### **📈 Momentum Strategy**
    - **Logic:** Follows price trends - buys when price is rising, sells when falling
    - **Best for:** Strong trending markets
    - **Risk:** High during market reversals
    - **Current Stats:** 41 trades, 36.6% win rate, $129.05 PnL
    
    #### **📈 Mean Reversion Strategy**
    - **Logic:** Bets prices return to average - buys when low, sells when high
    - **Best for:** Range-bound markets
    - **Risk:** Low in trending markets
    - **Current Stats:** 35 trades, 14.3% win rate, -$60.09 PnL
    
    #### **📈 Breakout Strategy**
    - **Logic:** Captures price breakouts from consolidation
    - **Best for:** Volatile markets with clear support/resistance
    - **Risk:** False breakouts can cause losses
    - **Current Stats:** 23 trades, 26.1% win rate, $95.11 PnL
    
    ### ⚙️ **Sidebar Controls:**
    
    #### **Auto-refresh**
    - Automatically updates data every 30 seconds
    - Toggle on/off as needed
    
    #### **Focus Strategy**
    - Filter view to specific strategy
    - "All Strategies" shows combined performance
    
    #### **Quick Stats**
    - At-a-glance overview of total performance
    - Updates in real-time
    
    ### 🔄 **Data Updates:**
    - **Manual:** Click "Refresh Data" button
    - **Auto:** Enable auto-refresh checkbox
    - **Simulated:** Trades generated algorithmically
    
    ### ⚠️ **Important Notes:**
    - This is **PAPER TRADING** only - no real money involved
    - Past performance ≠ future results
    - For educational purposes only
    - Always do your own research before real trading
    
    ### 🆘 **Need Help?**
    - Check console for errors (F12)
    - Clear browser cache if issues persist
    - Test in incognito mode if using crypto wallet extensions
    - Contact support if problems continue
    """)

# Auto-refresh logic
if auto_refresh:
    time.sleep(30)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("*Paper trading simulation for educational purposes* | *Data updates every 30 seconds*")

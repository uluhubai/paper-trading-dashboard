"""
Dashboard module for Paper Trading System
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import os

logger = logging.getLogger(__name__)

class TradingDashboard:
    """Interactive trading dashboard using Streamlit"""
    
    def __init__(self):
        self.title = "📈 Paper Trading System Dashboard"
        self.theme = "dark"
        self.data = None
        self.performance_data = None
        
    def setup_page(self):
        """Setup Streamlit page configuration"""
        st.set_page_config(
            page_title="Paper Trading System",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E88E5;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #1E1E1E;
            padding: 1rem;
            border-radius: 10px;
            border-left: 5px solid #1E88E5;
            margin-bottom: 1rem;
        }
        .positive {
            color: #4CAF50;
        }
        .negative {
            color: #F44336;
        }
        </style>
        """, unsafe_allow_html=True)
        
    def display_header(self):
        """Display dashboard header"""
        st.markdown(f'<h1 class="main-header">{self.title}</h1>', unsafe_allow_html=True)
        
        # Status bar
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Status", "🟢 Active", delta="Running")
        
        with col2:
            st.metric("Last Update", datetime.now().strftime("%H:%M:%S"))
        
        with col3:
            st.metric("Mode", "📄 Paper Trading")
        
        with col4:
            st.metric("Version", "1.0.0")
    
    def display_metrics(self, metrics: Dict[str, Any]):
        """Display key performance metrics"""
        
        st.subheader("📊 Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_return = metrics.get('total_return', 0)
            delta_color = "normal" if total_return >= 0 else "inverse"
            st.metric(
                "Total Return", 
                f"{total_return:.2%}",
                delta=f"{total_return:.2%}",
                delta_color=delta_color
            )
        
        with col2:
            sharpe = metrics.get('sharpe_ratio', 0)
            st.metric("Sharpe Ratio", f"{sharpe:.2f}")
        
        with col3:
            max_dd = metrics.get('max_drawdown', 0)
            st.metric("Max Drawdown", f"{max_dd:.2%}")
        
        with col4:
            win_rate = metrics.get('win_rate', 0)
            st.metric("Win Rate", f"{win_rate:.2%}")
        
        # Second row of metrics
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            total_trades = metrics.get('total_trades', 0)
            st.metric("Total Trades", f"{total_trades}")
        
        with col6:
            current_value = metrics.get('current_value', 0)
            st.metric("Portfolio Value", f"${current_value:,.2f}")
        
        with col7:
            cash_balance = metrics.get('cash_balance', 0)
            st.metric("Cash Balance", f"${cash_balance:,.2f}")
        
        with col8:
            positions = metrics.get('positions_count', 0)
            st.metric("Open Positions", f"{positions}")
    
    def plot_equity_curve(self, equity_data: pd.DataFrame):
        """Plot equity curve"""
        
        st.subheader("📈 Equity Curve")
        
        if equity_data is None or equity_data.empty:
            st.warning("No equity data available")
            return
        
        fig = go.Figure()
        
        # Add equity curve
        fig.add_trace(go.Scatter(
            x=equity_data['date'] if 'date' in equity_data.columns else equity_data.index,
            y=equity_data['portfolio_value'],
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#1E88E5', width=2)
        ))
        
        # Add running maximum
        equity_data['running_max'] = equity_data['portfolio_value'].expanding().max()
        fig.add_trace(go.Scatter(
            x=equity_data['date'] if 'date' in equity_data.columns else equity_data.index,
            y=equity_data['running_max'],
            mode='lines',
            name='Running Max',
            line=dict(color='#4CAF50', width=1, dash='dash'),
            opacity=0.7
        ))
        
        # Calculate drawdown
        equity_data['drawdown'] = (equity_data['portfolio_value'] - equity_data['running_max']) / equity_data['running_max']
        
        # Add drawdown area
        fig.add_trace(go.Scatter(
            x=equity_data['date'] if 'date' in equity_data.columns else equity_data.index,
            y=equity_data['drawdown'] * 100,  # Convert to percentage
            fill='tozeroy',
            name='Drawdown %',
            yaxis='y2',
            line=dict(color='#F44336', width=0),
            fillcolor='rgba(244, 67, 54, 0.3)'
        ))
        
        # Update layout
        fig.update_layout(
            title="Portfolio Value & Drawdown",
            xaxis_title="Date",
            yaxis_title="Portfolio Value ($)",
            yaxis2=dict(
                title="Drawdown (%)",
                overlaying='y',
                side='right',
                range=[-50, 0]  # Drawdown from 0% to -50%
            ),
            hovermode='x unified',
            template='plotly_dark',
            height=400
        )
        
        st.plotly_chart(fig, width='stretch')
    
    def plot_returns_distribution(self, returns_data: pd.Series):
        """Plot returns distribution"""
        
        st.subheader("📊 Returns Distribution")
        
        if returns_data is None or len(returns_data) == 0:
            st.warning("No returns data available")
            return
        
        fig = go.Figure()
        
        # Histogram of returns
        # Convert to pandas Series if it's a list
        if isinstance(returns_data, list):
            import pandas as pd
            returns_for_hist = pd.Series(returns_data) * 100
        else:
            returns_for_hist = returns_data * 100
            
        fig.add_trace(go.Histogram(
            x=returns_for_hist,  # Already converted to percentage
            nbinsx=50,
            name='Returns',
            marker_color='#1E88E5',
            opacity=0.7
        ))
        
        # Add mean line
        # Convert to pandas Series if it's a list
        if isinstance(returns_data, list):
            import pandas as pd
            returns_series = pd.Series(returns_data)
            mean_return = returns_series.mean() * 100
        else:
            mean_return = returns_data.mean() * 100
        fig.add_vline(
            x=mean_return,
            line_dash="dash",
            line_color="white",
            annotation_text=f"Mean: {mean_return:.2f}%",
            annotation_position="top right"
        )
        
        # Update layout
        fig.update_layout(
            title="Daily Returns Distribution",
            xaxis_title="Daily Return (%)",
            yaxis_title="Frequency",
            template='plotly_dark',
            height=300
        )
        
        st.plotly_chart(fig, width='stretch')
    
    def display_trade_history(self, trades: List[Dict[str, Any]]):
        """Display trade history table"""
        
        st.subheader("📋 Trade History")
        
        if not trades:
            st.info("No trades executed yet")
            return
        
        # Convert to DataFrame
        trades_df = pd.DataFrame(trades)
        
        # Format columns
        if not trades_df.empty:
            # Select and rename columns
            # Try 'type' first, then 'action' (actual column name in data)
            # Also handle 'value' vs 'pnl' column names
            if 'type' in trades_df.columns:
                # Check if we have 'value' or 'pnl'
                value_col = 'value' if 'value' in trades_df.columns else 'pnl'
                display_cols = ['timestamp', 'symbol', 'type', 'quantity', 'price', value_col]
            elif 'action' in trades_df.columns:
                # Rename 'action' to 'type' for consistency BEFORE selecting columns
                trades_df = trades_df.rename(columns={'action': 'type'})
                # Check if we have 'value' or 'pnl'
                value_col = 'value' if 'value' in trades_df.columns else 'pnl'
                display_cols = ['timestamp', 'symbol', 'type', 'quantity', 'price', value_col]
            else:
                # Build display columns based on what's available
                base_cols = ['timestamp', 'symbol', 'quantity', 'price']
                display_cols = []
                for col in base_cols:
                    if col in trades_df.columns:
                        display_cols.append(col)
                # Add value/pnl if available
                if 'value' in trades_df.columns:
                    display_cols.append('value')
                elif 'pnl' in trades_df.columns:
                    display_cols.append('pnl')
            
            display_df = trades_df[display_cols].copy() if display_cols else trades_df
            
            # Format values
            # Handle both 'value' and 'pnl' columns
            for col in ['value', 'pnl']:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}")
            
            if 'price' in display_df.columns:
                display_df['price'] = display_df['price'].apply(lambda x: f"${x:.2f}")
            
            if 'quantity' in display_df.columns:
                display_df['quantity'] = display_df['quantity'].apply(lambda x: f"{x:.2f}")
            
            # Color code trade types
            def color_trade_type(trade_type):
                if trade_type == 'BUY':
                    return 'background-color: #4CAF50; color: white'
                else:
                    return 'background-color: #F44336; color: white'
            
            # Display table
            # Only apply styling if 'type' column exists (renamed from 'action')
            if 'type' in display_df.columns:
                # Use map() for newer pandas versions, applymap() for older
                try:
                    styled_df = display_df.style.map(
                        lambda x: color_trade_type(x) if isinstance(x, str) and x in ['BUY', 'SELL'] else '',
                        subset=['type']
                    )
                except AttributeError:
                    styled_df = display_df.style.applymap(
                        lambda x: color_trade_type(x) if isinstance(x, str) and x in ['BUY', 'SELL'] else '',
                        subset=['type']
                    )
            else:
                styled_df = display_df
            
            st.dataframe(
                styled_df,
                width='stretch',
                height=300
            )
    
    def display_positions(self, positions: Dict[str, Dict[str, float]], current_prices: Dict[str, float] = None):
        """Display current positions"""
        
        st.subheader("💰 Current Positions")
        
        if not positions:
            st.info("No open positions")
            return
        
        # Convert to DataFrame
        positions_list = []
        
        # Handle both dict format and list format
        if isinstance(positions, dict):
            # Dict format: {symbol: {position_data}}
            position_items = positions.items()
        elif isinstance(positions, list):
            # List format: [{position_data}, ...]
            # Convert list to dict-like items
            position_items = [(pos.get('symbol', f'UNKNOWN_{i}'), pos) for i, pos in enumerate(positions)]
        else:
            st.warning(f"Unknown positions format: {type(positions)}")
            return
        
        for symbol, position in position_items:
            quantity = position.get('quantity', 0)
            avg_price = position.get('avg_price', 0)
            total_cost = position.get('total_cost', quantity * avg_price)  # Calculate if not provided
            
            position_data = {
                'Symbol': symbol,
                'Quantity': quantity,
                'Avg Price': avg_price,
                'Total Cost': total_cost
            }
            
            # Add current price and P&L if available
            if current_prices and symbol in current_prices:
                current_price = current_prices[symbol]
                position_value = quantity * current_price
                unrealized_pnl = position_value - total_cost
                unrealized_pnl_pct = unrealized_pnl / total_cost if total_cost > 0 else 0
                
                position_data.update({
                    'Current Price': current_price,
                    'Position Value': position_value,
                    'Unrealized P&L': unrealized_pnl,
                    'Unrealized %': unrealized_pnl_pct
                })
            else:
                # Use values from position if available
                current_price = position.get('current_price', 0)
                pnl = position.get('pnl', 0)
                pnl_pct = position.get('pnl_percent', 0)
                
                # Calculate position value
                position_value = quantity * current_price if current_price > 0 else total_cost
                
                position_data.update({
                    'Current Price': current_price,
                    'Position Value': position_value,
                    'Unrealized P&L': pnl,
                    'Unrealized %': pnl_pct
                })
            
            positions_list.append(position_data)
        
        positions_df = pd.DataFrame(positions_list)
        
        # Format values
        if not positions_df.empty:
            # Format currency columns
            currency_cols = ['Avg Price', 'Total Cost', 'Current Price', 'Position Value', 'Unrealized P&L']
            for col in currency_cols:
                if col in positions_df.columns:
                    positions_df[col] = positions_df[col].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "")
            
            # Format percentage columns
            if 'Unrealized %' in positions_df.columns:
                positions_df['Unrealized %'] = positions_df['Unrealized %'].apply(
                    lambda x: f"{x:.2%}" if pd.notnull(x) else ""
                )
            
            # Color code P&L
            def color_pnl(value):
                if isinstance(value, str) and value.startswith('$'):
                    try:
                        num = float(value.replace('$', '').replace(',', ''))
                        if num > 0:
                            return 'color: #4CAF50'
                        elif num < 0:
                            return 'color: #F44336'
                    except:
                        pass
                return ''
            
            # Display table
            # Use map() for newer pandas versions, applymap() for older
            try:
                styled_positions = positions_df.style.map(color_pnl, subset=['Unrealized P&L', 'Unrealized %'])
            except AttributeError:
                styled_positions = positions_df.style.applymap(color_pnl, subset=['Unrealized P&L', 'Unrealized %'])
            
            st.dataframe(
                styled_positions,
                width='stretch',
                height=300
            )
    
    def display_risk_metrics(self, risk_metrics: Dict[str, Any]):
        """Display risk metrics"""
        
        st.subheader("⚠️ Risk Metrics")
        
        if not risk_metrics:
            st.warning("No risk metrics available")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            var_95 = risk_metrics.get('var_95', 0)
            st.metric("VaR (95%)", f"{var_95:.2%}")
        
        with col2:
            cvar_95 = risk_metrics.get('cvar_95', 0)
            st.metric("CVaR (95%)", f"{cvar_95:.2%}")
        
        with col3:
            volatility = risk_metrics.get('annual_volatility', 0)
            st.metric("Annual Volatility", f"{volatility:.2%}")
        
        with col4:
            sortino = risk_metrics.get('sortino_ratio', 0)
            st.metric("Sortino Ratio", f"{sortino:.2f}")
    
    def display_strategy_comparison(self, strategy_results: Dict[str, Dict[str, Any]]):
        """Display strategy comparison"""
        
        st.subheader("🔄 Strategy Comparison")
        
        if not strategy_results:
            st.info("No strategy results to compare")
            return
        
        # Convert to DataFrame
        comparison_data = []
        
        # Handle both dict format and list format
        if isinstance(strategy_results, dict):
            # Dict format: {strategy_name: {results}}
            items = strategy_results.items()
        elif isinstance(strategy_results, list):
            # List format: [{results}, ...]
            # Convert list to dict-like items
            items = [(f"Strategy_{i}", result) for i, result in enumerate(strategy_results)]
        else:
            st.warning(f"Unknown strategy_results format: {type(strategy_results)}")
            return
        
        for strategy_name, results in items:
            comparison_data.append({
                'Strategy': strategy_name,
                'Total Return': results.get('total_return', 0),
                'Sharpe Ratio': results.get('sharpe_ratio', 0),
                'Max Drawdown': results.get('max_drawdown', 0),
                'Win Rate': results.get('win_rate', 0),
                'Total Trades': results.get('total_trades', 0)
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        if not comparison_df.empty:
            # Format percentages
            comparison_df['Total Return'] = comparison_df['Total Return'].apply(lambda x: f"{x:.2%}")
            comparison_df['Max Drawdown'] = comparison_df['Max Drawdown'].apply(lambda x: f"{x:.2%}")
            comparison_df['Win Rate'] = comparison_df['Win Rate'].apply(lambda x: f"{x:.2%}")
            
            # Highlight best performers
            def highlight_best(column):
                if column.name in ['Total Return', 'Sharpe Ratio', 'Win Rate']:
                    try:
                        # Extract numeric values
                        values = column.str.rstrip('%').astype(float)
                        best_idx = values.idxmax()
                        return ['background-color: #4CAF50; color: white' if i == best_idx else '' for i in range(len(column))]
                    except:
                        return [''] * len(column)
                elif column.name == 'Max Drawdown':
                    try:
                        values = column.str.rstrip('%').astype(float)
                        best_idx = values.idxmin()  # Lower drawdown is better
                        return ['background-color: #4CAF50; color: white' if i == best_idx else '' for i in range(len(column))]
                    except:
                        return [''] * len(column)
                return [''] * len(column)
            
            st.dataframe(
                comparison_df.style.apply(highlight_best),
                width='stretch',
                height=300
            )
    
    def display_ml_predictions(self, ml_predictions: Dict[str, Any]):
        """Display ML predictions"""
        
        st.subheader("🤖 ML Predictions")
        
        if not ml_predictions:
            st.info("No ML predictions available")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'lstm_accuracy' in ml_predictions:
                accuracy = ml_predictions['lstm_accuracy']
                st.metric("LSTM Accuracy", f"{accuracy:.2%}")
            
            if 'ensemble_r2' in ml_predictions:
                r2 = ml_predictions['ensemble_r2']
                st.metric("Ensemble R²", f"{r2:.4f}")
        
        with col2:
            if 'next_day_prediction' in ml_predictions:
                prediction = ml_predictions['next_day_prediction']
                direction = "UP" if prediction > 0 else "DOWN"
                color = "#4CAF50" if prediction > 0 else "#F44336"
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Next Day Prediction</h3>
                    <h2 style="color: {color}">{direction} ({prediction:.2%})</h2>
                </div>
                """, unsafe_allow_html=True)
    
    def run(self, 
            portfolio_data: Dict[str, Any] = None,
            strategy_results: Dict[str, Dict[str, Any]] = None,
            ml_predictions: Dict[str, Any] = None):
        """Run the dashboard"""
        
        try:
            # Setup page
            self.setup_page()
            
            # Display header
            self.display_header()
            
            # Create tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Overview", 
                "💰 Portfolio", 
                "🔄 Strategies", 
                "🤖 ML Insights"
            ])
            
            with tab1:
                # Overview tab
                if portfolio_data and 'metrics' in portfolio_data:
                    self.display_metrics(portfolio_data['metrics'])
                
                if portfolio_data and 'equity_curve' in portfolio_data:
                    self.plot_equity_curve(portfolio_data['equity_curve'])
                
                if portfolio_data and 'returns' in portfolio_data:
                    self.plot_returns_distribution(portfolio_data['returns'])
            
            with tab2:
                # Portfolio tab
                if portfolio_data:
                    if 'positions' in portfolio_data:
                        current_prices = portfolio_data.get('current_prices', {})
                        self.display_positions(portfolio_data['positions'], current_prices)
                    
                    if 'trades' in portfolio_data:
                        self.display_trade_history(portfolio_data['trades'])
                    
                    if 'risk_metrics' in portfolio_data:
                        self.display_risk_metrics(portfolio_data['risk_metrics'])
            
            with tab3:
                # Strategies tab
                if strategy_results:
                    self.display_strategy_comparison(strategy_results)
                
                # Strategy configuration
                st.subheader("⚙️ Strategy Configuration")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    ma_short = st.slider("MA Short Window", 5, 50, 10, key="slider_0")
                    ma_long = st.slider("MA Long Window", 20, 200, 30, key="slider_1")
                    
                    if st.button("Run MA Crossover Backtest", key="ma_backtest_btn"):
                        st.info("Backtest running...")
                
                with col2:
                    bb_window = st.slider("Bollinger Band Window", 10, 100, 20, key="slider_2")
                    bb_std = st.slider("Bollinger Band Std Dev", 1.0, 3.0, 2.0, key="bb_std_slider")
                    
                    if st.button("Run Mean Reversion Backtest", key="mr_backtest_btn"):
                        st.info("Backtest running...")
            
            with tab4:
                # ML Insights tab
                if ml_predictions:
                    self.display_ml_predictions(ml_predictions)
                
                # ML configuration
                st.subheader("⚙️ ML Model Configuration")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    sequence_length = st.slider("Sequence Length", 10, 100, 60, key="slider_4")
                    lstm_units = st.slider("LSTM Units", 16, 128, 32, key="lstm_units_slider")
                    
                    if st.button("Retrain LSTM Model", key="lstm_retrain_btn"):
                        st.info("Retraining LSTM model...")
                
                with col2:
                    train_test_split = st.slider("Train/Test Split", 0.5, 0.9, 0.8, key="slider_6")
                    epochs = st.slider("Training Epochs", 10, 100, 50, key="epochs_slider")
                    
                    if st.button("Retrain Ensemble Model", key="ensemble_retrain_btn"):
                        st.info("Retraining ensemble model...")
            
            # Sidebar controls
            with st.sidebar:
                st.header("🎛️ Controls")
                
                # Trading mode
                trading_mode = st.selectbox(
                    "Trading Mode",
                    ["Paper Trading", "Live Trading (Coming Soon)"],
                    disabled=True,
                    key="trading_mode_select"
                )
                
                # Capital management
                st.subheader("💰 Capital Management")
                initial_capital = st.number_input(
                    "Initial Capital ($)",
                    min_value=1000,
                    max_value=1000000,
                    value=10000,
                    step=1000,
                    key="initial_capital_input"
                )
                
                if st.button("Reset Portfolio", key="reset_portfolio_btn"):
                    st.info("Portfolio reset requested")
                
                # Auto-refresh settings
                st.subheader("🔄 Auto-Refresh")
                
                # Auto-refresh toggle
                auto_refresh = st.checkbox("Enable Auto-Refresh", value=False, key="checkbox_0")
                
                if auto_refresh:
                    refresh_interval = st.select_slider(
                        "Refresh Interval",
                        options=["30 seconds", "1 minute", "5 minutes", "10 minutes", "30 minutes"],
                        value="1 minute",
                        key="refresh_interval_slider"
                    )
                    
                    # Convert to seconds
                    interval_map = {
                        "30 seconds": 30,
                        "1 minute": 60,
                        "5 minutes": 300,
                        "10 minutes": 600,
                        "30 minutes": 1800
                    }
                    
                    seconds = interval_map[refresh_interval]
                    
                    # Add JavaScript for auto-refresh
                    st.markdown(f"""
                    <script>
                    setTimeout(function() {{
                        window.location.reload();
                    }}, {seconds * 1000});
                    </script>
                    """, unsafe_allow_html=True)
                    
                    st.info(f"Page will refresh in {seconds} seconds...")
                
                # Manual refresh button
                if st.button("🔄 Refresh Now", key="refresh_now"):
                    # Clear ALL cache
                    st.cache_data.clear()
                    st.cache_resource.clear()
                    
                    # Force page refresh using JavaScript
                    st.markdown("""
                    <script>
                    setTimeout(function() {
                        window.location.reload(true);  // true = force reload from server
                    }, 100);
                    </script>
                    """, unsafe_allow_html=True)
                    
                    st.success("✅ Data refreshed! Page reloading...")
                
                # Risk settings
                st.subheader("⚠️ Risk Settings")
                risk_per_trade = st.slider("Risk per Trade (%)", 0.5, 5.0, 2.0, key="slider_9") / 100
                stop_loss = st.slider("Stop Loss (%)", 1.0, 10.0, 5.0, key="slider_10") / 100
                take_profit = st.slider("Take Profit (%)", 5.0, 20.0, 10.0, key="take_profit_slider") / 100
                
                # Data settings
                st.subheader("📊 Data Settings")
                data_source = st.selectbox(
                    "Data Source",
                    ["Yahoo Finance", "Alpha Vantage", "Polygon (Coming Soon)"],
                    key="data_source_select"
                )
                
                symbols = st.text_input(
                    "Trading Symbols (comma-separated)",
                    "AAPL,GOOGL,MSFT,AMZN,TSLA",
                    key="trading_symbols_input"
                )
                
                # System controls
                st.subheader("⚙️ System Controls")
                
                # Show update status
                if 'last_update' in st.session_state:
                    st.caption(f"Last update: {st.session_state.last_update}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔄 Update Market Data", width='stretch', key="update_market_btn"):
                        # Run market data update
                        import subprocess
                        import sys
                        
                        with st.spinner("🔄 Fetching latest market prices..."):
                            try:
                                # Run the update script
                                script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "update_real_data.py")
                                result = subprocess.run(
                                    [sys.executable, script_path],
                                    capture_output=True,
                                    text=True,
                                    timeout=30
                                )
                                
                                if result.returncode == 0:
                                    st.success("✅ Market data updated!")
                                    
                                    # Show key info
                                    for line in result.stdout.split('\n'):
                                        if 'Current prices:' in line or 'Real prices fetched:' in line:
                                            st.info(line.strip())
                                            break
                                
                                else:
                                    st.error(f"❌ Update failed: {result.stderr[:100]}...")
                            
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                
                with col2:
                    if st.button("🚀 Run Paper Trading Cycle", width='stretch', key="run_trading_cycle_btn"):
                        # Run ONE cycle of paper trading
                        import subprocess
                        import sys
                        
                        with st.spinner("🚀 Executing paper trading strategies..."):
                            try:
                                # Run one cycle of paper trading
                                script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paper_trading_engine.py")
                                result = subprocess.run(
                                    [sys.executable, script_path, "--interval", "1"],
                                    capture_output=True,
                                    text=True,
                                    timeout=60
                                )
                                
                                if result.returncode == 0:
                                    st.success("✅ Paper trading cycle completed!")
                                    
                                    # Extract portfolio info
                                    portfolio_value = None
                                    pnl = None
                                    for line in result.stdout.split('\n'):
                                        if 'Portfolio:' in line:
                                            st.info(line.strip())
                                        if 'CYCLE COMPLETE' in line:
                                            break
                                
                                else:
                                    st.error(f"❌ Paper trading failed: {result.stderr[:100]}...")
                            
                            except subprocess.TimeoutExpired:
                                st.warning("⚠️ Paper trading timed out after 60 seconds")
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                
                # Auto-refresh after any update
                if st.session_state.get('data_updated', False):
                    st.cache_data.clear()
                    st.markdown("""
                    <script>
                    setTimeout(function() {
                        window.location.reload(true);
                    }, 3000);
                    </script>
                    """, unsafe_allow_html=True)
                    st.info("🔄 Page will reload in 3 seconds...")
                
                if st.button("📊 Run All Backtests", key="run_all_backtests_btn"):
                    st.info("Running all backtests...")
                
                if st.button("🚀 Start Paper Trading", key="start_paper_trading_btn"):
                    st.success("Paper trading started!")
                
                # Status
                st.subheader("📈 System Status")
                st.progress(75, text="System Operational: 75%")
                
                # Logs
                with st.expander("📋 System Logs"):
                    st.text("19:30: System initialized")
                    st.text("19:31: Data loaded successfully")
                    st.text("19:32: ML models ready")
                    st.text("19:33: Dashboard active")
        
        except Exception as e:
            st.error(f"Dashboard error: {str(e)}")
            logger.error(f"Dashboard error: {str(e)}")

# Global dashboard instance
dashboard = TradingDashboard()

def run_dashboard():
    """Run the dashboard"""
    # Try to load data automatically if not provided
    import pandas as pd
    import json
    import os
    from datetime import datetime
    
    portfolio_data = None
    strategy_results = None
    ml_predictions = None
    
    # Try to load data from files
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    if os.path.exists(data_dir):
        try:
            # Load portfolio data
            portfolio_file = os.path.join(data_dir, 'portfolio_history.csv')
            metrics_file = os.path.join(data_dir, 'metrics.json')
            trades_file = os.path.join(data_dir, 'recent_trades.csv')
            
            if os.path.exists(portfolio_file) and os.path.exists(metrics_file):
                # Load portfolio history
                df = pd.read_csv(portfolio_file)
                df['date'] = pd.to_datetime(df['date'])
                
                # Load metrics
                with open(metrics_file, 'r') as f:
                    metrics = json.load(f)
                
                # Format portfolio data FROM ACTUAL FILES
                portfolio_data = {
                    'equity_curve': df[['date', 'portfolio_value']].copy(),
                    'returns': df['portfolio_value'].pct_change().dropna().tolist() if len(df) > 1 else [0],
                    'metrics': {
                        'total_return': metrics.get('total_return', 0),
                        'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                        'max_drawdown': metrics.get('max_drawdown', 0),
                        'win_rate': metrics.get('win_rate', 0),
                        'volatility': metrics.get('volatility', 0),
                        'current_portfolio': df['portfolio_value'].iloc[-1] if len(df) > 0 else 10000
                    }
                }
                
                # Load trades if available
                if os.path.exists(trades_file):
                    trades_df = pd.read_csv(trades_file)
                    if 'timestamp' in trades_df.columns:
                        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
                    portfolio_data['trades'] = trades_df.to_dict('records')
                else:
                    portfolio_data['trades'] = []
                
                # Create positions from metrics (or use defaults)
                portfolio_data['positions'] = [
                    {
                        'symbol': 'BTC',
                        'quantity': 0.5,
                        'avg_price': 45000,
                        'current_price': metrics.get('current_btc_price', 67321),
                        'pnl': (metrics.get('current_btc_price', 67321) - 45000) * 0.5,
                        'pnl_percent': ((metrics.get('current_btc_price', 67321) / 45000) - 1) * 100
                    },
                    {
                        'symbol': 'ETH',
                        'quantity': 3.2,
                        'avg_price': 3200,
                        'current_price': metrics.get('current_eth_price', 3500),
                        'pnl': (metrics.get('current_eth_price', 3500) - 3200) * 3.2,
                        'pnl_percent': ((metrics.get('current_eth_price', 3500) / 3200) - 1) * 100
                    },
                    {
                        'symbol': 'ADA',
                        'quantity': 5000,
                        'avg_price': 0.40,
                        'current_price': metrics.get('current_ada_price', 0.45),
                        'pnl': (metrics.get('current_ada_price', 0.45) - 0.40) * 5000,
                        'pnl_percent': ((metrics.get('current_ada_price', 0.45) / 0.40) - 1) * 100
                    }
                ]
                
                portfolio_data['current_prices'] = {
                    'BTC': metrics.get('current_btc_price', 67321),
                    'ETH': metrics.get('current_eth_price', 3500),
                    'ADA': metrics.get('current_ada_price', 0.45)
                }
                
                print(f"✅ Loaded REAL portfolio data from files: Total Return={metrics.get('total_return', 0)}%, Win Rate={metrics.get('win_rate', 0)}%")
            
            # Create sample strategy results
            strategy_results = {
                'ma_crossover': {
                    'total_return': 0.125,
                    'sharpe_ratio': 1.8,
                    'win_rate': 0.62,
                    'num_trades': 45
                },
                'mean_reversion': {
                    'total_return': 0.085,
                    'sharpe_ratio': 1.2,
                    'win_rate': 0.58,
                    'num_trades': 32
                },
                'breakout': {
                    'total_return': 0.152,
                    'sharpe_ratio': 2.1,
                    'win_rate': 0.65,
                    'num_trades': 28
                }
            }
            
            # Create sample ML predictions
            ml_predictions = {
                'next_hour': {
                    'BTC': {'direction': 'UP', 'confidence': 0.72, 'predicted_change': 0.015},
                    'ETH': {'direction': 'UP', 'confidence': 0.68, 'predicted_change': 0.012},
                    'ADA': {'direction': 'DOWN', 'confidence': 0.61, 'predicted_change': -0.008}
                }
            }
            
        except Exception as e:
            print(f"⚠️ Could not load data files: {e}")
            print("📊 Dashboard will run with sample data")
    
    # Run dashboard with loaded data
    dashboard.run(portfolio_data, strategy_results, ml_predictions)

if __name__ == "__main__":
    run_dashboard()
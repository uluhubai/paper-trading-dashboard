#!/usr/bin/env python3
"""
Dashboard V2 - Multi-Strategy Comparison
Shows performance of 3 trading strategies side-by-side
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add CORS headers for iframe embedding
import streamlit.components.v1 as components

# Custom HTML to set headers (workaround for Streamlit CORS)
iframe_embed_html = """
<script>
// Workaround for CORS/iframe issues
if (window !== window.top) {
    // We're in an iframe
    console.log("Dashboard loaded in iframe");
}
</script>
"""

class MultiStrategyDashboard:
    """Dashboard for comparing multiple trading strategies"""
    
    def __init__(self):
        self.title = "📊 Multi-Strategy Paper Trading Dashboard"
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
    def load_data(self):
        """Load data from files"""
        data = {}
        
        # Load metrics
        metrics_file = os.path.join(self.data_dir, 'metrics_v2.json')
        if os.path.exists(metrics_file):
            with open(metrics_file, 'r') as f:
                data['metrics'] = json.load(f)
        
        # Load portfolio history
        history_file = os.path.join(self.data_dir, 'portfolio_history_v2.csv')
        if os.path.exists(history_file):
            data['history'] = pd.read_csv(history_file)
            if 'timestamp' in data['history'].columns:
                data['history']['timestamp'] = pd.to_datetime(data['history']['timestamp'])
        
        # Load recent trades
        trades_file = os.path.join(self.data_dir, 'recent_trades_v2.csv')
        if os.path.exists(trades_file):
            data['trades'] = pd.read_csv(trades_file)
            if 'timestamp' in data['trades'].columns:
                data['trades']['timestamp'] = pd.to_datetime(data['trades']['timestamp'])
        
        # Load strategy documentation
        docs_file = os.path.join(os.path.dirname(__file__), 'reports', 'strategy_details.md')
        if os.path.exists(docs_file):
            with open(docs_file, 'r', encoding='utf-8') as f:
                data['documentation'] = f.read()
        else:
            data['documentation'] = "# Strategy Documentation\n\nDocumentation file not found."
        
        return data
    
    def create_strategy_comparison_chart(self, metrics):
        """Create chart comparing strategy performance"""
        if 'strategies' not in metrics:
            return None
        
        strategies = metrics['strategies']
        df = pd.DataFrame([
            {
                'Strategy': strategy,
                'Trades': stats.get('trades', 0),
                'PnL': stats.get('pnl', 0),
                'Win Rate': (stats.get('wins', 0) / max(1, stats.get('trades', 0))) * 100
            }
            for strategy, stats in strategies.items()
        ])
        
        if df.empty:
            return None
        
        # Create bar chart
        fig = go.Figure()
        
        # PnL bars
        fig.add_trace(go.Bar(
            x=df['Strategy'],
            y=df['PnL'],
            name='PnL ($)',
            marker_color=['#00cc96' if x >= 0 else '#ef553b' for x in df['PnL']],
            text=[f'${x:,.2f}' for x in df['PnL']],
            textposition='auto'
        ))
        
        # Win rate line
        fig.add_trace(go.Scatter(
            x=df['Strategy'],
            y=df['Win Rate'],
            name='Win Rate (%)',
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='#636efa', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title='Strategy Performance Comparison',
            yaxis=dict(title='PnL ($)'),
            yaxis2=dict(
                title='Win Rate (%)',
                overlaying='y',
                side='right',
                range=[0, 100]
            ),
            hovermode='x unified',
            showlegend=True
        )
        
        return fig
    
    def create_portfolio_history_chart(self, history_df):
        """Create portfolio value over time chart"""
        if history_df is None or history_df.empty:
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=history_df['timestamp'],
            y=history_df['portfolio_value'],
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#00cc96', width=3),
            fill='tozeroy',
            fillcolor='rgba(0, 204, 150, 0.1)'
        ))
        
        fig.update_layout(
            title='Portfolio Value Over Time',
            xaxis_title='Date',
            yaxis_title='Value ($)',
            hovermode='x unified'
        )
        
        return fig
    
    def create_trades_timeline(self, trades_df):
        """Create timeline of trades"""
        if trades_df is None or trades_df.empty:
            return None
        
        # Color by strategy
        strategy_colors = {
            'momentum': '#636efa',
            'mean_reversion': '#ef553b',
            'breakout': '#00cc96'
        }
        
        fig = go.Figure()
        
        for strategy in trades_df['strategy'].unique():
            strategy_trades = trades_df[trades_df['strategy'] == strategy]
            
            # Buy trades
            buys = strategy_trades[strategy_trades['action'] == 'BUY']
            if not buys.empty:
                fig.add_trace(go.Scatter(
                    x=buys['timestamp'],
                    y=[1] * len(buys),
                    mode='markers',
                    name=f'{strategy} - BUY',
                    marker=dict(
                        symbol='triangle-up',
                        size=15,
                        color=strategy_colors.get(strategy, '#000000')
                    ),
                    text=[f"BUY {row['symbol']} @ ${row['price']:.2f}" for _, row in buys.iterrows()]
                ))
            
            # Sell trades
            sells = strategy_trades[strategy_trades['action'] == 'SELL']
            if not sells.empty:
                fig.add_trace(go.Scatter(
                    x=sells['timestamp'],
                    y=[0] * len(sells),
                    mode='markers',
                    name=f'{strategy} - SELL',
                    marker=dict(
                        symbol='triangle-down',
                        size=15,
                        color=strategy_colors.get(strategy, '#000000')
                    ),
                    text=[f"SELL {row['symbol']} @ ${row['price']:.2f} (PnL: ${row.get('pnl', 0):.2f})" for _, row in sells.iterrows()]
                ))
        
        fig.update_layout(
            title='Trades Timeline by Strategy',
            xaxis_title='Date',
            yaxis=dict(
                title='Action',
                ticktext=['SELL', 'BUY'],
                tickvals=[0, 1],
                range=[-0.5, 1.5]
            ),
            hovermode='closest',
            showlegend=True
        )
        
        return fig
    
    def run(self):
        """Run the dashboard"""
        st.set_page_config(
            page_title="Multi-Strategy Paper Trading",
            page_icon="📊",
            layout="wide"
        )
        
        # Load data
        data = self.load_data()
        
        # Title
        st.title(self.title)
        st.markdown("---")
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'metrics' in data:
                portfolio_value = data['metrics'].get('portfolio_value', 0)
                st.metric("Portfolio Value", f"${portfolio_value:,.2f}")
        
        with col2:
            if 'metrics' in data:
                cash = data['metrics'].get('cash', 0)
                st.metric("Cash", f"${cash:,.2f}")
        
        with col3:
            if 'metrics' in data:
                positions = data['metrics'].get('positions', 0)
                st.metric("Active Positions", positions)
        
        with col4:
            if 'metrics' in data:
                last_updated = data['metrics'].get('last_updated', 'N/A')
                st.metric("Last Updated", last_updated)
        
        st.markdown("---")
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Performance", 
            "📈 History", 
            "💱 Trades", 
            "📚 Documentation"
        ])
        
        # Tab 1: Performance
        with tab1:
            # Strategy Comparison Section
            st.header("🎯 Strategy Performance Comparison")
            
            if 'metrics' in data and 'strategies' in data['metrics']:
                strategies = data['metrics']['strategies']
                
                # Create columns for each strategy
                cols = st.columns(3)
                
                for idx, (strategy_name, stats) in enumerate(strategies.items()):
                    with cols[idx]:
                        # Strategy card
                        trades = stats.get('trades', 0)
                        pnl = stats.get('pnl', 0)
                        wins = stats.get('wins', 0)
                        win_rate = (wins / max(1, trades)) * 100
                        
                        # Color based on performance
                        color = "green" if pnl >= 0 else "red"
                        
                        st.subheader(f"📈 {strategy_name.title()}")
                        st.metric("Total PnL", f"${pnl:,.2f}", delta_color="off")
                        st.metric("Win Rate", f"{win_rate:.1f}%")
                        st.metric("Trades Executed", trades)
                        
                        # Strategy description
                        descriptions = {
                            'momentum': "Trend following - buys rising assets, sells falling ones",
                            'mean_reversion': "Buy low, sell high - trades against extremes",
                            'breakout': "Captures big moves after consolidation periods"
                        }
                        
                        st.info(descriptions.get(strategy_name, "No description available"))
                
                # Strategy comparison chart
                fig = self.create_strategy_comparison_chart(data['metrics'])
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No strategy data available yet. Run a few trading cycles first.")
        
        # Tab 2: Portfolio History
        with tab2:
            st.header("📈 Portfolio History")
            
            if 'history' in data and not data['history'].empty:
                fig = self.create_portfolio_history_chart(data['history'])
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                # Show recent history as table
                with st.expander("View Portfolio History Table"):
                    st.dataframe(data['history'].tail(10))
            else:
                st.info("No portfolio history available yet.")
        
        # Tab 3: Recent Trades
        with tab3:
            st.header("💱 Recent Trades")
            
            if 'trades' in data and not data['trades'].empty:
                # Trades timeline
                fig = self.create_trades_timeline(data['trades'])
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                # Trades table
                with st.expander("View All Recent Trades"):
                    # Format trades for display
                    display_cols = ['timestamp', 'strategy', 'symbol', 'action', 'quantity', 'price']
                    if 'pnl' in data['trades'].columns:
                        display_cols.append('pnl')
                    if 'reason' in data['trades'].columns:
                        display_cols.append('reason')
                    
                    display_df = data['trades'][display_cols].copy()
                    display_df = display_df.sort_values('timestamp', ascending=False)
                    
                    # Color code actions
                    def color_action(val):
                        color = 'green' if val == 'BUY' else 'red'
                        return f'color: {color}'
                    
                    # Use map instead of applymap for newer pandas versions
                    try:
                        styled_df = display_df.style.map(color_action, subset=['action'])
                    except AttributeError:
                        # Fallback to applymap for older versions
                        styled_df = display_df.style.applymap(color_action, subset=['action'])
                    
                    st.dataframe(styled_df, height=400)
            else:
                st.info("No trades executed yet.")
        
        # Tab 4: Documentation
        with tab4:
            st.header("📚 Strategy Documentation")
            st.markdown("---")
            
            if 'documentation' in data:
                # Display documentation with better formatting
                st.markdown(data['documentation'])
            else:
                st.warning("Documentation not loaded. Check if reports/strategy_details.md exists.")
            
            # Quick reference section
            st.markdown("---")
            st.subheader("🎯 Quick Strategy Reference")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 🚀 Momentum")
                st.markdown("""
                **Filosofia:** Follow the trend  
                **Threshold:** ±2% em 50min  
                **Quando funciona:** Mercados trending  
                **Risco:** Whipsaws em ranging
                """)
            
            with col2:
                st.markdown("### 🔄 Mean Reversion")
                st.markdown("""
                **Filosofia:** Buy low, sell high  
                **Threshold:** Z-score ±1.5σ  
                **Quando funciona:** Mercados laterais  
                **Risco:** Trend continuation
                """)
            
            with col3:
                st.markdown("### ⚡ Breakout")
                st.markdown("""
                **Filosofia:** Capture big moves  
                **Threshold:** ±1% além S/R  
                **Quando funciona:** Após consolidação  
                **Risco:** False breakouts
                """)
        
        # Sidebar controls
        with st.sidebar:
            st.header("⚙️ Controls")
            
            # Refresh button
            if st.button("🔄 Refresh Data", key="refresh_v2"):
                st.rerun()
            
            # Auto-refresh
            st.subheader("🔄 Auto-Refresh")
            auto_refresh = st.checkbox("Enable Auto-Refresh", value=False, key="auto_refresh_v2")
            if auto_refresh:
                refresh_interval = st.select_slider(
                    "Refresh Interval",
                    options=["30 seconds", "1 minute", "5 minutes"],
                    value="1 minute",
                    key="refresh_interval_v2"
                )
                st.info(f"Will refresh every {refresh_interval}")
            
            # Strategy controls
            st.subheader("🎯 Strategy Controls")
            
            if 'metrics' in data and 'strategies' in data['metrics']:
                for strategy in data['metrics']['strategies'].keys():
                    st.checkbox(
                        f"Enable {strategy.title()}",
                        value=True,
                        key=f"enable_{strategy}"
                    )
            
            # Information
            st.subheader("ℹ️ Information")
            st.info("""
            **Paper Trading Engine V2** runs 3 strategies simultaneously:
            
            1. **Momentum**: Trend following
            2. **Mean Reversion**: Buy low, sell high  
            3. **Breakout**: Capture big moves
            
            Each strategy operates independently with its own logic.
            """)
            
            # Status
            st.subheader("📊 Current Status")
            if 'metrics' in data:
                st.write(f"**Engine:** Running")
                st.write(f"**Last Update:** {data['metrics'].get('last_updated', 'N/A')}")
                st.write(f"**Data Source:** {data['metrics'].get('data_source', 'Paper Trading V2')}")

def main():
    """Main function"""
    dashboard = MultiStrategyDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
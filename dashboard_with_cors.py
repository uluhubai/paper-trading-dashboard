#!/usr/bin/env python3
"""
Dashboard V2 com CORS headers para iframe embedding
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

# Import the original dashboard class
from dashboard_v2 import MultiStrategyDashboard

class MultiStrategyDashboardWithCORS(MultiStrategyDashboard):
    """Extend dashboard with CORS support"""
    
    def run(self):
        """Run dashboard with CORS headers"""
        # Set page config
        st.set_page_config(
            page_title="Multi-Strategy Paper Trading",
            page_icon="📊",
            layout="wide"
        )
        
        # Add CORS headers via HTML injection
        st.markdown("""
        <script>
        // Workaround for iframe embedding
        if (window.self !== window.top) {
            console.log("Running in iframe - CORS workaround active");
        }
        </script>
        """, unsafe_allow_html=True)
        
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
            if st.button("🔄 Refresh Data", key="refresh_v2_cors"):
                st.rerun()
            
            # Auto-refresh
            st.subheader("🔄 Auto-Refresh")
            auto_refresh = st.checkbox("Enable Auto-Refresh", value=False, key="auto_refresh_v2_cors")
            if auto_refresh:
                refresh_interval = st.select_slider(
                    "Refresh Interval",
                    options=["30 seconds", "1 minute", "5 minutes"],
                    value="1 minute",
                    key="refresh_interval_v2_cors"
                )
                st.info(f"Will refresh every {refresh_interval}")
            
            # Strategy controls
            st.subheader("🎯 Strategy Controls")
            
            if 'metrics' in data and 'strategies' in data['metrics']:
                for strategy in data['metrics']['strategies'].keys():
                    st.checkbox(
                        f"Enable {strategy.title()}",
                        value=True,
                        key=f"enable_{strategy}_cors"
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
    dashboard = MultiStrategyDashboardWithCORS()
    dashboard.run()

if __name__ == "__main__":
    main()
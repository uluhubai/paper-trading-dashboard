"""
Paper Trading Dashboard - Streamlit Cloud Deployment
Main entry point for Streamlit Cloud
"""

import streamlit as st
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set page config
st.set_page_config(
    page_title="Paper Trading Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Import and run the main dashboard
try:
    # Try to import dashboard_v2
    from dashboard_v2 import main as dashboard_main
    
    st.markdown("""
    <style>
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
    </style>
    
    <div class="main-header">📊 Paper Trading Dashboard</div>
    """, unsafe_allow_html=True)
    
    # Run the dashboard
    dashboard_main()
    
except Exception as e:
    st.error(f"Error loading dashboard: {str(e)}")
    st.info("Trying alternative import...")
    
    # Fallback to basic dashboard
    try:
        import dashboard
        dashboard.main()
    except:
        st.error("Could not load any dashboard. Please check the deployment.")
        st.code(f"Error details: {str(e)}", language="python")
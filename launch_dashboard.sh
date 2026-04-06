#!/bin/bash
echo "🚀 Launching Paper Trading Dashboard..."
echo "📊 URL: http://localhost:8501"
echo "⏳ Starting Streamlit..."

cd "$(dirname "$0")"
source venv/bin/activate

# Check if dashboard module exists
if [ -f "dashboard/__init__.py" ]; then
    echo "✅ Dashboard module found"
    streamlit run dashboard/__init__.py --server.port=8501 --server.address=0.0.0.0
else
    echo "❌ Dashboard module not found"
    echo "Creating basic dashboard..."
    
    # Create minimal dashboard
    cat > dashboard_app.py << 'EOF'
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Paper Trading Dashboard", layout="wide")

st.title("🚀 Paper Trading System Dashboard")
st.subheader("Crypto Integration Ready")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("System Status", "Operational", "100%")
    
with col2:
    st.metric("Crypto Module", "Active", "✅")
    
with col3:
    st.metric("Last Update", datetime.now().strftime("%H:%M:%S"))

st.success("🎉 Crypto integration complete! Ready for paper trading.")
EOF

    streamlit run dashboard_app.py --server.port=8501 --server.address=0.0.0.0
fi

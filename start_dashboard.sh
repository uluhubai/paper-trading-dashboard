#!/bin/bash
# Start Streamlit Dashboard on Tailscale network

cd /mnt/sovereign/openclaw-instances/assist/.openclaw/workspace/paper_trading_system

# Activate virtual environment
source venv/bin/activate

# Kill any existing Streamlit process
pkill -f "streamlit" 2>/dev/null

# Start Streamlit on all interfaces (for Tailscale access)
echo "🚀 Starting Paper Trading Dashboard..."
echo "📡 Access URL: http://$(hostname -I | awk '{print $1}'):8501"
echo "🔗 Tailscale URL: http://100.92.200.109:8501 (if port forwarded)"

# Run Streamlit with external access
streamlit run dashboard/__init__.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.headless true \
  --browser.serverAddress 100.92.200.109 \
  --browser.gatherUsageStats false \
  --theme.base dark \
  --theme.primaryColor "#00ff88" \
  --theme.backgroundColor "#0e1117" \
  --theme.secondaryBackgroundColor "#262730" \
  --theme.textColor "#fafafa" \
  --theme.font "sans serif"
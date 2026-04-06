#!/bin/bash
# Start Streamlit in background without systemd/sudo

echo "🚀 STARTING PAPER TRADING DASHBOARD (BACKGROUND)"
echo "=================================================="

# Kill any existing Streamlit process
pkill -f "streamlit.*8501" 2>/dev/null && echo "🔄 Stopped previous instance"

# Create logs directory
mkdir -p /mnt/sovereign/openclaw-instances/assist/.openclaw/workspace/paper_trading_system/logs

# Start Streamlit in background
cd /mnt/sovereign/openclaw-instances/assist/.openclaw/workspace/paper_trading_system
source venv/bin/activate

nohup streamlit run dashboard/__init__.py \
  --server.port=8501 \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.serverAddress=100.92.200.109 \
  --browser.gatherUsageStats=false \
  --theme.base=dark \
  --theme.primaryColor="#00ff88" \
  --theme.backgroundColor="#0e1117" \
  --theme.secondaryBackgroundColor="#262730" \
  --theme.textColor="#fafafa" \
  --theme.font="sans serif" \
  > logs/streamlit.log 2>&1 &

PID=$!
echo $PID > logs/streamlit.pid

echo "✅ Dashboard started with PID: $PID"
echo "📝 Logs: /mnt/sovereign/openclaw-instances/assist/.openclaw/workspace/paper_trading_system/logs/streamlit.log"

# Wait a bit and check if it's running
sleep 3

if ps -p $PID > /dev/null; then
    echo "🎉 DASHBOARD IS RUNNING!"
    echo ""
    echo "🌐 ACCESS URLs:"
    echo "   - Direct: http://100.92.200.109:8501"
    echo "   - WordPress: http://100.92.200.109:8080/paper-trading-dashboard/"
    echo ""
    echo "🔧 MANAGEMENT:"
    echo "   Stop: pkill -f 'streamlit.*8501'"
    echo "   Restart: Run this script again"
    echo "   Logs: tail -f logs/streamlit.log"
    echo ""
    echo "✅ Dashboard will run until server restart"
else
    echo "❌ Dashboard failed to start"
    echo "Check logs: tail -n 50 logs/streamlit.log"
fi
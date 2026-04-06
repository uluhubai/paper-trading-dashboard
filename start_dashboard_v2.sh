#!/bin/bash
# Start Dashboard V2

cd "$(dirname "$0")"

echo "🚀 STARTING MULTI-STRATEGY DASHBOARD V2"
echo "=================================================="

# Check if already running
if pgrep -f "streamlit.*dashboard_v2.py" > /dev/null; then
    echo "⚠️  Dashboard V2 is already running"
    echo "   To restart: pkill -f 'streamlit.*dashboard_v2.py' && ./start_dashboard_v2.sh"
    exit 1
fi

# Stop old dashboard if running
pkill -f "streamlit.*__init__.py" 2>/dev/null
sleep 2

# Start the dashboard
echo "🔄 Starting Multi-Strategy Dashboard V2..."
nohup ./venv/bin/streamlit run dashboard_v2.py --server.port=8502 --server.address=0.0.0.0 --server.headless=true > logs/dashboard_v2.log 2>&1 &

# Get PID
sleep 5
PID=$(pgrep -f "streamlit.*dashboard_v2.py")

if [ -z "$PID" ]; then
    echo "❌ Failed to start dashboard V2"
    echo "   Check logs: tail -f logs/dashboard_v2.log"
    exit 1
fi

echo "✅ Multi-Strategy Dashboard V2 started with PID: $PID"
echo "📝 Logs: logs/dashboard_v2.log"

echo ""
echo "🌐 ACCESS URLS:"
echo "   Dashboard V2: http://100.92.200.109:8502"
echo "   Old Dashboard: http://100.92.200.109:8501 (stopped)"
echo "   WordPress: http://100.92.200.109:8080/paper-trading-dashboard/"

echo ""
echo "📊 DASHBOARD FEATURES:"
echo "   ✅ 3 Strategy Comparison (Momentum, Mean Reversion, Breakout)"
echo "   ✅ Side-by-side performance metrics"
echo "   ✅ Portfolio history charts"
echo "   ✅ Trades timeline by strategy"
echo "   ✅ Real-time data from Paper Trading Engine V2"

echo ""
echo "🔧 MANAGEMENT:"
echo "   Stop: pkill -f 'streamlit.*dashboard_v2.py'"
echo "   Restart: Run this script again"
echo "   Logs: tail -f logs/dashboard_v2.log"

echo ""
echo "🎯 PAPER TRADING ENGINE V2 STATUS:"
./status_paper_trading_v2.sh | tail -20

echo ""
echo "✅ SYSTEM READY FOR STRATEGY TESTING!"
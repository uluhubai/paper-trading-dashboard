#!/bin/bash
# Start Paper Trading Engine V2

cd "$(dirname "$0")"

echo "🚀 STARTING PAPER TRADING ENGINE V2"
echo "=================================================="

# Check if already running
if pgrep -f "paper_trading_engine_v2.py" > /dev/null; then
    echo "⚠️  Paper trading engine V2 is already running"
    echo "   To restart: ./stop_paper_trading_v2.sh && ./start_paper_trading_v2.sh"
    exit 1
fi

# Start the engine
echo "🔄 Starting paper trading engine V2..."
nohup python3 paper_trading_engine_v2_simple.py > logs/paper_trading_v2.log 2>&1 &

# Get PID
sleep 2
PID=$(pgrep -f "paper_trading_engine_v2_simple.py")

if [ -z "$PID" ]; then
    echo "❌ Failed to start paper trading engine V2"
    echo "   Check logs: tail -f logs/paper_trading_v2.log"
    exit 1
fi

echo "✅ Paper trading engine V2 started with PID: $PID"
echo "📝 Logs: logs/paper_trading_v2.log"

echo ""
echo "📊 ENGINE CONFIGURATION:"
echo "   Interval: 10 minutes between cycles"
echo "   Capital: $10,000"
echo "   Assets: BTC, ETH, ADA"
echo "   Strategies: Momentum, Mean Reversion, Breakout"
echo "   Data: metrics_v2.json, portfolio_history_v2.csv"

echo ""
echo "🔧 MANAGEMENT:"
echo "   Stop: ./stop_paper_trading_v2.sh"
echo "   Status: ./status_paper_trading_v2.sh"
echo "   Logs: tail -f logs/paper_trading_v2.log"

echo ""
echo "🎯 WHAT HAPPENS:"
echo "   Every 10 minutes:"
echo "   1. Fetch market prices (simulated)"
echo "   2. Run 3 trading strategies simultaneously"
echo "   3. Execute simulated trades"
echo "   4. Update portfolio with strategy tracking"
echo "   5. Generate dashboard data for comparison"

echo ""
echo "📈 DASHBOARD WILL SHOW STRATEGY COMPARISON!"
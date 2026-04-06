#!/bin/bash
# Start Paper Trading Engine in background

set -e

cd "$(dirname "$0")"

echo "🚀 STARTING PAPER TRADING ENGINE"
echo "=================================================="

# Create logs directory
mkdir -p logs

# Check if already running
if pgrep -f "paper_trading_engine.py" > /dev/null; then
    echo "⚠️ Paper trading engine is already running"
    echo "   PID: $(pgrep -f "paper_trading_engine.py")"
    echo "   To restart: ./stop_paper_trading.sh then run this script again"
    exit 1
fi

# Start the engine
echo "🔄 Starting paper trading engine..."
nohup python3 paper_trading_engine.py --interval 10 --capital 10000 > logs/paper_trading.log 2>&1 &

# Get PID
PID=$!
sleep 2

# Check if started successfully
if ps -p $PID > /dev/null; then
    echo "✅ Paper trading engine started with PID: $PID"
    echo "📝 Logs: logs/paper_trading.log"
    echo ""
    echo "📊 ENGINE CONFIGURATION:"
    echo "   Interval: 10 minutes between cycles"
    echo "   Capital: $10,000"
    echo "   Assets: BTC, ETH, ADA"
    echo "   Strategies: MA Crossover, Mean Reversion"
    echo ""
    echo "🔧 MANAGEMENT:"
    echo "   Stop: ./stop_paper_trading.sh"
    echo "   Status: ./status_paper_trading.sh"
    echo "   Logs: tail -f logs/paper_trading.log"
    echo ""
    echo "🎯 WHAT HAPPENS:"
    echo "   Every 10 minutes:"
    echo "   1. Fetch market prices"
    echo "   2. Run trading strategies"
    echo "   3. Execute simulated trades"
    echo "   4. Update portfolio"
    echo "   5. Generate dashboard data"
    echo ""
    echo "📈 DASHBOARD WILL SHOW REAL-TIME DATA!"
else
    echo "❌ Failed to start paper trading engine"
    echo "Check logs/paper_trading.log for details"
    exit 1
fi
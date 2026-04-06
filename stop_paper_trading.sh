#!/bin/bash
# Stop Paper Trading Engine

set -e

cd "$(dirname "$0")"

echo "🛑 STOPPING PAPER TRADING ENGINE"
echo "=================================================="

# Find and kill the process
if pgrep -f "paper_trading_engine.py" > /dev/null; then
    PID=$(pgrep -f "paper_trading_engine.py")
    echo "🔄 Stopping paper trading engine (PID: $PID)..."
    kill $PID
    sleep 2
    
    if pgrep -f "paper_trading_engine.py" > /dev/null; then
        echo "⚠️ Process still running, forcing kill..."
        kill -9 $PID 2>/dev/null || true
        sleep 1
    fi
    
    if ! pgrep -f "paper_trading_engine.py" > /dev/null; then
        echo "✅ Paper trading engine stopped successfully"
    else
        echo "❌ Failed to stop paper trading engine"
        exit 1
    fi
else
    echo "ℹ️ Paper trading engine is not running"
fi

echo ""
echo "📊 FINAL PORTFOLIO STATUS:"
if [ -f "data/paper_portfolio.json" ]; then
    python3 -c "
import json
with open('data/paper_portfolio.json', 'r') as f:
    portfolio = json.load(f)
print(f'  Cash: \${portfolio[\"cash\"]:.2f}')
print(f'  Positions: {len(portfolio[\"positions\"])}')
if portfolio['history']:
    latest = portfolio['history'][-1]
    print(f'  Last Portfolio Value: \${latest[\"portfolio_value\"]:.2f}')
"
fi
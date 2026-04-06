#!/bin/bash
# Stop Paper Trading Engine V2

cd "$(dirname "$0")"

echo "🛑 STOPPING PAPER TRADING ENGINE V2"
echo "=================================================="

# Find and kill the process
PID=$(pgrep -f "paper_trading_engine_v2_simple.py")

if [ -z "$PID" ]; then
    echo "ℹ️  Paper trading engine V2 is not running"
    exit 0
fi

echo "🔄 Stopping paper trading engine V2 (PID: $PID)..."
kill $PID

# Wait for process to stop
sleep 3

# Check if still running
if pgrep -f "paper_trading_engine_v2.py" > /dev/null; then
    echo "⚠️  Process still running, forcing kill..."
    kill -9 $PID 2>/dev/null
    sleep 2
fi

if pgrep -f "paper_trading_engine_v2.py" > /dev/null; then
    echo "❌ Failed to stop paper trading engine V2"
    exit 1
fi

echo "✅ Paper trading engine V2 stopped successfully"

# Show final status
echo ""
echo "📊 FINAL STATUS (from metrics_v2.json):"
if [ -f "data/metrics_v2.json" ]; then
    python3 -c "
import json
try:
    with open('data/metrics_v2.json', 'r') as f:
        data = json.load(f)
    print(f'  Last Updated: {data.get(\"last_updated\", \"N/A\")}')
    print(f'  Portfolio Value: ${data.get(\"current_portfolio\", 0):,.2f}')
    print(f'  Total Return: {data.get(\"total_return\", 0):.2f}%')
    print(f'  Cash: ${data.get(\"cash\", 0):,.2f}')
    print(f'  Positions: {data.get(\"num_positions\", 0)}')
    
    strategies = data.get('strategies', {})
    if strategies:
        print('  Strategy Performance:')
        for name, stats in strategies.items():
            print(f'    {name}: {stats.get(\"total_pnl\", 0):.2f} PnL, {stats.get(\"win_rate\", 0):.1f}% win rate')
except Exception as e:
    print(f'  Error reading metrics: {e}')
"
else:
    echo "  No metrics file found"
fi

echo ""
echo "🔧 NEXT STEPS:"
echo "   Start: ./start_paper_trading_v2.sh"
echo "   Status: ./status_paper_trading_v2.sh"
echo "   View logs: tail -f logs/paper_trading_v2.log"
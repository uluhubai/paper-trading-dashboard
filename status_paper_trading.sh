#!/bin/bash
# Check status of Paper Trading Engine

set -e

cd "$(dirname "$0")"

echo "📊 PAPER TRADING ENGINE STATUS"
echo "=================================================="

# Check if running
if pgrep -f "paper_trading_engine.py" > /dev/null; then
    PID=$(pgrep -f "paper_trading_engine.py")
    echo "✅ RUNNING - PID: $PID"
    echo ""
    
    # Show process info
    echo "📈 PROCESS INFO:"
    ps -p $PID -o pid,user,pcpu,pmem,etime,cmd
    
    # Show last log entries
    echo ""
    echo "📝 RECENT LOGS:"
    if [ -f "logs/paper_trading.log" ]; then
        tail -20 logs/paper_trading.log
    else
        echo "No log file found"
    fi
    
    # Show portfolio status
    echo ""
    echo "💰 PORTFOLIO STATUS:"
    if [ -f "data/paper_portfolio.json" ]; then
        python3 -c "
import json, os, datetime
with open('data/paper_portfolio.json', 'r') as f:
    portfolio = json.load(f)

print(f'  Cash: \${portfolio[\"cash\"]:.2f}')
print(f'  Active Positions: {len(portfolio[\"positions\"])}')

if portfolio['positions']:
    print('  Position Details:')
    for symbol, pos in portfolio['positions'].items():
        print(f'    {symbol}: {pos[\"quantity\"]:.4f} @ \${pos[\"avg_price\"]:.2f}')

if portfolio['history']:
    latest = portfolio['history'][-1]
    initial = 10000.0
    current = latest['portfolio_value']
    pnl = current - initial
    pnl_pct = (pnl / initial) * 100
    print(f'  Portfolio Value: \${current:.2f}')
    print(f'  Total P&L: \${pnl:.2f} ({pnl_pct:.2f}%)')
    print(f'  Last Update: {latest[\"timestamp\"][:19]}')

if portfolio['trades']:
    print(f'  Total Trades: {len(portfolio[\"trades\"])}')
    recent = portfolio['trades'][-5:] if len(portfolio['trades']) >= 5 else portfolio['trades']
    print('  Recent Trades:')
    for trade in reversed(recent):
        print(f'    {trade[\"timestamp\"][11:19]} {trade[\"action\"]} {trade[\"quantity\"]:.4f} {trade[\"symbol\"]} @ \${trade[\"price\"]:.2f}')
"
    else
        echo "  No portfolio data found"
    fi
    
else
    echo "❌ NOT RUNNING"
    echo ""
    echo "To start: ./start_paper_trading.sh"
    
    # Show last known status
    if [ -f "data/metrics.json" ]; then
        echo ""
        echo "📅 LAST KNOWN STATUS (from metrics.json):"
        python3 -c "
import json, datetime
with open('data/metrics.json', 'r') as f:
    metrics = json.load(f)
print(f'  Last Updated: {metrics.get(\"last_updated\", \"Unknown\")}')
print(f'  Total Return: {metrics.get(\"total_return\", 0):.2f}%')
print(f'  Portfolio Value: \${metrics.get(\"current_portfolio\", 0):.2f}')
"
    fi
fi

echo ""
echo "🔧 QUICK COMMANDS:"
echo "  Start:   ./start_paper_trading.sh"
echo "  Stop:    ./stop_paper_trading.sh"
echo "  Restart: ./stop_paper_trading.sh && ./start_paper_trading.sh"
echo "  Logs:    tail -f logs/paper_trading.log"
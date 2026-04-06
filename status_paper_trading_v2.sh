#!/bin/bash
# Status check for Paper Trading Engine V2

cd "$(dirname "$0")"

echo "📊 PAPER TRADING ENGINE V2 STATUS"
echo "=================================================="

# Check if running
PID=$(pgrep -f "paper_trading_engine_v2_simple.py")

if [ -z "$PID" ]; then
    echo "❌ NOT RUNNING"
    echo ""
    echo "To start: ./start_paper_trading_v2.sh"
else
    echo "✅ RUNNING - PID: $PID"
    echo ""
    echo "📈 ENGINE INFO:"
    echo "   Process: paper_trading_engine_v2.py"
    echo "   PID: $PID"
    echo "   Uptime: $(ps -p $PID -o etime= 2>/dev/null || echo 'N/A')"
    echo "   Logs: logs/paper_trading_v2.log"
fi

echo ""
echo "📅 CURRENT STATUS (from metrics_v2.json):"
if [ -f "data/metrics_v2.json" ]; then
    python3 -c "
import json
from datetime import datetime

try:
    with open('data/metrics_v2.json', 'r') as f:
        data = json.load(f)
    
    last_updated = data.get('last_updated', 'N/A')
    portfolio = data.get('current_portfolio', 0)
    total_return = data.get('total_return', 0)
    cash = data.get('cash', 0)
    positions = data.get('num_positions', 0)
    
    print(f'  Last Updated: {last_updated}')
    print(f'  Portfolio Value: ${portfolio:,.2f}')
    print(f'  Total Return: {total_return:.2f}%')
    print(f'  Cash: ${cash:,.2f}')
    print(f'  Active Positions: {positions}')
    
    # Calculate time since last update
    if last_updated != 'N/A':
        try:
            last_time = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            diff = now - last_time
            minutes = int(diff.total_seconds() / 60)
            print(f'  Time Since Update: {minutes} minutes')
        except:
            pass
    
    # Show strategy performance
    strategies = data.get('strategies', {})
    if strategies:
        print('')
        print('  🎯 STRATEGY PERFORMANCE:')
        for name, stats in strategies.items():
            active = '✅' if stats.get('active', False) else '❌'
            pnl = stats.get('total_pnl', 0)
            win_rate = stats.get('win_rate', 0)
            trades = stats.get('num_trades', 0)
            print(f'    {active} {name}:')
            print(f'      PnL: ${pnl:.2f}')
            print(f'      Win Rate: {win_rate:.1f}%')
            print(f'      Trades: {trades}')
    
    # Show recent trades if available
    try:
        import pandas as pd
        df = pd.read_csv('data/recent_trades_v2.csv')
        if not df.empty:
            print('')
            print('  📊 RECENT TRADES (last 5):')
            recent = df.tail(5)
            for _, trade in recent.iterrows():
                action = '🟢 BUY' if trade['action'] == 'BUY' else '🔴 SELL'
                symbol = trade['symbol']
                quantity = trade['quantity']
                price = trade['price']
                strategy = trade.get('strategy', 'N/A')
                print(f'    {action} {quantity:.4f} {symbol} @ ${price:.2f} ({strategy})')
    except:
        pass
        
except Exception as e:
    print(f'  Error reading metrics: {e}')
"
else
    echo "  No metrics file found"
    echo "  Engine may not have run yet or data directory missing"
fi

echo ""
echo "🔧 QUICK COMMANDS:"
echo "  Start:   ./start_paper_trading_v2.sh"
echo "  Stop:    ./stop_paper_trading_v2.sh"
echo "  Restart: ./stop_paper_trading_v2.sh && ./start_paper_trading_v2.sh"
echo "  Logs:    tail -f logs/paper_trading_v2.log"

echo ""
echo "📁 DATA FILES:"
echo "  Metrics: data/metrics_v2.json"
echo "  Portfolio History: data/portfolio_history_v2.csv"
echo "  Recent Trades: data/recent_trades_v2.csv"
echo "  Strategy Comparison: data/strategy_comparison_v2.json"
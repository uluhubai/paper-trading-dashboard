#!/usr/bin/env python3
"""
Generate test data for Paper Trading Dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

def generate_portfolio_data():
    """Generate sample portfolio data for dashboard"""
    
    # Create date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate portfolio value (starting at 10,000 with random walk)
    np.random.seed(42)
    initial_capital = 10000
    daily_returns = np.random.normal(0.001, 0.02, len(dates))  # Mean 0.1%, Std 2%
    portfolio_value = initial_capital * np.cumprod(1 + daily_returns)
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'portfolio_value': portfolio_value,
        'daily_return': daily_returns,
        'cumulative_return': portfolio_value / initial_capital - 1
    })
    
    # Calculate metrics
    total_return = df['cumulative_return'].iloc[-1]
    volatility = df['daily_return'].std() * np.sqrt(252)  # Annualized
    sharpe_ratio = df['daily_return'].mean() / df['daily_return'].std() * np.sqrt(252)
    
    # Find max drawdown
    cumulative = (1 + df['daily_return']).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()
    
    # Win rate (simulate trades)
    n_trades = 30
    trades = pd.DataFrame({
        'timestamp': dates[:n_trades],  # First 30 days
        'symbol': ['BTC', 'ETH', 'ADA'] * 10,
        'action': np.random.choice(['BUY', 'SELL'], n_trades),
        'quantity': np.random.uniform(0.1, 5, n_trades),
        'price': np.random.uniform(100, 50000, n_trades),
        'pnl': np.random.normal(0, 100, n_trades)
    })
    
    win_rate = len(trades[trades['pnl'] > 0]) / len(trades) if len(trades) > 0 else 0
    
    # Save data
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Save portfolio data
    df.to_csv(os.path.join(data_dir, 'portfolio_history.csv'), index=False)
    
    # Save trades
    trades.to_csv(os.path.join(data_dir, 'recent_trades.csv'), index=False)
    
    # Save metrics
    metrics = {
        'total_return': float(total_return),
        'sharpe_ratio': float(sharpe_ratio),
        'max_drawdown': float(max_drawdown),
        'win_rate': float(win_rate),
        'volatility': float(volatility),
        'initial_capital': float(initial_capital),
        'current_portfolio': float(portfolio_value[-1]),
        'total_trades': len(trades),
        'winning_trades': len(trades[trades['pnl'] > 0]),
        'losing_trades': len(trades[trades['pnl'] < 0])
    }
    
    with open(os.path.join(data_dir, 'metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("✅ Generated test data:")
    print(f"   Portfolio history: {len(df)} days")
    print(f"   Recent trades: {len(trades)} trades")
    print(f"   Metrics: Total Return = {total_return:.2%}, Sharpe = {sharpe_ratio:.2f}")
    print(f"   Files saved to: {data_dir}/")
    
    return metrics

if __name__ == "__main__":
    print("🚀 Generating test data for Paper Trading Dashboard...")
    metrics = generate_portfolio_data()
    print("🎉 Test data generation complete!")
    print("\n📊 Generated Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            if 'return' in key or 'rate' in key:
                print(f"   {key}: {value:.2%}")
            elif 'ratio' in key:
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value:,.2f}")
        else:
            print(f"   {key}: {value}")
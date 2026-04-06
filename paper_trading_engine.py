#!/usr/bin/env python3
"""
Paper Trading Engine
Executes trading strategies in real-time and updates portfolio
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import random
import logging
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/paper_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PaperTradingEngine:
    """Engine for paper trading with simulated market data"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.portfolio = {
            'cash': initial_capital,
            'positions': {},  # symbol -> {'quantity': float, 'avg_price': float}
            'history': [],
            'trades': []
        }
        self.current_prices = {}
        self.strategies = []
        self.running = False
        
        # Load or create portfolio data
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.load_portfolio()
    
    def load_portfolio(self):
        """Load portfolio from file or create new"""
        portfolio_file = os.path.join(self.data_dir, 'paper_portfolio.json')
        
        if os.path.exists(portfolio_file):
            try:
                with open(portfolio_file, 'r') as f:
                    self.portfolio = json.load(f)
                logger.info(f"Loaded portfolio: ${self.portfolio['cash']:.2f} cash, "
                          f"{len(self.portfolio['positions'])} positions")
            except Exception as e:
                logger.error(f"Error loading portfolio: {e}")
                self.reset_portfolio()
        else:
            self.reset_portfolio()
    
    def save_portfolio(self):
        """Save portfolio to file"""
        portfolio_file = os.path.join(self.data_dir, 'paper_portfolio.json')
        
        try:
            with open(portfolio_file, 'w') as f:
                json.dump(self.portfolio, f, indent=2)
            logger.debug("Portfolio saved")
        except Exception as e:
            logger.error(f"Error saving portfolio: {e}")
    
    def reset_portfolio(self):
        """Reset portfolio to initial state"""
        self.portfolio = {
            'cash': self.initial_capital,
            'positions': {},
            'history': [],
            'trades': []
        }
        logger.info(f"Reset portfolio to ${self.initial_capital:.2f}")
        self.save_portfolio()
    
    def fetch_market_data(self) -> Dict[str, float]:
        """Fetch current market prices (simulated or real)"""
        try:
            # Try to use DataFetcher if available
            from data.data_fetcher import DataFetcher
            fetcher = DataFetcher()
            prices = fetcher.fetch_latest_prices(['bitcoin', 'ethereum', 'cardano'])
            
            if prices:
                self.current_prices = {
                    'BTC': prices.get('bitcoin', {}).get('usd', 67321.45),
                    'ETH': prices.get('ethereum', {}).get('usd', 3650.78),
                    'ADA': prices.get('cardano', {}).get('usd', 0.58)
                }
                logger.info(f"Fetched real prices: {self.current_prices}")
                return self.current_prices
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Error fetching real prices: {e}")
        
        # Fallback to simulated prices with realistic volatility
        symbols = ['BTC', 'ETH', 'ADA']
        base_prices = {'BTC': 67321.45, 'ETH': 3650.78, 'ADA': 0.58}
        
        for symbol in symbols:
            # Add some random movement (±2% for BTC/ETH, ±5% for ADA)
            volatility = 0.02 if symbol in ['BTC', 'ETH'] else 0.05
            change = random.uniform(-volatility, volatility)
            
            if symbol not in self.current_prices:
                self.current_prices[symbol] = base_prices[symbol]
            else:
                self.current_prices[symbol] *= (1 + change)
        
        logger.debug(f"Simulated prices: {self.current_prices}")
        return self.current_prices
    
    def calculate_portfolio_value(self) -> float:
        """Calculate total portfolio value (cash + positions)"""
        total_value = self.portfolio['cash']
        
        for symbol, position in self.portfolio['positions'].items():
            if symbol in self.current_prices:
                position_value = position['quantity'] * self.current_prices[symbol]
                total_value += position_value
        
        return total_value
    
    def execute_trade(self, symbol: str, action: str, quantity: float, price: float = None):
        """Execute a trade (BUY or SELL)"""
        if price is None:
            price = self.current_prices.get(symbol)
            if price is None:
                logger.error(f"No price available for {symbol}")
                return False
        
        symbol = symbol.upper()
        trade_value = quantity * price
        
        if action.upper() == 'BUY':
            if trade_value > self.portfolio['cash']:
                logger.warning(f"Insufficient cash for BUY {symbol}: ${trade_value:.2f} > ${self.portfolio['cash']:.2f}")
                return False
            
            # Update cash
            self.portfolio['cash'] -= trade_value
            
            # Update or create position
            if symbol in self.portfolio['positions']:
                pos = self.portfolio['positions'][symbol]
                total_quantity = pos['quantity'] + quantity
                total_cost = (pos['quantity'] * pos['avg_price']) + trade_value
                pos['avg_price'] = total_cost / total_quantity
                pos['quantity'] = total_quantity
            else:
                self.portfolio['positions'][symbol] = {
                    'quantity': quantity,
                    'avg_price': price
                }
            
            logger.info(f"BUY {quantity:.4f} {symbol} @ ${price:.2f} = ${trade_value:.2f}")
            
        elif action.upper() == 'SELL':
            if symbol not in self.portfolio['positions']:
                logger.warning(f"No position to SELL for {symbol}")
                return False
            
            pos = self.portfolio['positions'][symbol]
            if quantity > pos['quantity']:
                logger.warning(f"Insufficient quantity to SELL {symbol}: {quantity} > {pos['quantity']}")
                return False
            
            # Update cash
            self.portfolio['cash'] += trade_value
            
            # Update position
            pos['quantity'] -= quantity
            if pos['quantity'] <= 0.000001:  # Near zero
                del self.portfolio['positions'][symbol]
            
            logger.info(f"SELL {quantity:.4f} {symbol} @ ${price:.2f} = ${trade_value:.2f}")
        
        else:
            logger.error(f"Invalid action: {action}")
            return False
        
        # Record trade
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'action': action.upper(),
            'quantity': quantity,
            'price': price,
            'value': trade_value,
            'cash_after': self.portfolio['cash'],
            'portfolio_value': self.calculate_portfolio_value()
        }
        
        self.portfolio['trades'].append(trade_record)
        
        # Keep only last 100 trades
        if len(self.portfolio['trades']) > 100:
            self.portfolio['trades'] = self.portfolio['trades'][-100:]
        
        # Update portfolio history
        self.update_portfolio_history()
        
        self.save_portfolio()
        return True
    
    def update_portfolio_history(self):
        """Update portfolio history with current snapshot"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'portfolio_value': self.calculate_portfolio_value(),
            'cash': self.portfolio['cash'],
            'num_positions': len(self.portfolio['positions']),
            'btc_price': self.current_prices.get('BTC', 0),
            'eth_price': self.current_prices.get('ETH', 0),
            'ada_price': self.current_prices.get('ADA', 0)
        }
        
        self.portfolio['history'].append(snapshot)
        
        # Keep only last 1000 snapshots
        if len(self.portfolio['history']) > 1000:
            self.portfolio['history'] = self.portfolio['history'][-1000:]
    
    def run_strategy_ma_crossover(self):
        """Simple Moving Average Crossover strategy"""
        # This is a simplified version - in reality would use historical data
        symbols = ['BTC', 'ETH', 'ADA']
        
        for symbol in symbols:
            if symbol not in self.current_prices:
                continue
            
            price = self.current_prices[symbol]
            
            # Simulate MA signals (in reality would calculate from historical data)
            # 50% chance of buy signal, 30% sell, 20% hold
            signal = random.choices(['BUY', 'SELL', 'HOLD'], weights=[0.5, 0.3, 0.2])[0]
            
            if signal == 'BUY':
                # Determine quantity (1-10% of cash)
                cash_alloc = self.portfolio['cash'] * random.uniform(0.01, 0.10)
                quantity = cash_alloc / price
                
                if quantity > 0:
                    self.execute_trade(symbol, 'BUY', quantity, price)
            
            elif signal == 'SELL':
                if symbol in self.portfolio['positions']:
                    pos = self.portfolio['positions'][symbol]
                    # Sell 10-50% of position
                    sell_pct = random.uniform(0.10, 0.50)
                    quantity = pos['quantity'] * sell_pct
                    
                    if quantity > 0:
                        self.execute_trade(symbol, 'SELL', quantity, price)
    
    def run_strategy_mean_reversion(self):
        """Mean Reversion strategy"""
        symbols = ['BTC', 'ETH', 'ADA']
        
        for symbol in symbols:
            if symbol not in self.current_prices:
                continue
            
            price = self.current_prices[symbol]
            
            # Simulate oversold/overbought conditions
            # Random signal based on "volatility"
            rsi_simulated = random.uniform(20, 80)  # Simulated RSI
            
            if rsi_simulated < 30:  # Oversold - BUY
                cash_alloc = self.portfolio['cash'] * random.uniform(0.05, 0.15)
                quantity = cash_alloc / price
                
                if quantity > 0:
                    self.execute_trade(symbol, 'BUY', quantity, price)
            
            elif rsi_simulated > 70:  # Overbought - SELL
                if symbol in self.portfolio['positions']:
                    pos = self.portfolio['positions'][symbol]
                    sell_pct = random.uniform(0.20, 0.80)
                    quantity = pos['quantity'] * sell_pct
                    
                    if quantity > 0:
                        self.execute_trade(symbol, 'SELL', quantity, price)
    
    def generate_dashboard_data(self):
        """Generate data files for the dashboard"""
        # Generate portfolio history CSV
        if self.portfolio['history']:
            history_df = pd.DataFrame(self.portfolio['history'])
            history_df['date'] = pd.to_datetime(history_df['timestamp'])
            
            # Save to CSV
            portfolio_file = os.path.join(self.data_dir, 'portfolio_history.csv')
            history_df[['date', 'portfolio_value', 'cash']].to_csv(portfolio_file, index=False)
            
            # Generate recent trades CSV
            if self.portfolio['trades']:
                trades_df = pd.DataFrame(self.portfolio['trades'])
                trades_file = os.path.join(self.data_dir, 'recent_trades.csv')
                trades_df.to_csv(trades_file, index=False)
            
            # Calculate metrics
            if len(history_df) > 1:
                returns = history_df['portfolio_value'].pct_change().dropna()
                total_return = (history_df['portfolio_value'].iloc[-1] / history_df['portfolio_value'].iloc[0] - 1) * 100
                
                # Sharpe ratio (assuming 0% risk-free rate)
                sharpe_ratio = returns.mean() / returns.std() * np.sqrt(365) if returns.std() > 0 else 0
                
                # Max drawdown
                cumulative = (1 + returns).cumprod()
                running_max = cumulative.expanding().max()
                drawdown = (cumulative / running_max - 1)
                max_drawdown = drawdown.min() * 100
                
                # Win rate from trades
                if self.portfolio['trades']:
                    trades_df = pd.DataFrame(self.portfolio['trades'])
                    winning_trades = (trades_df['value'] > 0).sum() if 'value' in trades_df.columns else 0
                    win_rate = (winning_trades / len(trades_df)) * 100 if len(trades_df) > 0 else 50
                else:
                    win_rate = 50.0
                
                # Volatility
                volatility = returns.std() * np.sqrt(365) * 100 if len(returns) > 0 else 20
            else:
                total_return = 0
                sharpe_ratio = 0
                max_drawdown = 0
                win_rate = 50
                volatility = 20
            
            # Create metrics JSON
            metrics = {
                'total_return': round(total_return, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'max_drawdown': round(max_drawdown, 2),
                'win_rate': round(win_rate, 2),
                'volatility': round(volatility, 2),
                'current_btc_price': round(self.current_prices.get('BTC', 67321.45), 2),
                'current_eth_price': round(self.current_prices.get('ETH', 3650.78), 2),
                'current_ada_price': round(self.current_prices.get('ADA', 0.58), 4),
                'current_portfolio': round(self.calculate_portfolio_value(), 2),
                'cash': round(self.portfolio['cash'], 2),
                'num_positions': len(self.portfolio['positions']),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_source': 'Paper Trading Engine'
            }
            
            metrics_file = os.path.join(self.data_dir, 'metrics.json')
            with open(metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            logger.info(f"Generated dashboard data: Total Return={total_return:.2f}%, "
                      f"Portfolio=${self.calculate_portfolio_value():.2f}")
            
            return True
        
        return False
    
    def run_cycle(self):
        """Run one cycle of the trading engine"""
        logger.info("=" * 60)
        logger.info("STARTING PAPER TRADING CYCLE")
        logger.info("=" * 60)
        
        # 1. Fetch market data
        self.fetch_market_data()
        
        # 2. Run strategies
        logger.info("Running strategies...")
        self.run_strategy_ma_crossover()
        self.run_strategy_mean_reversion()
        
        # 3. Update portfolio history
        self.update_portfolio_history()
        
        # 4. Generate dashboard data
        self.generate_dashboard_data()
        
        # 5. Log status
        portfolio_value = self.calculate_portfolio_value()
        pnl = portfolio_value - self.initial_capital
        pnl_pct = (pnl / self.initial_capital) * 100
        
        logger.info(f"Portfolio: ${portfolio_value:.2f} (PNL: ${pnl:.2f}, {pnl_pct:.2f}%)")
        logger.info(f"Cash: ${self.portfolio['cash']:.2f}")
        logger.info(f"Positions: {len(self.portfolio['positions'])}")
        
        logger.info("=" * 60)
        logger.info("CYCLE COMPLETE")
        logger.info("=" * 60)
        
        return True
    
    def run_continuously(self, interval_minutes: int = 5):
        """Run the trading engine continuously"""
        logger.info(f"Starting paper trading engine (interval: {interval_minutes} minutes)")
        logger.info(f"Initial capital: ${self.initial_capital:.2f})")
        
        self.running = True
        cycle_count = 0
        
        try:
            while self.running:
                cycle_count += 1
                logger.info(f"\n📊 CYCLE {cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Run one cycle
                self.run_cycle()
                
                # Wait for next cycle
                logger.info(f"⏳ Waiting {interval_minutes} minutes for next cycle...")
                for i in range(interval_minutes * 60):
                    if not self.running:
                        break
                    time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Paper trading engine stopped by user")
        except Exception as e:
            logger.error(f"Error in paper trading engine: {e}")
        finally:
            self.running = False
            logger.info("Paper trading engine stopped")

def main():
    """Main function to run paper trading engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Paper Trading Engine')
    parser.add_argument('--interval', type=int, default=5,
                       help='Interval between cycles in minutes (default: 5)')
    parser.add_argument('--capital', type=float, default=10000.0,
                       help='Initial capital (default: 10000)')
    parser.add_argument('--reset', action='store_true',
                       help='Reset portfolio before starting')
    
    args = parser.parse_args()
    
    # Create engine
    engine = PaperTradingEngine(initial_capital=args.capital)
    
    if args.reset:
        engine.reset_portfolio()
        logger.info("Portfolio reset to initial state")
    
    # Run continuously
    engine.run_continuously(interval_minutes=args.interval)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Paper Trading Engine V2 - Simple Multi-Strategy Version
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import time
import random
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/paper_trading_v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PaperTradingEngineV2:
    """Enhanced engine with multiple strategies"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.portfolio = {
            'cash': initial_capital,
            'positions': {},
            'history': [],
            'trades': []
        }
        self.strategy_performance = {
            'momentum': {'trades': 0, 'pnl': 0, 'wins': 0},
            'mean_reversion': {'trades': 0, 'pnl': 0, 'wins': 0},
            'breakout': {'trades': 0, 'pnl': 0, 'wins': 0}
        }
        
        # Data directory
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.load_portfolio()
    
    def load_portfolio(self):
        """Load or create portfolio"""
        portfolio_file = os.path.join(self.data_dir, 'portfolio_v2.json')
        if os.path.exists(portfolio_file):
            try:
                with open(portfolio_file, 'r') as f:
                    self.portfolio = json.load(f)
                logger.info("Loaded portfolio V2")
            except:
                self.reset_portfolio()
        else:
            self.reset_portfolio()
    
    def reset_portfolio(self):
        """Reset to initial state"""
        self.portfolio = {
            'cash': self.initial_capital,
            'positions': {},
            'history': [],
            'trades': []
        }
        logger.info(f"Reset portfolio to ${self.initial_capital:,.2f}")
    
    def fetch_market_prices(self):
        """Get current prices"""
        base_prices = {'BTC': 67321, 'ETH': 3650, 'ADA': 0.58}
        return {k: v * (1 + random.uniform(-0.02, 0.02)) for k, v in base_prices.items()}
    
    def momentum_strategy(self, prices, portfolio):
        """Trend following strategy"""
        signals = []
        for symbol, price in prices.items():
            # Simple momentum logic
            position = portfolio['positions'].get(symbol, {}).get('quantity', 0)
            
            # Random buy/sell for demo (will be replaced with real logic)
            if random.random() > 0.7 and position == 0:
                qty = (portfolio['cash'] * 0.1) / price
                signals.append({
                    'symbol': symbol, 'action': 'BUY', 'quantity': qty,
                    'price': price, 'strategy': 'momentum', 'reason': 'Momentum signal'
                })
            elif random.random() > 0.8 and position > 0:
                signals.append({
                    'symbol': symbol, 'action': 'SELL', 'quantity': position,
                    'price': price, 'strategy': 'momentum', 'reason': 'Take profit'
                })
        return signals
    
    def mean_reversion_strategy(self, prices, portfolio):
        """Buy low, sell high strategy"""
        signals = []
        for symbol, price in prices.items():
            position = portfolio['positions'].get(symbol, {}).get('quantity', 0)
            
            # Simple mean reversion logic
            if random.random() > 0.75 and position == 0:
                qty = (portfolio['cash'] * 0.08) / price
                signals.append({
                    'symbol': symbol, 'action': 'BUY', 'quantity': qty,
                    'price': price, 'strategy': 'mean_reversion', 'reason': 'Oversold'
                })
            elif random.random() > 0.85 and position > 0:
                signals.append({
                    'symbol': symbol, 'action': 'SELL', 'quantity': position,
                    'price': price, 'strategy': 'mean_reversion', 'reason': 'Overbought'
                })
        return signals
    
    def breakout_strategy(self, prices, portfolio):
        """Breakout trading strategy"""
        signals = []
        for symbol, price in prices.items():
            position = portfolio['positions'].get(symbol, {}).get('quantity', 0)
            
            # Simple breakout logic
            if random.random() > 0.8 and position == 0:
                qty = (portfolio['cash'] * 0.12) / price
                signals.append({
                    'symbol': symbol, 'action': 'BUY', 'quantity': qty,
                    'price': price, 'strategy': 'breakout', 'reason': 'Breakout signal'
                })
            elif random.random() > 0.9 and position > 0:
                signals.append({
                    'symbol': symbol, 'action': 'SELL', 'quantity': position,
                    'price': price, 'strategy': 'breakout', 'reason': 'Stop loss'
                })
        return signals
    
    def execute_trade(self, signal):
        """Execute a trade"""
        symbol = signal['symbol']
        action = signal['action']
        quantity = signal['quantity']
        price = signal['price']
        strategy = signal['strategy']
        
        if action == 'BUY':
            cost = quantity * price
            if self.portfolio['cash'] >= cost:
                self.portfolio['cash'] -= cost
                
                if symbol not in self.portfolio['positions']:
                    self.portfolio['positions'][symbol] = {'quantity': 0, 'avg_price': 0}
                
                pos = self.portfolio['positions'][symbol]
                total_qty = pos['quantity'] + quantity
                total_cost = (pos['quantity'] * pos['avg_price']) + cost
                pos['avg_price'] = total_cost / total_qty if total_qty > 0 else 0
                pos['quantity'] = total_qty
                
                self.portfolio['trades'].append({
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol, 'action': action, 'quantity': quantity,
                    'price': price, 'cost': cost, 'strategy': strategy,
                    'reason': signal['reason']
                })
                
                self.strategy_performance[strategy]['trades'] += 1
                logger.info(f"{strategy}: BUY {quantity:.4f} {symbol} @ ${price:.2f}")
                return True
        
        elif action == 'SELL':
            if symbol in self.portfolio['positions']:
                pos = self.portfolio['positions'][symbol]
                if pos['quantity'] >= quantity:
                    revenue = quantity * price
                    self.portfolio['cash'] += revenue
                    
                    cost_basis = quantity * pos['avg_price']
                    pnl = revenue - cost_basis
                    
                    pos['quantity'] -= quantity
                    if pos['quantity'] == 0:
                        del self.portfolio['positions'][symbol]
                    
                    self.portfolio['trades'].append({
                        'timestamp': datetime.now().isoformat(),
                        'symbol': symbol, 'action': action, 'quantity': quantity,
                        'price': price, 'revenue': revenue, 'pnl': pnl,
                        'strategy': strategy, 'reason': signal['reason']
                    })
                    
                    self.strategy_performance[strategy]['trades'] += 1
                    self.strategy_performance[strategy]['pnl'] += pnl
                    if pnl > 0:
                        self.strategy_performance[strategy]['wins'] += 1
                    
                    logger.info(f"{strategy}: SELL {quantity:.4f} {symbol} @ ${price:.2f} (PNL: ${pnl:.2f})")
                    return True
        
        return False
    
    def run_cycle(self):
        """Run one trading cycle"""
        logger.info("=" * 60)
        logger.info(f"TRADING CYCLE - {datetime.now()}")
        logger.info("=" * 60)
        
        # Get prices
        prices = self.fetch_market_prices()
        logger.info(f"Prices: BTC=${prices.get('BTC', 0):.2f}, ETH=${prices.get('ETH', 0):.2f}, ADA=${prices.get('ADA', 0):.4f}")
        
        # Run all strategies
        all_signals = []
        all_signals.extend(self.momentum_strategy(prices, self.portfolio))
        all_signals.extend(self.mean_reversion_strategy(prices, self.portfolio))
        all_signals.extend(self.breakout_strategy(prices, self.portfolio))
        
        # Execute trades
        executed = 0
        for signal in all_signals:
            if self.execute_trade(signal):
                executed += 1
        
        # Calculate portfolio value
        portfolio_value = self.portfolio['cash']
        for symbol, pos in self.portfolio['positions'].items():
            if symbol in prices:
                portfolio_value += pos['quantity'] * prices[symbol]
        
        # Save history
        self.portfolio['history'].append({
            'timestamp': datetime.now().isoformat(),
            'portfolio_value': portfolio_value,
            'cash': self.portfolio['cash'],
            'positions': len(self.portfolio['positions'])
        })
        
        # Save data
        self.save_data(prices, portfolio_value)
        
        # Log results
        logger.info(f"Executed {executed} trades")
        logger.info(f"Portfolio: ${portfolio_value:,.2f} (Cash: ${self.portfolio['cash']:,.2f})")
        
        # Show strategy performance
        logger.info("Strategy Performance:")
        for strategy, perf in self.strategy_performance.items():
            win_rate = (perf['wins'] / perf['trades'] * 100) if perf['trades'] > 0 else 0
            logger.info(f"  {strategy}: {perf['trades']} trades, ${perf['pnl']:.2f} PnL, {win_rate:.1f}% win rate")
        
        logger.info("=" * 60)
        
        # Save portfolio
        self.save_portfolio()
        
        return executed
    
    def save_data(self, prices, portfolio_value):
        """Save data for dashboard"""
        # Metrics
        metrics = {
            'portfolio_value': portfolio_value,
            'cash': self.portfolio['cash'],
            'positions': len(self.portfolio['positions']),
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'strategies': self.strategy_performance
        }
        
        with open(os.path.join(self.data_dir, 'metrics_v2.json'), 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Recent trades
        if self.portfolio['trades']:
            recent = self.portfolio['trades'][-20:]
            pd.DataFrame(recent).to_csv(os.path.join(self.data_dir, 'recent_trades_v2.csv'), index=False)
        
        # Portfolio history
        if self.portfolio['history']:
            pd.DataFrame(self.portfolio['history']).to_csv(os.path.join(self.data_dir, 'portfolio_history_v2.csv'), index=False)
    
    def save_portfolio(self):
        """Save portfolio state"""
        with open(os.path.join(self.data_dir, 'portfolio_v2.json'), 'w') as f:
            json.dump(self.portfolio, f, indent=2)
    
    def run(self, interval_minutes=10):
        """Main loop"""
        logger.info(f"Starting Paper Trading Engine V2 ({interval_minutes}-min intervals)")
        logger.info(f"Strategies: Momentum, Mean Reversion, Breakout")
        
        try:
            while True:
                self.run_cycle()
                logger.info(f"Waiting {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            logger.info("Stopping...")

def main():
    engine = PaperTradingEngineV2(initial_capital=10000.0)
    engine.run(interval_minutes=10)

if __name__ == "__main__":
    main()
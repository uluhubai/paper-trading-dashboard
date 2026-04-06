"""
Portfolio Management module for Paper Trading System
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class Portfolio:
    """Portfolio management system"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}  # symbol -> {'quantity': float, 'avg_price': float}
        self.trade_history = []
        self.performance_history = []
        self.current_value = initial_capital
        
    def execute_trade(self, 
                     symbol: str, 
                     order_type: str, 
                     quantity: float, 
                     price: float,
                     commission: float = 0.0) -> bool:
        """Execute a trade and update portfolio"""
        
        if order_type not in ['BUY', 'SELL']:
            logger.error(f"Invalid order type: {order_type}")
            return False
        
        if quantity <= 0:
            logger.error(f"Invalid quantity: {quantity}")
            return False
        
        if price <= 0:
            logger.error(f"Invalid price: {price}")
            return False
        
        trade_value = quantity * price
        total_cost = trade_value + commission
        
        if order_type == 'BUY':
            if total_cost > self.cash:
                logger.error(f"Insufficient cash for buy: ${total_cost:.2f} > ${self.cash:.2f}")
                return False
            
            # Update cash
            self.cash -= total_cost
            
            # Update position
            if symbol in self.positions:
                # Average price calculation
                old_quantity = self.positions[symbol]['quantity']
                old_avg_price = self.positions[symbol]['avg_price']
                old_value = old_quantity * old_avg_price
                
                new_quantity = old_quantity + quantity
                new_avg_price = (old_value + trade_value) / new_quantity
                
                self.positions[symbol] = {
                    'quantity': new_quantity,
                    'avg_price': new_avg_price,
                    'total_cost': old_quantity * old_avg_price + total_cost
                }
            else:
                self.positions[symbol] = {
                    'quantity': quantity,
                    'avg_price': price,
                    'total_cost': total_cost
                }
            
            logger.info(f"Bought {quantity:.2f} {symbol} @ ${price:.2f} "
                       f"(cost: ${total_cost:.2f}, cash: ${self.cash:.2f})")
        
        elif order_type == 'SELL':
            if symbol not in self.positions or self.positions[symbol]['quantity'] < quantity:
                logger.error(f"Insufficient position for sell: {quantity} > "
                           f"{self.positions.get(symbol, {}).get('quantity', 0)}")
                return False
            
            # Update position
            position = self.positions[symbol]
            remaining_quantity = position['quantity'] - quantity
            
            if remaining_quantity > 0:
                # Partial sell - keep position with same average price
                self.positions[symbol]['quantity'] = remaining_quantity
            else:
                # Full sell - remove position
                del self.positions[symbol]
            
            # Update cash
            self.cash += trade_value - commission
            
            logger.info(f"Sold {quantity:.2f} {symbol} @ ${price:.2f} "
                       f"(proceeds: ${trade_value:.2f}, cash: ${self.cash:.2f})")
        
        # Record trade
        trade_record = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'type': order_type,
            'quantity': quantity,
            'price': price,
            'value': trade_value,
            'commission': commission,
            'cash_after': self.cash
        }
        
        self.trade_history.append(trade_record)
        
        # Update performance
        self.update_performance()
        
        return True
    
    def update_performance(self, current_prices: Dict[str, float] = None):
        """Update portfolio performance metrics"""
        
        if current_prices is None:
            current_prices = {}
        
        # Calculate position values
        position_values = {}
        total_position_value = 0
        
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                position_value = position['quantity'] * current_price
                position_values[symbol] = position_value
                total_position_value += position_value
            else:
                # Use average price if current price not available
                position_value = position['quantity'] * position['avg_price']
                position_values[symbol] = position_value
                total_position_value += position_value
        
        # Calculate total portfolio value
        self.current_value = self.cash + total_position_value
        
        # Calculate P&L
        total_invested = self.initial_capital - self.cash
        unrealized_pnl = total_position_value - total_invested if total_invested > 0 else 0
        
        # Calculate returns
        total_return = (self.current_value - self.initial_capital) / self.initial_capital
        
        # Record performance
        performance_record = {
            'timestamp': datetime.now(),
            'cash': self.cash,
            'position_value': total_position_value,
            'total_value': self.current_value,
            'unrealized_pnl': unrealized_pnl,
            'total_return': total_return,
            'positions_count': len(self.positions),
            'position_values': position_values
        }
        
        self.performance_history.append(performance_record)
        
        logger.debug(f"Portfolio updated: ${self.current_value:.2f} "
                    f"(cash: ${self.cash:.2f}, positions: ${total_position_value:.2f})")
    
    def get_position(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get position details for a symbol"""
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> Dict[str, Dict[str, float]]:
        """Get all positions"""
        return self.positions.copy()
    
    def get_portfolio_value(self, current_prices: Dict[str, float] = None) -> float:
        """Get current portfolio value"""
        self.update_performance(current_prices)
        return self.current_value
    
    def get_cash_balance(self) -> float:
        """Get current cash balance"""
        return self.cash
    
    def get_trade_history(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Get trade history, optionally filtered by symbol"""
        if symbol:
            return [trade for trade in self.trade_history if trade['symbol'] == symbol]
        return self.trade_history.copy()
    
    def get_performance_history(self) -> List[Dict[str, Any]]:
        """Get performance history"""
        return self.performance_history.copy()
    
    def calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        
        if not self.performance_history:
            return {}
        
        # Convert to DataFrame for easier analysis
        perf_df = pd.DataFrame(self.performance_history)
        
        if len(perf_df) < 2:
            return {}
        
        # Calculate returns
        perf_df['returns'] = perf_df['total_value'].pct_change()
        
        # Basic metrics
        total_return = (perf_df['total_value'].iloc[-1] - perf_df['total_value'].iloc[0]) / perf_df['total_value'].iloc[0]
        
        # Calculate Sharpe ratio (simplified)
        if len(perf_df['returns']) > 1 and perf_df['returns'].std() > 0:
            sharpe_ratio = np.sqrt(252) * perf_df['returns'].mean() / perf_df['returns'].std()
        else:
            sharpe_ratio = 0
        
        # Calculate max drawdown
        running_max = perf_df['total_value'].expanding().max()
        drawdowns = (perf_df['total_value'] - running_max) / running_max
        max_drawdown = drawdowns.min() if not drawdowns.empty else 0
        
        # Calculate win rate from trades
        if self.trade_history:
            # Group trades by symbol and calculate P&L
            trade_pnls = []
            symbol_trades = {}
            
            for trade in self.trade_history:
                symbol = trade['symbol']
                if symbol not in symbol_trades:
                    symbol_trades[symbol] = {'buys': [], 'sells': []}
                
                if trade['type'] == 'BUY':
                    symbol_trades[symbol]['buys'].append(trade)
                else:
                    symbol_trades[symbol]['sells'].append(trade)
            
            # Calculate P&L for completed trades
            for symbol, trades in symbol_trades.items():
                buys = trades['buys']
                sells = trades['sells']
                
                # Match buys with sells (FIFO)
                buy_idx = 0
                sell_idx = 0
                
                while buy_idx < len(buys) and sell_idx < len(sells):
                    buy = buys[buy_idx]
                    sell = sells[sell_idx]
                    
                    # Calculate P&L
                    quantity = min(buy['quantity'], sell['quantity'])
                    pnl = (sell['price'] - buy['price']) * quantity - (buy['commission'] + sell['commission'])
                    
                    trade_pnls.append(pnl)
                    
                    # Update quantities
                    buy['quantity'] -= quantity
                    sell['quantity'] -= quantity
                    
                    if buy['quantity'] == 0:
                        buy_idx += 1
                    if sell['quantity'] == 0:
                        sell_idx += 1
            
            winning_trades = [pnl for pnl in trade_pnls if pnl > 0]
            win_rate = len(winning_trades) / len(trade_pnls) if trade_pnls else 0
            total_trades = len(trade_pnls)
        else:
            win_rate = 0
            total_trades = 0
        
        # Calculate concentration
        if self.positions:
            position_values = {}
            for symbol, position in self.positions.items():
                # Use average price for value calculation
                position_values[symbol] = position['quantity'] * position['avg_price']
            
            total_position_value = sum(position_values.values())
            
            if total_position_value > 0:
                concentration = {symbol: value / total_position_value 
                               for symbol, value in position_values.items()}
                max_concentration = max(concentration.values()) if concentration else 0
            else:
                concentration = {}
                max_concentration = 0
        else:
            concentration = {}
            max_concentration = 0
        
        metrics = {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': total_trades,
            'current_value': self.current_value,
            'cash_balance': self.cash,
            'positions_count': len(self.positions),
            'max_concentration': max_concentration,
            'position_concentration': concentration,
            'initial_capital': self.initial_capital,
            'unrealized_pnl': self.performance_history[-1]['unrealized_pnl'] if self.performance_history else 0
        }
        
        return metrics
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive portfolio report"""
        
        metrics = self.calculate_performance_metrics()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'portfolio_summary': {
                'current_value': self.current_value,
                'cash_balance': self.cash,
                'positions_count': len(self.positions),
                'initial_capital': self.initial_capital
            },
            'performance_metrics': metrics,
            'positions': self.get_all_positions(),
            'recent_trades': self.trade_history[-10:] if self.trade_history else [],
            'performance_history_summary': {
                'records': len(self.performance_history),
                'first_record': self.performance_history[0]['timestamp'].isoformat() if self.performance_history else None,
                'last_record': self.performance_history[-1]['timestamp'].isoformat() if self.performance_history else None
            }
        }
        
        return report
    
    def reset(self, new_capital: float = None):
        """Reset portfolio to initial state"""
        if new_capital is not None:
            self.initial_capital = new_capital
        
        self.cash = self.initial_capital
        self.positions = {}
        self.trade_history = []
        self.performance_history = []
        self.current_value = self.initial_capital
        
        logger.info(f"Portfolio reset with capital: ${self.initial_capital:.2f}")

class PortfolioManager:
    """Manager for multiple portfolios"""
    
    def __init__(self):
        self.portfolios = {}  # name -> Portfolio
        self.active_portfolio = None
        
    def create_portfolio(self, name: str, initial_capital: float = 10000.0) -> Portfolio:
        """Create a new portfolio"""
        portfolio = Portfolio(initial_capital)
        self.portfolios[name] = portfolio
        
        if self.active_portfolio is None:
            self.active_portfolio = name
        
        logger.info(f"Created portfolio '{name}' with capital ${initial_capital:.2f}")
        return portfolio
    
    def get_portfolio(self, name: str = None) -> Optional[Portfolio]:
        """Get a portfolio by name, or active portfolio if None"""
        if name is None:
            name = self.active_portfolio
        
        return self.portfolios.get(name)
    
    def set_active_portfolio(self, name: str) -> bool:
        """Set active portfolio"""
        if name in self.portfolios:
            self.active_portfolio = name
            logger.info(f"Active portfolio set to '{name}'")
            return True
        else:
            logger.error(f"Portfolio '{name}' not found")
            return False
    
    def get_all_portfolios(self) -> Dict[str, Portfolio]:
        """Get all portfolios"""
        return self.portfolios.copy()
    
    def compare_portfolios(self) -> pd.DataFrame:
        """Compare performance of all portfolios"""
        
        comparison_data = []
        
        for name, portfolio in self.portfolios.items():
            metrics = portfolio.calculate_performance_metrics()
            
            comparison_data.append({
                'Portfolio': name,
                'Current Value': portfolio.current_value,
                'Total Return': metrics.get('total_return', 0),
                'Sharpe Ratio': metrics.get('sharpe_ratio', 0),
                'Max Drawdown': metrics.get('max_drawdown', 0),
                'Win Rate': metrics.get('win_rate', 0),
                'Positions': len(portfolio.positions),
                'Active': name == self.active_portfolio
            })
        
        return pd.DataFrame(comparison_data)

# Global portfolio manager instance
portfolio_manager = PortfolioManager()

# Create default portfolio
default_portfolio = portfolio_manager.create_portfolio('default', 10000.0)
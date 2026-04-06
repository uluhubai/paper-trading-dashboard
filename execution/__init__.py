"""
Execution module for Paper Trading System
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class Order:
    """Represents a trading order"""
    
    def __init__(self, order_id: str, symbol: str, order_type: str, 
                 quantity: float, price: float, timestamp: datetime):
        self.order_id = order_id
        self.symbol = symbol
        self.order_type = order_type  # 'BUY', 'SELL'
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp
        self.status = 'PENDING'  # 'PENDING', 'FILLED', 'CANCELLED', 'REJECTED'
        self.filled_quantity = 0
        self.filled_price = 0
        self.commission = 0
        
    def fill(self, filled_price: float, filled_quantity: float = None, 
             commission: float = 0):
        """Fill the order"""
        if filled_quantity is None:
            filled_quantity = self.quantity
        
        self.filled_quantity = filled_quantity
        self.filled_price = filled_price
        self.commission = commission
        self.status = 'FILLED'
        
        logger.info(f"Order {self.order_id} filled: {filled_quantity} @ {filled_price}")
    
    def cancel(self):
        """Cancel the order"""
        self.status = 'CANCELLED'
        logger.info(f"Order {self.order_id} cancelled")
    
    def reject(self, reason: str):
        """Reject the order"""
        self.status = 'REJECTED'
        logger.info(f"Order {self.order_id} rejected: {reason}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary"""
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'order_type': self.order_type,
            'quantity': self.quantity,
            'price': self.price,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'filled_quantity': self.filled_quantity,
            'filled_price': self.filled_price,
            'commission': self.commission,
            'value': self.filled_quantity * self.filled_price if self.filled_quantity > 0 else 0
        }

class ExecutionEngine:
    """Execution engine for paper trading"""
    
    def __init__(self, commission_rate: float = 0.001, slippage: float = 0.0005):
        self.commission_rate = commission_rate
        self.slippage = slippage
        self.orders = {}
        self.order_counter = 0
        self.trade_history = []
        
    def generate_order_id(self) -> str:
        """Generate unique order ID"""
        self.order_counter += 1
        return f"ORD{self.order_counter:06d}"
    
    def create_order(self, symbol: str, order_type: str, 
                    quantity: float, price: float) -> Order:
        """Create a new order"""
        
        order_id = self.generate_order_id()
        order = Order(
            order_id=order_id,
            symbol=symbol,
            order_type=order_type,
            quantity=quantity,
            price=price,
            timestamp=datetime.now()
        )
        
        self.orders[order_id] = order
        logger.info(f"Created order {order_id}: {order_type} {quantity} {symbol} @ {price}")
        
        return order
    
    def execute_order(self, order: Order, current_price: float) -> bool:
        """Execute an order with slippage and commission"""
        
        if order.status != 'PENDING':
            logger.warning(f"Order {order.order_id} is not pending (status: {order.status})")
            return False
        
        # Apply slippage
        if order.order_type == 'BUY':
            execution_price = current_price * (1 + self.slippage)
        else:  # SELL
            execution_price = current_price * (1 - self.slippage)
        
        # Calculate commission
        order_value = order.quantity * execution_price
        commission = order_value * self.commission_rate
        
        # Fill the order
        order.fill(
            filled_price=execution_price,
            filled_quantity=order.quantity,
            commission=commission
        )
        
        # Record trade
        trade = {
            'order_id': order.order_id,
            'symbol': order.symbol,
            'type': order.order_type,
            'quantity': order.filled_quantity,
            'price': order.filled_price,
            'commission': order.commission,
            'timestamp': datetime.now(),
            'value': order.filled_quantity * order.filled_price
        }
        
        self.trade_history.append(trade)
        logger.info(f"Executed order {order.order_id}: {order.order_type} {order.quantity} "
                   f"{order.symbol} @ {execution_price:.2f} (commission: {commission:.2f})")
        
        return True
    
    def execute_market_order(self, symbol: str, order_type: str, 
                            quantity: float, current_price: float) -> Order:
        """Create and execute a market order immediately"""
        
        order = self.create_order(symbol, order_type, quantity, current_price)
        success = self.execute_order(order, current_price)
        
        if not success:
            order.reject("Execution failed")
        
        return order
    
    def execute_limit_order(self, symbol: str, order_type: str,
                           quantity: float, limit_price: float,
                           current_price: float) -> Order:
        """Create and execute a limit order if price is favorable"""
        
        order = self.create_order(symbol, order_type, quantity, limit_price)
        
        # Check if limit order can be executed
        if order_type == 'BUY' and current_price <= limit_price:
            success = self.execute_order(order, current_price)
        elif order_type == 'SELL' and current_price >= limit_price:
            success = self.execute_order(order, current_price)
        else:
            order.reject(f"Limit price not met: {current_price} vs {limit_price}")
            success = False
        
        return order
    
    def execute_stop_order(self, symbol: str, order_type: str,
                          quantity: float, stop_price: float,
                          current_price: float) -> Order:
        """Create and execute a stop order if price triggers"""
        
        order = self.create_order(symbol, order_type, quantity, stop_price)
        
        # Check if stop order should be triggered
        if order_type == 'BUY' and current_price >= stop_price:
            success = self.execute_order(order, current_price)
        elif order_type == 'SELL' and current_price <= stop_price:
            success = self.execute_order(order, current_price)
        else:
            order.reject(f"Stop price not triggered: {current_price} vs {stop_price}")
            success = False
        
        return order
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get status of an order"""
        
        if order_id in self.orders:
            return self.orders[order_id].to_dict()
        else:
            return {'error': f'Order {order_id} not found'}
    
    def get_all_orders(self) -> List[Dict[str, Any]]:
        """Get all orders"""
        
        return [order.to_dict() for order in self.orders.values()]
    
    def get_trade_history(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Get trade history, optionally filtered by symbol"""
        
        if symbol:
            return [trade for trade in self.trade_history if trade['symbol'] == symbol]
        else:
            return self.trade_history
    
    def calculate_performance(self) -> Dict[str, Any]:
        """Calculate execution performance metrics"""
        
        if not self.trade_history:
            return {'total_trades': 0, 'total_commission': 0}
        
        total_trades = len(self.trade_history)
        total_commission = sum(trade['commission'] for trade in self.trade_history)
        total_volume = sum(trade['value'] for trade in self.trade_history)
        
        # Calculate average slippage
        slippages = []
        for trade in self.trade_history:
            order = self.orders.get(trade['order_id'])
            if order and order.price > 0:
                slippage_pct = abs(trade['price'] - order.price) / order.price
                slippages.append(slippage_pct)
        
        avg_slippage = np.mean(slippages) if slippages else 0
        
        # Calculate win rate (simplified)
        profitable_trades = 0
        for i in range(1, len(self.trade_history), 2):
            if i < len(self.trade_history):
                buy_trade = self.trade_history[i-1]
                sell_trade = self.trade_history[i]
                if sell_trade['price'] > buy_trade['price']:
                    profitable_trades += 1
        
        win_rate = profitable_trades / (total_trades // 2) if total_trades >= 2 else 0
        
        return {
            'total_trades': total_trades,
            'total_commission': total_commission,
            'total_volume': total_volume,
            'average_slippage': avg_slippage,
            'win_rate': win_rate,
            'commission_rate': self.commission_rate,
            'slippage_rate': self.slippage
        }
    
    def execute_strategy_signals(self, signals: pd.DataFrame, 
                                data: pd.DataFrame,
                                capital: float,
                                max_position_size: float = 0.1) -> List[Order]:
        """Execute trading signals from a strategy"""
        
        executed_orders = []
        
        if signals.empty or 'positions' not in signals.columns:
            logger.warning("No signals or positions column found")
            return executed_orders
        
        # Get price column
        price_col = 'close' if 'close' in data.columns else 'Close'
        
        for i in range(len(signals)):
            position_change = signals['positions'].iloc[i]
            
            if position_change != 0 and i < len(data):
                symbol = 'AAPL'  # Default symbol - would need to be parameterized
                current_price = data[price_col].iloc[i]
                
                # Calculate position size
                position_value = capital * max_position_size
                quantity = position_value / current_price
                
                # Determine order type
                order_type = 'BUY' if position_change > 0 else 'SELL'
                
                # Execute market order
                order = self.execute_market_order(
                    symbol=symbol,
                    order_type=order_type,
                    quantity=quantity,
                    current_price=current_price
                )
                
                executed_orders.append(order)
                
                logger.info(f"Executed signal: {order_type} {quantity:.2f} {symbol} "
                           f"@ {current_price:.2f}")
        
        return executed_orders

# Global execution engine instance
execution_engine = ExecutionEngine()
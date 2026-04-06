"""
Risk Management module for Paper Trading System
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class RiskManager:
    """Risk management system for trading"""
    
    def __init__(self, 
                 max_position_size: float = 0.1,
                 stop_loss: float = 0.05,
                 take_profit: float = 0.10,
                 max_drawdown: float = 0.20,
                 risk_per_trade: float = 0.02):
        
        self.max_position_size = max_position_size  # Max 10% of capital per position
        self.stop_loss = stop_loss  # 5% stop loss
        self.take_profit = take_profit  # 10% take profit
        self.max_drawdown = max_drawdown  # Max 20% drawdown
        self.risk_per_trade = risk_per_trade  # 2% risk per trade
        
        self.risk_metrics = {}
        self.alerts = []
        
    def calculate_position_size(self, 
                               capital: float, 
                               entry_price: float,
                               stop_loss_price: float = None) -> float:
        """Calculate position size based on risk"""
        
        if stop_loss_price is None:
            stop_loss_price = entry_price * (1 - self.stop_loss)
        
        # Calculate risk amount
        risk_amount = capital * self.risk_per_trade
        
        # Calculate position size based on stop loss
        risk_per_share = entry_price - stop_loss_price
        if risk_per_share <= 0:
            logger.warning("Risk per share is zero or negative")
            return 0
        
        position_size = risk_amount / risk_per_share
        
        # Apply max position size limit
        max_position_value = capital * self.max_position_size
        max_position_by_value = max_position_value / entry_price
        
        position_size = min(position_size, max_position_by_value)
        
        logger.info(f"Position size calculated: {position_size:.2f} shares "
                   f"(risk: ${risk_amount:.2f}, max: {max_position_by_value:.2f})")
        
        return position_size
    
    def check_stop_loss(self, entry_price: float, current_price: float) -> bool:
        """Check if stop loss is hit"""
        loss_pct = (current_price - entry_price) / entry_price
        stop_loss_hit = loss_pct <= -self.stop_loss
        
        if stop_loss_hit:
            logger.warning(f"Stop loss hit: {loss_pct:.2%} loss "
                          f"(entry: {entry_price:.2f}, current: {current_price:.2f})")
            self.alerts.append({
                'type': 'STOP_LOSS',
                'entry_price': entry_price,
                'current_price': current_price,
                'loss_pct': loss_pct
            })
        
        return stop_loss_hit
    
    def check_take_profit(self, entry_price: float, current_price: float) -> bool:
        """Check if take profit is hit"""
        profit_pct = (current_price - entry_price) / entry_price
        take_profit_hit = profit_pct >= self.take_profit
        
        if take_profit_hit:
            logger.info(f"Take profit hit: {profit_pct:.2%} profit "
                       f"(entry: {entry_price:.2f}, current: {current_price:.2f})")
            self.alerts.append({
                'type': 'TAKE_PROFIT',
                'entry_price': entry_price,
                'current_price': current_price,
                'profit_pct': profit_pct
            })
        
        return take_profit_hit
    
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk (VaR)"""
        
        if len(returns) == 0:
            return 0
        
        # Historical VaR
        var = np.percentile(returns, (1 - confidence_level) * 100)
        
        logger.info(f"VaR ({confidence_level:.0%}): {var:.4f}")
        
        return var
    
    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (CVaR)"""
        
        if len(returns) == 0:
            return 0
        
        var = self.calculate_var(returns, confidence_level)
        cvar = returns[returns <= var].mean()
        
        logger.info(f"CVaR ({confidence_level:.0%}): {cvar:.4f}")
        
        return cvar
    
    def calculate_max_drawdown(self, equity_curve: pd.Series) -> Dict[str, float]:
        """Calculate maximum drawdown"""
        
        if len(equity_curve) == 0:
            return {'max_drawdown': 0, 'drawdown_duration': 0}
        
        # Calculate running maximum
        running_max = equity_curve.expanding().max()
        
        # Calculate drawdown
        drawdown = (equity_curve - running_max) / running_max
        
        # Find maximum drawdown
        max_drawdown = drawdown.min()
        max_drawdown_idx = drawdown.idxmin() if hasattr(drawdown, 'idxmin') else 0
        
        # Calculate drawdown duration
        drawdown_start = None
        drawdown_duration = 0
        
        for i in range(len(drawdown)):
            if drawdown.iloc[i] < 0 and drawdown_start is None:
                drawdown_start = i
            elif drawdown.iloc[i] >= 0 and drawdown_start is not None:
                duration = i - drawdown_start
                if duration > drawdown_duration:
                    drawdown_duration = duration
                drawdown_start = None
        
        if drawdown_start is not None:
            duration = len(drawdown) - drawdown_start
            if duration > drawdown_duration:
                drawdown_duration = duration
        
        result = {
            'max_drawdown': max_drawdown,
            'max_drawdown_idx': max_drawdown_idx,
            'drawdown_duration': drawdown_duration
        }
        
        logger.info(f"Max drawdown: {max_drawdown:.2%}, "
                   f"Duration: {drawdown_duration} periods")
        
        return result
    
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        
        if len(returns) == 0 or returns.std() == 0:
            return 0
        
        excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
        sharpe = np.sqrt(252) * excess_returns.mean() / returns.std()
        
        logger.info(f"Sharpe ratio: {sharpe:.4f}")
        
        return sharpe
    
    def calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio (downside risk only)"""
        
        if len(returns) == 0:
            return 0
        
        excess_returns = returns - risk_free_rate / 252
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0
        
        sortino = np.sqrt(252) * excess_returns.mean() / downside_returns.std()
        
        logger.info(f"Sortino ratio: {sortino:.4f}")
        
        return sortino
    
    def portfolio_risk_analysis(self, 
                               positions: Dict[str, float],
                               prices: Dict[str, float],
                               capital: float) -> Dict[str, Any]:
        """Analyze portfolio risk"""
        
        total_value = capital
        position_values = {}
        
        # Calculate position values
        for symbol, quantity in positions.items():
            if symbol in prices and quantity > 0:
                position_value = quantity * prices[symbol]
                position_values[symbol] = position_value
                total_value += position_value
        
        # Calculate concentration risk
        concentration_risk = {}
        for symbol, value in position_values.items():
            concentration = value / total_value
            concentration_risk[symbol] = concentration
            
            if concentration > self.max_position_size:
                self.alerts.append({
                    'type': 'CONCENTRATION_RISK',
                    'symbol': symbol,
                    'concentration': concentration,
                    'limit': self.max_position_size
                })
        
        # Calculate portfolio beta (simplified)
        portfolio_beta = sum(concentration_risk.values())  # Placeholder
        
        result = {
            'total_value': total_value,
            'capital': capital,
            'positions': len(positions),
            'position_values': position_values,
            'concentration_risk': concentration_risk,
            'portfolio_beta': portfolio_beta,
            'alerts': self.alerts.copy()
        }
        
        logger.info(f"Portfolio risk analysis: {len(positions)} positions, "
                   f"total value: ${total_value:.2f}")
        
        return result
    
    def check_risk_limits(self, 
                         equity_curve: pd.Series,
                         current_drawdown: float = None) -> List[Dict[str, Any]]:
        """Check all risk limits"""
        
        alerts = []
        
        # Check max drawdown
        if current_drawdown is None:
            drawdown_info = self.calculate_max_drawdown(equity_curve)
            current_drawdown = abs(drawdown_info['max_drawdown'])
        
        if current_drawdown > self.max_drawdown:
            alerts.append({
                'type': 'MAX_DRAWDOWN_EXCEEDED',
                'current_drawdown': current_drawdown,
                'limit': self.max_drawdown
            })
            logger.warning(f"Max drawdown exceeded: {current_drawdown:.2%} > {self.max_drawdown:.2%}")
        
        # Check daily loss limit (simplified)
        if len(equity_curve) >= 2:
            daily_return = (equity_curve.iloc[-1] - equity_curve.iloc[-2]) / equity_curve.iloc[-2]
            daily_loss_limit = -0.05  # 5% daily loss limit
            
            if daily_return < daily_loss_limit:
                alerts.append({
                    'type': 'DAILY_LOSS_LIMIT_EXCEEDED',
                    'daily_return': daily_return,
                    'limit': daily_loss_limit
                })
                logger.warning(f"Daily loss limit exceeded: {daily_return:.2%} < {daily_loss_limit:.2%}")
        
        return alerts
    
    def get_risk_report(self) -> Dict[str, Any]:
        """Generate comprehensive risk report"""
        
        report = {
            'risk_parameters': {
                'max_position_size': self.max_position_size,
                'stop_loss': self.stop_loss,
                'take_profit': self.take_profit,
                'max_drawdown': self.max_drawdown,
                'risk_per_trade': self.risk_per_trade
            },
            'risk_metrics': self.risk_metrics,
            'alerts': self.alerts,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        return report

# Global risk manager instance
risk_manager = RiskManager()
"""
Backtesting module for Paper Trading System
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
import logging

logger = logging.getLogger(__name__)

class BacktestResult:
    """Container for backtest results"""
    
    def __init__(self, 
                 strategy_name: str,
                 initial_capital: float,
                 final_capital: float,
                 total_return: float,
                 sharpe_ratio: float,
                 max_drawdown: float,
                 total_trades: int,
                 winning_trades: int,
                 losing_trades: int,
                 win_rate: float,
                 profit_factor: float,
                 avg_win: float,
                 avg_loss: float,
                 equity_curve: pd.Series,
                 trades: List[Dict[str, Any]]):
        
        self.strategy_name = strategy_name
        self.initial_capital = initial_capital
        self.final_capital = final_capital
        self.total_return = total_return
        self.sharpe_ratio = sharpe_ratio
        self.max_drawdown = max_drawdown
        self.total_trades = total_trades
        self.winning_trades = winning_trades
        self.losing_trades = losing_trades
        self.win_rate = win_rate
        self.profit_factor = profit_factor
        self.avg_win = avg_win
        self.avg_loss = avg_loss
        self.equity_curve = equity_curve
        self.trades = trades
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'strategy_name': self.strategy_name,
            'initial_capital': self.initial_capital,
            'final_capital': self.final_capital,
            'total_return': self.total_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'equity_curve_length': len(self.equity_curve),
            'trades_count': len(self.trades)
        }
    
    def summary(self) -> str:
        """Generate summary string"""
        return (f"Strategy: {self.strategy_name}\n"
                f"Total Return: {self.total_return:.2%}\n"
                f"Sharpe Ratio: {self.sharpe_ratio:.2f}\n"
                f"Max Drawdown: {self.max_drawdown:.2%}\n"
                f"Win Rate: {self.win_rate:.2%}\n"
                f"Total Trades: {self.total_trades}")

class BacktestingEngine:
    """Backtesting engine for trading strategies"""
    
    def __init__(self, 
                 initial_capital: float = 10000.0,
                 commission: float = 0.001,
                 slippage: float = 0.0005):
        
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.results = {}
        
    def run_backtest(self,
                    data: pd.DataFrame,
                    strategy_func: Callable,
                    strategy_params: Dict[str, Any] = None) -> BacktestResult:
        """Run backtest for a strategy"""
        
        logger.info(f"Starting backtest for strategy")
        
        if strategy_params is None:
            strategy_params = {}
        
        # Generate signals
        signals = strategy_func(data, **strategy_params)
        
        if signals is None or signals.empty:
            logger.error("No signals generated")
            return None
        
        # Initialize tracking variables
        capital = self.initial_capital
        position = 0
        entry_price = 0
        trades = []
        equity_curve = []
        
        # Get price column
        price_col = 'close' if 'close' in data.columns else 'Close'
        
        # Run backtest
        for i in range(len(signals)):
            current_price = data[price_col].iloc[i]
            signal = signals['signal'].iloc[i] if 'signal' in signals.columns else 0
            
            # Check for position exit
            if position > 0 and signal == -1:
                # Sell position
                exit_price = current_price * (1 - self.slippage)
                exit_value = position * exit_price
                commission = exit_value * self.commission
                
                capital += exit_value - commission
                
                # Calculate trade P&L
                trade_pnl = exit_value - (position * entry_price) - commission
                trade_return = trade_pnl / (position * entry_price)
                
                trades.append({
                    'type': 'SELL',
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'quantity': position,
                    'pnl': trade_pnl,
                    'return': trade_return,
                    'timestamp': data.index[i] if hasattr(data.index[i], 'isoformat') else str(data.index[i])
                })
                
                position = 0
                entry_price = 0
                
                logger.debug(f"Trade closed: P&L ${trade_pnl:.2f} ({trade_return:.2%})")
            
            # Check for position entry
            elif position == 0 and signal == 1:
                # Calculate position size (simplified - 10% of capital)
                position_value = capital * 0.1
                position = position_value / current_price
                
                # Apply slippage and commission
                entry_price = current_price * (1 + self.slippage)
                entry_cost = position * entry_price
                commission = entry_cost * self.commission
                
                capital -= entry_cost + commission
                
                trades.append({
                    'type': 'BUY',
                    'entry_price': entry_price,
                    'quantity': position,
                    'cost': entry_cost + commission,
                    'timestamp': data.index[i] if hasattr(data.index[i], 'isoformat') else str(data.index[i])
                })
                
                logger.debug(f"Trade opened: {position:.2f} shares @ {entry_price:.2f}")
            
            # Calculate current portfolio value
            current_value = capital + (position * current_price if position > 0 else 0)
            equity_curve.append(current_value)
        
        # Close any open position at the end
        if position > 0:
            exit_price = data[price_col].iloc[-1] * (1 - self.slippage)
            exit_value = position * exit_price
            commission = exit_value * self.commission
            
            capital += exit_value - commission
            
            trade_pnl = exit_value - (position * entry_price) - commission
            trade_return = trade_pnl / (position * entry_price)
            
            trades.append({
                'type': 'SELL',
                'entry_price': entry_price,
                'exit_price': exit_price,
                'quantity': position,
                'pnl': trade_pnl,
                'return': trade_return,
                'timestamp': data.index[-1] if hasattr(data.index[-1], 'isoformat') else str(data.index[-1])
            })
            
            logger.debug(f"Final trade closed: P&L ${trade_pnl:.2f} ({trade_return:.2%})")
        
        # Calculate performance metrics
        final_capital = equity_curve[-1] if equity_curve else self.initial_capital
        total_return = (final_capital - self.initial_capital) / self.initial_capital
        
        # Calculate equity curve returns
        equity_series = pd.Series(equity_curve, index=data.index[:len(equity_curve)])
        returns = equity_series.pct_change().dropna()
        
        # Calculate Sharpe ratio
        if len(returns) > 1 and returns.std() > 0:
            sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std()
        else:
            sharpe_ratio = 0
        
        # Calculate max drawdown
        running_max = equity_series.expanding().max()
        drawdowns = (equity_series - running_max) / running_max
        max_drawdown = drawdowns.min() if not drawdowns.empty else 0
        
        # Calculate trade statistics
        closed_trades = [t for t in trades if 'pnl' in t]
        winning_trades = [t for t in closed_trades if t['pnl'] > 0]
        losing_trades = [t for t in closed_trades if t['pnl'] <= 0]
        
        total_trades = len(closed_trades)
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        # Calculate profit factor
        total_profit = sum(t['pnl'] for t in winning_trades) if winning_trades else 0
        total_loss = abs(sum(t['pnl'] for t in losing_trades)) if losing_trades else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # Calculate average win/loss
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        # Create result object
        result = BacktestResult(
            strategy_name=strategy_params.get('name', 'Unknown Strategy'),
            initial_capital=self.initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            total_trades=total_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_win=avg_win,
            avg_loss=avg_loss,
            equity_curve=equity_series,
            trades=trades
        )
        
        logger.info(f"Backtest completed: {total_return:.2%} return, "
                   f"Sharpe: {sharpe_ratio:.2f}, Trades: {total_trades}")
        
        return result
    
    def run_multiple_strategies(self,
                               data: pd.DataFrame,
                               strategies: Dict[str, Tuple[Callable, Dict[str, Any]]]) -> Dict[str, BacktestResult]:
        """Run backtest for multiple strategies"""
        
        results = {}
        
        for strategy_name, (strategy_func, params) in strategies.items():
            logger.info(f"Running backtest for strategy: {strategy_name}")
            
            result = self.run_backtest(data, strategy_func, params)
            if result:
                results[strategy_name] = result
                self.results[strategy_name] = result
        
        return results
    
    def compare_strategies(self, results: Dict[str, BacktestResult]) -> pd.DataFrame:
        """Compare multiple strategy results"""
        
        comparison_data = []
        
        for strategy_name, result in results.items():
            comparison_data.append({
                'Strategy': strategy_name,
                'Total Return': result.total_return,
                'Sharpe Ratio': result.sharpe_ratio,
                'Max Drawdown': result.max_drawdown,
                'Win Rate': result.win_rate,
                'Total Trades': result.total_trades,
                'Profit Factor': result.profit_factor,
                'Final Capital': result.final_capital
            })
        
        return pd.DataFrame(comparison_data)
    
    def optimize_parameters(self,
                           data: pd.DataFrame,
                           strategy_func: Callable,
                           param_grid: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Optimize strategy parameters using grid search"""
        
        best_params = None
        best_result = None
        best_sharpe = -float('inf')
        
        # Generate all parameter combinations
        from itertools import product
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        total_combinations = np.prod([len(vals) for vals in param_values])
        logger.info(f"Testing {total_combinations} parameter combinations")
        
        for i, combination in enumerate(product(*param_values)):
            params = dict(zip(param_names, combination))
            
            # Run backtest with these parameters
            result = self.run_backtest(data, strategy_func, params)
            
            if result and result.sharpe_ratio > best_sharpe:
                best_sharpe = result.sharpe_ratio
                best_result = result
                best_params = params
            
            if i % 10 == 0:
                logger.info(f"Tested {i}/{total_combinations} combinations")
        
        logger.info(f"Best parameters: {best_params}, Sharpe: {best_sharpe:.4f}")
        
        return {
            'best_params': best_params,
            'best_result': best_result,
            'best_sharpe': best_sharpe
        }
    
    def calculate_metrics(self, equity_curve: pd.Series) -> Dict[str, float]:
        """Calculate various performance metrics"""
        
        if len(equity_curve) < 2:
            return {}
        
        returns = equity_curve.pct_change().dropna()
        
        metrics = {
            'total_return': (equity_curve.iloc[-1] - equity_curve.iloc[0]) / equity_curve.iloc[0],
            'annual_return': ((1 + returns.mean()) ** 252 - 1) if len(returns) > 0 else 0,
            'annual_volatility': returns.std() * np.sqrt(252) if len(returns) > 0 else 0,
            'sharpe_ratio': np.sqrt(252) * returns.mean() / returns.std() if len(returns) > 1 and returns.std() > 0 else 0,
            'sortino_ratio': self._calculate_sortino(returns),
            'calmar_ratio': self._calculate_calmar(equity_curve),
            'max_drawdown': self._calculate_max_drawdown(equity_curve),
            'var_95': np.percentile(returns, 5) if len(returns) > 0 else 0,
            'cvar_95': returns[returns <= np.percentile(returns, 5)].mean() if len(returns) > 0 else 0
        }
        
        return metrics
    
    def _calculate_sortino(self, returns: pd.Series) -> float:
        """Calculate Sortino ratio"""
        if len(returns) == 0:
            return 0
        
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0
        
        return np.sqrt(252) * returns.mean() / downside_returns.std()
    
    def _calculate_calmar(self, equity_curve: pd.Series) -> float:
        """Calculate Calmar ratio"""
        if len(equity_curve) < 2:
            return 0
        
        total_return = (equity_curve.iloc[-1] - equity_curve.iloc[0]) / equity_curve.iloc[0]
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        
        if max_drawdown == 0:
            return float('inf')
        
        return total_return / abs(max_drawdown)
    
    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown"""
        if len(equity_curve) == 0:
            return 0
        
        running_max = equity_curve.expanding().max()
        drawdowns = (equity_curve - running_max) / running_max
        return drawdowns.min() if not drawdowns.empty else 0
    
    def generate_report(self, results: Dict[str, BacktestResult]) -> Dict[str, Any]:
        """Generate comprehensive backtest report"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'initial_capital': self.initial_capital,
            'commission': self.commission,
            'slippage': self.slippage,
            'strategies_tested': len(results),
            'results': {name: result.to_dict() for name, result in results.items()},
            'comparison': self.compare_strategies(results).to_dict('records')
        }
        
        return report

# Global backtesting engine instance
backtesting_engine = BacktestingEngine()
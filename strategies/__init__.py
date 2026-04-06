"""
Strategies module for Paper Trading System
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Callable
import logging

logger = logging.getLogger(__name__)

class BaseStrategy:
    """Base class for all trading strategies"""
    
    def __init__(self, name: str = "Base Strategy"):
        self.name = name
        self.parameters = {}
        self.signals = None
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals from data"""
        raise NotImplementedError("Subclasses must implement generate_signals")
    
    def backtest(self, data: pd.DataFrame, initial_capital: float = 10000.0) -> Dict[str, Any]:
        """Backtest the strategy"""
        signals = self.generate_signals(data)
        
        if signals is None or signals.empty:
            return {'error': 'No signals generated'}
        
        # Simple backtest implementation
        capital = initial_capital
        position = 0
        trades = []
        equity_curve = []
        
        for i in range(len(signals)):
            price = data['close'].iloc[i] if 'close' in data.columns else data['Close'].iloc[i]
            signal = signals['signal'].iloc[i] if 'signal' in signals.columns else 0
            
            if signal == 1 and position == 0:  # Buy
                shares = capital * 0.1 / price  # Use 10% of capital
                cost = shares * price
                capital -= cost
                position = shares
                trades.append({
                    'type': 'BUY',
                    'price': price,
                    'shares': shares,
                    'timestamp': data.index[i] if hasattr(data.index[i], 'isoformat') else str(data.index[i])
                })
                
            elif signal == -1 and position > 0:  # Sell
                proceeds = position * price
                capital += proceeds
                trades.append({
                    'type': 'SELL',
                    'price': price,
                    'shares': position,
                    'timestamp': data.index[i] if hasattr(data.index[i], 'isoformat') else str(data.index[i])
                })
                position = 0
            
            # Current portfolio value
            current_value = capital + (position * price if position > 0 else 0)
            equity_curve.append(current_value)
        
        # Calculate performance metrics
        equity_series = pd.Series(equity_curve, index=data.index[:len(equity_curve)])
        returns = equity_series.pct_change().dropna()
        
        total_return = (equity_curve[-1] - initial_capital) / initial_capital if equity_curve else 0
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 1 else 0
        
        # Calculate max drawdown
        running_max = equity_series.expanding().max()
        drawdowns = (equity_series - running_max) / running_max
        max_drawdown = drawdowns.min() if not drawdowns.empty else 0
        
        return {
            'strategy_name': self.name,
            'initial_capital': initial_capital,
            'final_value': equity_curve[-1] if equity_curve else initial_capital,
            'total_return': total_return,
            'total_trades': len(trades),
            'winning_trades': sum(1 for trade in trades if trade.get('profit', 0) > 0),
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'equity_curve': equity_curve,
            'trades': trades,
            'signals': signals
        }

class MovingAverageCrossover(BaseStrategy):
    """Moving Average Crossover Strategy"""
    
    def __init__(self, short_window: int = 10, long_window: int = 30):
        super().__init__(f"MA Crossover ({short_window}/{long_window})")
        self.short_window = short_window
        self.long_window = long_window
        self.parameters = {
            'short_window': short_window,
            'long_window': long_window
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate signals based on MA crossover"""
        
        # Use appropriate price column
        price_col = 'close' if 'close' in data.columns else 'Close'
        
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data[price_col]
        
        # Calculate moving averages
        signals['short_ma'] = data[price_col].rolling(window=self.short_window, min_periods=1).mean()
        signals['long_ma'] = data[price_col].rolling(window=self.long_window, min_periods=1).mean()
        
        # Generate signals
        signals['signal'] = 0
        signals['signal'][self.short_window:] = np.where(
            signals['short_ma'][self.short_window:] > signals['long_ma'][self.short_window:], 
            1.0, 0.0
        )
        
        # Generate positions (1 for buy, -1 for sell, 0 for hold)
        signals['positions'] = signals['signal'].diff()
        
        logger.info(f"Generated {len(signals[signals['positions'] != 0])} trading signals")
        
        return signals

class MeanReversion(BaseStrategy):
    """Mean Reversion Strategy using Bollinger Bands"""
    
    def __init__(self, window: int = 20, num_std: float = 2.0):
        super().__init__(f"Mean Reversion BB ({window}, {num_std}σ)")
        self.window = window
        self.num_std = num_std
        self.parameters = {
            'window': window,
            'num_std': num_std
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate signals based on Bollinger Bands"""
        
        price_col = 'close' if 'close' in data.columns else 'Close'
        
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data[price_col]
        
        # Calculate Bollinger Bands
        signals['sma'] = data[price_col].rolling(window=self.window, min_periods=1).mean()
        signals['std'] = data[price_col].rolling(window=self.window, min_periods=1).std()
        
        signals['upper_band'] = signals['sma'] + (signals['std'] * self.num_std)
        signals['lower_band'] = signals['sma'] - (signals['std'] * self.num_std)
        
        # Generate signals
        signals['signal'] = 0
        
        # Buy when price crosses below lower band
        signals.loc[data[price_col] < signals['lower_band'], 'signal'] = 1
        
        # Sell when price crosses above upper band
        signals.loc[data[price_col] > signals['upper_band'], 'signal'] = -1
        
        # Generate positions
        signals['positions'] = signals['signal'].diff()
        
        logger.info(f"Generated {len(signals[signals['positions'] != 0])} mean reversion signals")
        
        return signals

class MLStrategy(BaseStrategy):
    """Machine Learning based strategy"""
    
    def __init__(self, ml_model: Any = None, threshold: float = 0.0):
        super().__init__("ML Strategy")
        self.ml_model = ml_model
        self.threshold = threshold
        self.parameters = {
            'threshold': threshold
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate signals using ML model predictions"""
        
        if self.ml_model is None:
            logger.error("ML model not provided")
            return pd.DataFrame()
        
        signals = pd.DataFrame(index=data.index)
        
        try:
            # Get predictions from ML model
            # This assumes the ML model has a predict method
            if hasattr(self.ml_model, 'predict'):
                # Prepare features for prediction
                # This would need to match the training feature format
                features = self._prepare_features(data)
                predictions = self.ml_model.predict(features)
                
                # Generate signals based on predictions
                signals['prediction'] = predictions
                signals['signal'] = 0
                signals.loc[predictions > self.threshold, 'signal'] = 1
                signals.loc[predictions < -self.threshold, 'signal'] = -1
                
                # Generate positions
                signals['positions'] = signals['signal'].diff()
                
                logger.info(f"Generated {len(signals[signals['positions'] != 0])} ML signals")
                
            else:
                logger.error("ML model doesn't have predict method")
                
        except Exception as e:
            logger.error(f"Error generating ML signals: {e}")
        
        return signals
    
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for ML model prediction"""
        # This is a placeholder - actual implementation would depend on the ML model
        # For now, return a simple feature set
        features = []
        
        if 'close' in data.columns:
            price = data['close'].values
        elif 'Close' in data.columns:
            price = data['Close'].values
        else:
            return np.array([])
        
        # Simple features: returns and moving averages
        returns = np.diff(price) / price[:-1]
        returns = np.append(returns, 0)  # Pad last value
        
        sma_10 = pd.Series(price).rolling(window=10, min_periods=1).mean().values
        sma_20 = pd.Series(price).rolling(window=20, min_periods=1).mean().values
        
        # Combine features
        features = np.column_stack([returns, sma_10, sma_20])
        
        return features

class StrategyManager:
    """Manager for multiple trading strategies"""
    
    def __init__(self):
        self.strategies = {}
        self.active_strategies = []
        
    def register_strategy(self, name: str, strategy: BaseStrategy):
        """Register a strategy"""
        self.strategies[name] = strategy
        logger.info(f"Registered strategy: {name}")
    
    def activate_strategy(self, name: str):
        """Activate a strategy"""
        if name in self.strategies:
            self.active_strategies.append(name)
            logger.info(f"Activated strategy: {name}")
        else:
            logger.error(f"Strategy not found: {name}")
    
    def deactivate_strategy(self, name: str):
        """Deactivate a strategy"""
        if name in self.active_strategies:
            self.active_strategies.remove(name)
            logger.info(f"Deactivated strategy: {name}")
    
    def run_strategies(self, data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Run all active strategies on data"""
        results = {}
        
        for name in self.active_strategies:
            if name in self.strategies:
                strategy = self.strategies[name]
                signals = strategy.generate_signals(data)
                results[name] = signals
                logger.info(f"Ran strategy {name}: {len(signals[signals['positions'] != 0])} signals")
        
        return results
    
    def combine_signals(self, signals_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Combine signals from multiple strategies"""
        
        if not signals_dict:
            return pd.DataFrame()
        
        # Get first strategy's index as reference
        first_key = list(signals_dict.keys())[0]
        combined = pd.DataFrame(index=signals_dict[first_key].index)
        
        # Combine signals (simple voting)
        for name, signals in signals_dict.items():
            if 'signal' in signals.columns:
                combined[name] = signals['signal']
        
        # Calculate combined signal (average)
        if not combined.empty:
            combined['combined_signal'] = combined.mean(axis=1)
            # Threshold for final signal
            combined['final_signal'] = 0
            combined.loc[combined['combined_signal'] > 0.5, 'final_signal'] = 1
            combined.loc[combined['combined_signal'] < -0.5, 'final_signal'] = -1
        
        return combined

# Global strategy manager instance
strategy_manager = StrategyManager()

# Register default strategies
strategy_manager.register_strategy('ma_crossover_10_30', MovingAverageCrossover(10, 30))
strategy_manager.register_strategy('ma_crossover_20_50', MovingAverageCrossover(20, 50))
strategy_manager.register_strategy('mean_reversion_bb', MeanReversion(20, 2.0))

# Activate default strategies
strategy_manager.activate_strategy('ma_crossover_10_30')
strategy_manager.activate_strategy('mean_reversion_bb')
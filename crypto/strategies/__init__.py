"""
Crypto Trading Strategies
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class CryptoStrategies:
    """Crypto-specific trading strategies"""
    
    def volatility_breakout(self, data: pd.DataFrame, lookback: int = 20) -> pd.Series:
        """Volatility breakout for crypto"""
        if len(data) < lookback:
            return pd.Series(0, index=data.index)
        
        returns = data['close'].pct_change()
        volatility = returns.rolling(window=lookback).std()
        
        upper_band = data['close'].rolling(window=lookback).mean() + (volatility * 2)
        lower_band = data['close'].rolling(window=lookback).mean() - (volatility * 2)
        
        signals = pd.Series(0, index=data.index)
        signals[data['close'] > upper_band] = 1
        signals[data['close'] < lower_band] = -1
        
        return signals
    
    def mean_reversion(self, data: pd.DataFrame, lookback: int = 50) -> pd.Series:
        """Mean reversion for crypto"""
        if len(data) < lookback:
            return pd.Series(0, index=data.index)
        
        sma = data['close'].rolling(window=lookback).mean()
        std = data['close'].rolling(window=lookback).std()
        
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        
        signals = pd.Series(0, index=data.index)
        signals[data['close'] <= lower_band] = 1
        signals[data['close'] >= upper_band] = -1
        
        return signals
    
    def trend_following(self, data: pd.DataFrame) -> pd.Series:
        """Trend following with EMAs"""
        if len(data) < 26:
            return pd.Series(0, index=data.index)
        
        ema_12 = data['close'].ewm(span=12, adjust=False).mean()
        ema_26 = data['close'].ewm(span=26, adjust=False).mean()
        
        signals = pd.Series(0, index=data.index)
        signals[(ema_12 > ema_26) & (ema_12.shift() <= ema_26.shift())] = 1
        signals[(ema_12 < ema_26) & (ema_12.shift() >= ema_26.shift())] = -1
        
        return signals

# Create global instance
crypto_strategies = CryptoStrategies()

__all__ = ['CryptoStrategies', 'crypto_strategies']
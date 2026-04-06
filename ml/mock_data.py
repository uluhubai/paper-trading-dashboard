
"""
Mock data for ML module testing
"""

import pandas as pd
import numpy as np

def create_mock_data(n_days=100):
    """Create mock financial data for testing"""
    
    dates = pd.date_range(start='2024-01-01', periods=n_days, freq='D')
    
    # Create price data with some trend and noise
    np.random.seed(42)
    base_price = 100
    returns = np.random.randn(n_days) * 0.02  # 2% daily volatility
    prices = base_price * np.exp(np.cumsum(returns))
    
    data = pd.DataFrame({
        'open': prices * (1 + np.random.randn(n_days) * 0.01),
        'high': prices * (1 + np.random.randn(n_days) * 0.015),
        'low': prices * (1 + np.random.randn(n_days) * 0.015),
        'close': prices,
        'volume': np.random.randint(1000, 10000, n_days)
    }, index=dates)
    
    return data

def create_mock_features(data):
    """Create mock features for testing"""
    
    # Simple moving averages
    data['sma_20'] = data['close'].rolling(window=20).mean()
    data['ema_20'] = data['close'].ewm(span=20).mean()
    data['rsi_14'] = 50 + np.random.randn(len(data)) * 10  # Mock RSI
    
    return data

if __name__ == "__main__":
    data = create_mock_data()
    features = create_mock_features(data)
    print(f"Created mock data with {len(data)} rows")
    print(f"Features: {list(features.columns)}")

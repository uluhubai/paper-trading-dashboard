"""
Data Preprocessing for Machine Learning Trading Models
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class TradingDataPreprocessor:
    """Preprocess financial data for machine learning models"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.scalers: Dict[str, Any] = {}
        self.feature_columns: List[str] = []
        self.target_columns: List[str] = []
        
    def create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create features for machine learning models"""
        
        if data.empty:
            return data
        
        result = data.copy()
        
        # Price-based features
        result['returns'] = result['close'].pct_change()
        result['log_returns'] = np.log(result['close'] / result['close'].shift(1))
        result['price_change'] = result['close'].diff()
        result['gap'] = (result['open'] - result['close'].shift(1)) / result['close'].shift(1)
        
        # Volume features
        result['volume_change'] = result['volume'].pct_change()
        result['volume_ratio'] = result['volume'] / result['volume'].rolling(20).mean()
        result['dollar_volume'] = result['close'] * result['volume']
        
        # Technical indicators (simplified - would use TA-Lib in production)
        # Moving averages
        for window in [5, 10, 20, 50, 100, 200]:
            result[f'sma_{window}'] = result['close'].rolling(window=window).mean()
            result[f'ema_{window}'] = result['close'].ewm(span=window, adjust=False).mean()
            result[f'price_sma_ratio_{window}'] = result['close'] / result[f'sma_{window}']
        
        # Volatility
        result['volatility_20'] = result['returns'].rolling(window=20).std()
        result['volatility_50'] = result['returns'].rolling(window=50).std()
        result['atr_14'] = self._calculate_atr(result, window=14)
        
        # Momentum indicators
        result['rsi_14'] = self._calculate_rsi(result['close'], window=14)
        result['macd'] = result['ema_20'] - result['ema_20']
        result['macd_signal'] = result['macd'].ewm(span=9, adjust=False).mean()
        result['macd_hist'] = result['macd'] - result['macd_signal']
        
        # Support/resistance
        result['high_20'] = result['high'].rolling(window=20).max()
        result['low_20'] = result['low'].rolling(window=20).min()
        result['high_low_range'] = (result['high_20'] - result['low_20']) / result['close']
        
        # Statistical features
        result['skew_20'] = result['returns'].rolling(window=20).skew()
        result['kurtosis_20'] = result['returns'].rolling(window=20).kurt()
        
        # Target variable: Future returns (1-day, 5-day, 10-day ahead)
        result['target_1d'] = result['close'].shift(-1) / result['close'] - 1
        result['target_5d'] = result['close'].shift(-5) / result['close'] - 1
        result['target_10d'] = result['close'].shift(-10) / result['close'] - 1
        
        # Binary classification target (up/down)
        result['target_binary_1d'] = (result['target_1d'] > 0).astype(int)
        
        # Drop NaN values
        result = result.dropna()
        
        # Store feature columns
        self.feature_columns = [col for col in result.columns 
                               if col.startswith(('sma_', 'ema_', 'price_sma_ratio_', 
                                                'volatility_', 'atr_', 'rsi_', 'macd',
                                                'high_', 'low_', 'skew_', 'kurtosis_',
                                                'returns', 'log_returns', 'price_change',
                                                'gap', 'volume_', 'dollar_volume'))]
        
        self.target_columns = [col for col in result.columns if col.startswith('target_')]
        
        logger.info(f"Created {len(self.feature_columns)} features and {len(self.target_columns)} targets")
        
        return result
    
    def _calculate_atr(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(window=window).mean()
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def split_data(self, data: pd.DataFrame, 
                  test_size: float = 0.2,
                  time_based: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split data into train and test sets"""
        
        if time_based:
            # Time-based split (for time series)
            split_idx = int(len(data) * (1 - test_size))
            train_data = data.iloc[:split_idx]
            test_data = data.iloc[split_idx:]
        else:
            # Random split (for non-time series)
            from sklearn.model_selection import train_test_split
            train_data, test_data = train_test_split(data, test_size=test_size, shuffle=False)
        
        logger.info(f"Split data: {len(train_data)} train, {len(test_data)} test")
        
        return train_data, test_data
    
    def scale_features(self, train_data: pd.DataFrame, 
                      test_data: pd.DataFrame = None,
                      method: str = 'standard') -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Scale features for machine learning"""
        
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown scaling method: {method}")
        
        # Scale features
        X_train_scaled = scaler.fit_transform(train_data[self.feature_columns])
        train_data_scaled = train_data.copy()
        train_data_scaled[self.feature_columns] = X_train_scaled
        
        # Store scaler
        self.scalers[method] = scaler
        
        if test_data is not None:
            X_test_scaled = scaler.transform(test_data[self.feature_columns])
            test_data_scaled = test_data.copy()
            test_data_scaled[self.feature_columns] = X_test_scaled
        else:
            test_data_scaled = None
        
        logger.info(f"Features scaled using {method} scaler")
        
        return train_data_scaled, test_data_scaled
    
    def create_sequences(self, data: pd.DataFrame, 
                        sequence_length: int = 60,
                        target_col: str = 'target_1d') -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for time series models (LSTM, etc.)"""
        
        if target_col not in data.columns:
            raise ValueError(f"Target column {target_col} not found in data")
        
        X, y = [], []
        
        for i in range(len(data) - sequence_length):
            # Features sequence
            X_seq = data[self.feature_columns].iloc[i:i+sequence_length].values
            # Target (next value after sequence)
            y_val = data[target_col].iloc[i+sequence_length]
            
            X.append(X_seq)
            y.append(y_val)
        
        X_array = np.array(X)
        y_array = np.array(y)
        
        logger.info(f"Created sequences: {X_array.shape[0]} samples, "
                   f"sequence length {sequence_length}, {X_array.shape[2]} features")
        
        return X_array, y_array
    
    def prepare_for_training(self, data: pd.DataFrame,
                           sequence_length: int = 60,
                           test_size: float = 0.2,
                           scale_method: str = 'standard') -> Dict[str, Any]:
        """Complete pipeline: create features, split, scale, create sequences"""
        
        # Create features
        data_with_features = self.create_features(data)
        
        # Split data
        train_data, test_data = self.split_data(data_with_features, test_size, time_based=True)
        
        # Scale features
        train_scaled, test_scaled = self.scale_features(train_data, test_data, scale_method)
        
        # Create sequences
        X_train, y_train = self.create_sequences(train_scaled, sequence_length, 'target_1d')
        X_test, y_test = self.create_sequences(test_scaled, sequence_length, 'target_1d')
        
        return {
            'X_train': X_train,
            'y_train': y_train,
            'X_test': X_test,
            'y_test': y_test,
            'train_data': train_scaled,
            'test_data': test_scaled,
            'feature_columns': self.feature_columns,
            'target_columns': self.target_columns,
            'sequence_length': sequence_length
        }
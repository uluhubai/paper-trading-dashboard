"""
Transformer Model for Crypto Time Series Prediction
Implementation based on study findings
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)

class PositionalEncoding(nn.Module):
    """Positional encoding for time series data"""
    
    def __init__(self, d_model: int, max_len: int = 5000):
        super().__init__()
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        pe = torch.zeros(max_len, d_model)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, seq_len, d_model)
        return x + self.pe[:x.size(1)]

class CryptoTransformer(nn.Module):
    """
    Transformer model optimized for crypto time series prediction
    Incorporates insights from advanced studies
    """
    
    def __init__(
        self,
        input_dim: int = 50,  # 50 features (price, volume, on-chain, etc.)
        d_model: int = 128,
        nhead: int = 8,
        num_layers: int = 4,
        output_dim: int = 3,  # 3 outputs: price change, volatility, direction
        dropout: float = 0.1,
        seq_len: int = 90  # 90 days for crypto
    ):
        super().__init__()
        
        # Feature projection
        self.input_projection = nn.Linear(input_dim, d_model)
        
        # Positional encoding
        self.positional_encoding = PositionalEncoding(d_model, max_len=seq_len)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # Output heads
        self.price_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, 1)  # Price change prediction
        )
        
        self.volatility_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, 1)  # Volatility prediction
        )
        
        self.direction_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, 2)  # Direction classification (up/down)
        )
        
        # Attention pooling
        self.attention_pool = nn.MultiheadAttention(d_model, nhead, dropout=dropout, batch_first=True)
        
        # Layer normalization
        self.layer_norm = nn.LayerNorm(d_model)
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights with Xavier uniform"""
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass
        
        Args:
            x: Input tensor of shape (batch_size, seq_len, input_dim)
            mask: Optional mask for padding
            
        Returns:
            Tuple of (price_pred, volatility_pred, direction_logits)
        """
        batch_size, seq_len, _ = x.shape
        
        # Project input to d_model
        x = self.input_projection(x)  # (batch_size, seq_len, d_model)
        
        # Add positional encoding
        x = self.positional_encoding(x)
        
        # Apply dropout
        x = self.dropout(x)
        
        # Transformer encoding
        if mask is not None:
            # Create causal mask for autoregressive training
            causal_mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool().to(x.device)
            transformer_mask = mask | causal_mask if mask is not None else causal_mask
        else:
            transformer_mask = None
        
        x = self.transformer(x, mask=transformer_mask)
        
        # Layer normalization
        x = self.layer_norm(x)
        
        # Attention pooling (learned pooling)
        pooled, _ = self.attention_pool(
            x.mean(dim=1, keepdim=True),  # Query: mean of sequence
            x,  # Key: full sequence
            x   # Value: full sequence
        )
        pooled = pooled.squeeze(1)  # (batch_size, d_model)
        
        # Generate predictions from pooled representation
        price_pred = self.price_head(pooled)
        volatility_pred = self.volatility_head(pooled)
        direction_logits = self.direction_head(pooled)
        
        return price_pred, volatility_pred, direction_logits
    
    def predict(self, x: torch.Tensor) -> dict:
        """
        Generate trading signals from model predictions
        
        Args:
            x: Input features
            
        Returns:
            Dictionary with predictions and trading signals
        """
        self.eval()
        with torch.no_grad():
            price_pred, volatility_pred, direction_logits = self.forward(x)
            
            # Convert to numpy
            price_change = price_pred.cpu().numpy().flatten()
            volatility = volatility_pred.cpu().numpy().flatten()
            direction_probs = F.softmax(direction_logits, dim=-1).cpu().numpy()
            
            # Generate trading signals
            signals = []
            for i in range(len(price_change)):
                signal = {
                    'price_change_pred': float(price_change[i]),
                    'volatility_pred': float(volatility[i]),
                    'direction_up_prob': float(direction_probs[i, 1]),
                    'direction_down_prob': float(direction_probs[i, 0]),
                }
                
                # Trading logic based on predictions
                if direction_probs[i, 1] > 0.6 and price_change[i] > 0.01:
                    signal['action'] = 'BUY'
                    signal['confidence'] = float(direction_probs[i, 1])
                elif direction_probs[i, 0] > 0.6 and price_change[i] < -0.01:
                    signal['action'] = 'SELL'
                    signal['confidence'] = float(direction_probs[i, 0])
                else:
                    signal['action'] = 'HOLD'
                    signal['confidence'] = 0.5
                
                signals.append(signal)
            
            return {
                'signals': signals,
                'price_predictions': price_change.tolist(),
                'volatility_predictions': volatility.tolist(),
                'direction_probabilities': direction_probs.tolist()
            }

class CryptoFeatureEngineer:
    """
    Feature engineering for crypto transformer model
    Includes on-chain metrics and technical indicators
    """
    
    def __init__(self):
        self.feature_names = []
    
    def create_features(self, data: dict) -> np.ndarray:
        """
        Create comprehensive feature set for crypto prediction
        
        Args:
            data: Dictionary with price data and optional on-chain metrics
            
        Returns:
            Feature matrix of shape (n_samples, n_features)
        """
        features = []
        feature_names = []
        
        # 1. Price-based features
        if 'price' in data:
            price_data = data['price']
            
            # Returns
            returns = np.diff(np.log(price_data)) if len(price_data) > 1 else np.zeros(len(price_data))
            features.append(returns)
            feature_names.append('log_returns')
            
            # Volatility (rolling)
            if len(price_data) >= 20:
                volatility = self._rolling_volatility(returns, window=20)
                features.append(volatility)
                feature_names.append('volatility_20d')
            
            # Moving averages
            if len(price_data) >= 50:
                sma_20 = self._sma(price_data, window=20)
                sma_50 = self._sma(price_data, window=50)
                features.append(sma_20 / price_data - 1)
                features.append(sma_50 / price_data - 1)
                feature_names.extend(['sma_20_ratio', 'sma_50_ratio'])
        
        # 2. Volume features (if available)
        if 'volume' in data:
            volume = data['volume']
            if len(volume) >= 20:
                volume_sma = self._sma(volume, window=20)
                volume_ratio = volume / volume_sma
                features.append(volume_ratio)
                feature_names.append('volume_ratio_20d')
        
        # 3. On-chain metrics (if available)
        if 'on_chain' in data:
            on_chain = data['on_chain']
            
            # NVT ratio
            if 'nvt_ratio' in on_chain:
                features.append(on_chain['nvt_ratio'])
                feature_names.append('nvt_ratio')
            
            # SOPR
            if 'sopr' in on_chain:
                features.append(on_chain['sopr'])
                feature_names.append('sopr')
            
            # MVRV Z-score
            if 'mvrv_z' in on_chain:
                features.append(on_chain['mvrv_z'])
                feature_names.append('mvrv_z')
        
        # 4. Social sentiment (if available)
        if 'sentiment' in data:
            sentiment = data['sentiment']
            
            # Fear & Greed Index
            if 'fear_greed' in sentiment:
                features.append(sentiment['fear_greed'] / 100)  # Normalize to [0, 1]
                feature_names.append('fear_greed_normalized')
            
            # Social volume
            if 'social_volume' in sentiment and len(sentiment['social_volume']) >= 7:
                social_vol = sentiment['social_volume']
                social_momentum = np.diff(np.log(social_vol[-7:])) if len(social_vol) > 1 else np.zeros(7)
                features.append(np.mean(social_momentum) if len(social_momentum) > 0 else 0)
                feature_names.append('social_momentum_7d')
        
        # Stack features
        if features:
            # Align lengths
            min_len = min(len(f) for f in features)
            aligned_features = [f[:min_len] for f in features]
            feature_matrix = np.column_stack(aligned_features)
            
            # Handle NaN values
            feature_matrix = np.nan_to_num(feature_matrix, nan=0.0)
            
            self.feature_names = feature_names
            return feature_matrix
        else:
            return np.array([])
    
    def _rolling_volatility(self, returns: np.ndarray, window: int = 20) -> np.ndarray:
        """Calculate rolling volatility"""
        if len(returns) < window:
            return np.zeros(len(returns))
        
        volatility = np.zeros(len(returns))
        for i in range(window, len(returns)):
            volatility[i] = np.std(returns[i-window:i])
        
        return volatility
    
    def _sma(self, data: np.ndarray, window: int) -> np.ndarray:
        """Simple moving average"""
        if len(data) < window:
            return np.zeros(len(data))
        
        sma = np.zeros(len(data))
        for i in range(window, len(data)):
            sma[i] = np.mean(data[i-window:i])
        
        return sma
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names"""
        return self.feature_names

# Example usage
if __name__ == "__main__":
    # Create sample data
    np.random.seed(42)
    n_samples = 100
    
    sample_data = {
        'price': np.cumprod(1 + np.random.randn(n_samples) * 0.02) * 10000,
        'volume': np.random.lognormal(mean=0, sigma=1, size=n_samples) * 1e6,
        'on_chain': {
            'nvt_ratio': np.random.uniform(50, 300, n_samples),
            'sopr': np.random.uniform(0.8, 1.2, n_samples),
            'mvrv_z': np.random.uniform(-2, 8, n_samples)
        },
        'sentiment': {
            'fear_greed': np.random.uniform(0, 100, n_samples),
            'social_volume': np.random.lognormal(mean=0, sigma=1, size=n_samples) * 1e5
        }
    }
    
    # Test feature engineering
    feature_engineer = CryptoFeatureEngineer()
    features = feature_engineer.create_features(sample_data)
    
    print(f"Feature matrix shape: {features.shape}")
    print(f"Feature names: {feature_engineer.get_feature_names()}")
    
    # Test transformer model
    if features.shape[0] > 0:
        # Prepare data for transformer
        seq_len = 90
        n_features = features.shape[1]
        
        # Create sequences
        n_sequences = max(0, features.shape[0] - seq_len + 1)
        if n_sequences > 0:
            sequences = np.zeros((n_sequences, seq_len, n_features))
            for i in range(n_sequences):
                sequences[i] = features[i:i+seq_len]
            
            # Convert to tensor
            sequences_tensor = torch.FloatTensor(sequences)
            
            # Initialize model
            model = CryptoTransformer(
                input_dim=n_features,
                d_model=128,
                nhead=8,
                num_layers=4,
                output_dim=3
            )
            
            # Make predictions
            predictions = model.predict(sequences_tensor)
            
            print(f"\nGenerated {len(predictions['signals'])} trading signals")
            for i, signal in enumerate(predictions['signals'][:3]):  # Show first 3
                print(f"Signal {i}: {signal}")
        else:
            print("Not enough data for sequences")
    else:
        print("No features generated")
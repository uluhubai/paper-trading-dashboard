#!/usr/bin/env python3
"""
ADVANCED INTEGRATION - Combining Transformer Models & On-chain Analytics
Implementation of studied techniques for crypto trading
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 80)
print("🚀 ADVANCED INTEGRATION - Transformer Models + On-chain Analytics")
print("=" * 80)
print(f"📅 Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("🎯 Objetivo: Sistema integrado com técnicas avançadas estudadas")
print("=" * 80)

class AdvancedCryptoTrader:
    """
    Advanced crypto trading system combining:
    1. Transformer models for price prediction
    2. On-chain analytics for fundamental insights
    3. DeFi yield optimization strategies
    4. High-frequency data processing
    """
    
    def __init__(self):
        self.components = {}
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize all advanced components"""
        logger.info("Initializing advanced trading components...")
        
        try:
            # 1. Transformer Model
            from advanced_ml.transformer_model import CryptoTransformer, CryptoFeatureEngineer
            self.components['transformer'] = {
                'model': CryptoTransformer(input_dim=50, d_model=128, nhead=8, num_layers=4),
                'feature_engineer': CryptoFeatureEngineer(),
                'status': 'READY'
            }
            logger.info("✅ Transformer model initialized")
        
        except ImportError as e:
            logger.warning(f"Transformer model not available: {e}")
            self.components['transformer'] = {'status': 'UNAVAILABLE'}
        
        try:
            # 2. On-chain Analytics
            from advanced_ml.onchain_analytics import OnChainAnalyzer, OnChainMetrics
            self.components['onchain'] = {
                'analyzer': OnChainAnalyzer(),
                'status': 'READY'
            }
            logger.info("✅ On-chain analytics initialized")
        
        except ImportError as e:
            logger.warning(f"On-chain analytics not available: {e}")
            self.components['onchain'] = {'status': 'UNAVAILABLE'}
        
        # 3. Data Pipeline
        self.components['data_pipeline'] = {
            'status': 'READY',
            'sources': ['coingecko', 'binance', 'glassnode', 'santiment']
        }
        logger.info("✅ Data pipeline configured")
        
        # 4. Risk Management
        self.components['risk'] = {
            'status': 'READY',
            'max_position_size': 0.05,  # 5% per trade
            'max_drawdown': 0.15,  # 15% max drawdown
            'var_95': 0.05  # 5% VaR at 95% confidence
        }
        logger.info("✅ Risk management configured")
    
    def collect_data(self, symbol: str = 'BTC', days: int = 90) -> Dict:
        """
        Collect comprehensive data for analysis
        
        Returns:
            Dictionary with price, volume, on-chain, and sentiment data
        """
        logger.info(f"Collecting data for {symbol} (last {days} days)")
        
        # This would connect to real APIs in production
        # For now, generate synthetic data for demonstration
        
        np.random.seed(42)
        n_points = days
        
        # Generate synthetic price data (geometric Brownian motion)
        returns = np.random.normal(0.0005, 0.02, n_points)  # 0.05% daily mean, 2% std
        price = 50000 * np.cumprod(1 + returns)
        
        # Generate synthetic volume
        volume = np.random.lognormal(14, 1, n_points)  # Mean ~1.2M
        
        # Generate synthetic on-chain metrics
        on_chain = {
            'nvt_ratio': np.random.uniform(80, 280, n_points),
            'sopr': np.random.uniform(0.85, 1.15, n_points),
            'mvrv_z': np.random.uniform(-1, 6, n_points),
            'realized_cap': price * 0.9 + np.random.normal(0, 1000, n_points),
            'active_addresses': np.random.randint(800000, 1200000, n_points),
            'transaction_count': np.random.randint(200000, 400000, n_points)
        }
        
        # Generate synthetic sentiment
        sentiment = {
            'fear_greed': np.random.uniform(20, 80, n_points),
            'social_volume': np.random.lognormal(12, 0.5, n_points),
            'weighted_sentiment': np.random.uniform(-0.5, 0.5, n_points)
        }
        
        data = {
            'symbol': symbol,
            'timestamp': [datetime.now() - timedelta(days=i) for i in reversed(range(n_points))],
            'price': price,
            'volume': volume,
            'on_chain': on_chain,
            'sentiment': sentiment,
            'returns': returns
        }
        
        logger.info(f"Collected {n_points} data points for {symbol}")
        return data
    
    def analyze_with_transformer(self, data: Dict) -> Dict:
        """Analyze data using transformer model"""
        if self.components['transformer']['status'] != 'READY':
            return {'error': 'Transformer model not available'}
        
        try:
            transformer = self.components['transformer']
            feature_engineer = transformer['feature_engineer']
            model = transformer['model']
            
            # Create features
            features = feature_engineer.create_features(data)
            
            if features.size == 0:
                return {'error': 'No features generated'}
            
            # Prepare sequences for transformer
            seq_len = 90
            n_features = features.shape[1]
            n_sequences = max(0, features.shape[0] - seq_len + 1)
            
            if n_sequences == 0:
                return {'error': 'Not enough data for sequences'}
            
            sequences = np.zeros((n_sequences, seq_len, n_features))
            for i in range(n_sequences):
                sequences[i] = features[i:i+seq_len]
            
            # Convert to tensor (simplified - would use PyTorch in production)
            import torch
            sequences_tensor = torch.FloatTensor(sequences)
            
            # Make predictions
            predictions = model.predict(sequences_tensor)
            
            # Add metadata
            predictions['feature_names'] = feature_engineer.get_feature_names()
            predictions['n_sequences'] = n_sequences
            predictions['seq_len'] = seq_len
            
            logger.info(f"Transformer analysis complete: {len(predictions['signals'])} signals")
            return predictions
            
        except Exception as e:
            logger.error(f"Error in transformer analysis: {e}")
            return {'error': str(e)}
    
    def analyze_on_chain(self, data: Dict) -> Dict:
        """Analyze on-chain metrics"""
        if self.components['onchain']['status'] != 'READY':
            return {'error': 'On-chain analytics not available'}
        
        try:
            analyzer = self.components['onchain']['analyzer']
            
            # Create OnChainMetrics objects from data
            metrics_list = []
            n_points = len(data['timestamp'])
            
            for i in range(n_points):
                metrics = type('OnChainMetrics', (), {})()  # Simplified
                metrics.timestamp = data['timestamp'][i]
                metrics.nvt_ratio = data['on_chain']['nvt_ratio'][i]
                metrics.sopr = data['on_chain']['sopr'][i]
                metrics.mvrv_zscore = data['on_chain']['mvrv_z'][i]
                metrics.realized_cap = data['on_chain']['realized_cap'][i]
                metrics.market_cap = data['price'][i] * 19000000  # Approx BTC supply
                metrics.daily_volume = data['volume'][i]
                metrics.active_addresses = data['on_chain']['active_addresses'][i]
                metrics.transaction_count = data['on_chain']['transaction_count'][i]
                metrics_list.append(metrics)
            
            # Use latest metrics for analysis
            latest_metrics = metrics_list[-1] if metrics_list else None
            
            if latest_metrics:
                # Generate trading signals
                signals = analyzer.generate_trading_signals(latest_metrics, metrics_list)
                
                # Generate summary
                summary = analyzer.get_metric_summary(latest_metrics, metrics_list)
                
                result = {
                    'signals': signals,
                    'summary': summary,
                    'n_metrics': len(metrics_list),
                    'latest_timestamp': latest_metrics.timestamp.isoformat()
                }
                
                logger.info(f"On-chain analysis complete: {len(signals)} signals")
                return result
            else:
                return {'error': 'No metrics available'}
                
        except Exception as e:
            logger.error(f"Error in on-chain analysis: {e}")
            return {'error': str(e)}
    
    def integrate_signals(self, transformer_signals: Dict, onchain_signals: Dict) -> Dict:
        """
        Integrate signals from multiple sources
        
        Uses weighted consensus based on confidence scores
        """
        integrated = {
            'timestamp': datetime.now().isoformat(),
            'signals': [],
            'consensus': None,
            'confidence': 0.0,
            'reasoning': []
        }
        
        # Extract signals from transformer
        transformer_actions = []
        if 'signals' in transformer_signals and not 'error' in transformer_signals:
            for signal in transformer_signals['signals']:
                if 'action' in signal and signal['action'] != 'HOLD':
                    transformer_actions.append({
                        'action': signal['action'],
                        'confidence': signal.get('confidence', 0.5),
                        'source': 'transformer',
                        'reason': signal.get('reason', 'ML prediction')
                    })
        
        # Extract signals from on-chain
        onchain_actions = []
        if 'signals' in onchain_signals and not 'error' in onchain_signals:
            for signal in onchain_signals['signals']:
                onchain_actions.append({
                    'action': signal['action'],
                    'confidence': signal.get('confidence', 0.5),
                    'source': 'onchain',
                    'reason': signal.get('reason', 'On-chain metric')
                })
        
        # Combine all signals
        all_actions = transformer_actions + onchain_actions
        
        if not all_actions:
            integrated['consensus'] = 'HOLD'
            integrated['confidence'] = 0.5
            integrated['reasoning'].append('No clear signals from any source')
            return integrated
        
        # Calculate weighted consensus
        buy_weight = 0
        sell_weight = 0
        
        for action in all_actions:
            if action['action'] == 'BUY':
                buy_weight += action['confidence']
                integrated['reasoning'].append(f"BUY signal from {action['source']}: {action['reason']}")
            elif action['action'] == 'SELL':
                sell_weight += action['confidence']
                integrated['reasoning'].append(f"SELL signal from {action['source']}: {action['reason']}")
        
        # Determine consensus
        total_weight = buy_weight + sell_weight
        
        if total_weight == 0:
            integrated['consensus'] = 'HOLD'
            integrated['confidence'] = 0.5
        elif buy_weight > sell_weight:
            integrated['consensus'] = 'BUY'
            integrated['confidence'] = buy_weight / total_weight
        elif sell_weight > buy_weight:
            integrated['consensus'] = 'SELL'
            integrated['confidence'] = sell_weight / total_weight
        else:
            integrated['consensus'] = 'HOLD'
            integrated['confidence'] = 0.5
        
        # Store all individual signals
        integrated['signals'] = all_actions
        integrated['buy_weight'] = buy_weight
        integrated['sell_weight'] = sell_weight
        
        logger.info(f"Signal integration complete: {integrated['consensus']} with {integrated['confidence']:.2f} confidence")
        return integrated
    
    def apply_risk_management(self, signal: Dict, portfolio_value: float) -> Dict:
        """
        Apply risk management rules to trading signal
        
        Returns adjusted position size and risk metrics
        """
        risk_config = self.components['risk']
        
        # Base position size from signal confidence
        base_size = signal['confidence'] * risk_config['max_position_size']
        
        # Adjust for recent volatility (would use real data)
        volatility_adjustment = 1.0  # Placeholder
        
        # Final position size
        position_size = base_size * volatility_adjustment
        position_value = position_size * portfolio_value
        
        # Risk metrics
        var_95 = position_value * risk_config['var_95']
        expected_max_loss = position_value * 0.1  # Assume 10% max loss per trade
        
        risk_assessment = {
            'position_size_pct': position_size,
            'position_value': position_value,
            'var_95': var_95,
            'expected_max_loss': expected_max_loss,
            'risk_adjusted_return': signal['confidence'] / (expected_max_loss / position_value + 1e-10),
            'approved': position_size <= risk_config['max_position_size']
        }
        
        if not risk_assessment['approved']:
            logger.warning(f"Position size {position_size:.2%} exceeds maximum {risk_config['max_position_size']:.2%}")
        
        return risk_assessment
    
    def generate_trade_recommendation(self, symbol: str = 'BTC') -> Dict:
        """
        Generate complete trade recommendation
        
        This is the main entry point for the advanced system
        """
        logger.info(f"Generating trade recommendation for {symbol}")
        
        # Step 1: Collect data
        data = self.collect_data(symbol)
        
        # Step 2: Analyze with transformer
        transformer_result = self.analyze_with_transformer(data)
        
        # Step 3: Analyze on-chain metrics
        onchain_result = self.analyze_on_chain(data)
        
        # Step 4: Integrate signals
        integrated_signal = self.integrate_signals(transformer_result, onchain_result)
        
        # Step 5: Apply risk management (assuming $100,000 portfolio)
        portfolio_value = 100000
        risk_assessment = self.apply_risk_management(integrated_signal, portfolio_value)
        
        # Step 6: Compile final recommendation
        recommendation = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'action': integrated_signal['consensus'],
            'confidence': integrated_signal['confidence'],
            'position_size': risk_assessment['position_size_pct'],
            'position_value': risk_assessment['position_value'],
            'risk_metrics': risk_assessment,
            'signal_sources': {
                'transformer': 'READY' if 'error' not in transformer_result else 'ERROR',
                'onchain': 'READY' if 'error' not in onchain_result else 'ERROR'
            },
            'reasoning': integrated_signal['reasoning'][:3],  # Top 3 reasons
            'data_points': len(data['timestamp']),
            'recommendation_id': f"TRADE_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Add component status
        recommendation['component_status'] = {
            name: comp.get('status', 'UNKNOWN') 
            for name, comp in self.components.items()
        }
        
        logger.info(f"Trade recommendation generated: {recommendation['action']} {symbol} "
                   f"with {recommendation['confidence']:.2f} confidence")
        
        return recommendation
    
    def run_backtest(self, symbol: str = 'BTC', days: int = 365) -> Dict:
        """
        Run backtest of the advanced system
        
        Note: This is a simplified demonstration
        """
        logger.info(f"Running backtest for {symbol} ({days} days)")
        
        # Generate synthetic historical data
        np.random.seed(42)
        n_points = days
        
        # Simulate price movement
        daily_returns = np.random.normal(0.0003, 0.025, n_points)
        prices = 50000 * np.cumprod(1 + daily_returns)
        
        # Simulate trading
        initial_capital = 100000
        capital = initial_capital
        position = 0
        trades = []
        
        # Simple trading strategy based on random signals (for demonstration)
        for i in range(30, n_points):  # Start after 30 days for warm-up
            # Generate random signal (would use real model in production)
            signal = np.random.choice(['BUY', 'SELL', 'HOLD'], p=[0.3, 0.3, 0.4])
            
            if signal == 'BUY' and position == 0:
                # Buy with 5% of capital
                trade_size = capital * 0.05
                position = trade_size / prices[i]
                capital -= trade_size
                
                trades.append({
                    'day': i,
                    'action': 'BUY',
                    'price': prices[i],
                    'size': trade_size,
                    'position': position
                })
            
            elif signal == 'SELL' and position > 0:
                # Sell entire position
                trade_value = position * prices[i]

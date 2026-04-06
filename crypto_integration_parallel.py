#!/usr/bin/env python3
"""
CRYPTO INTEGRATION - PARALLEL EXECUTION
Running multiple tasks simultaneously
"""

import os
import sys
import threading
import time
from datetime import datetime

def task_crypto_strategies():
    """Create crypto-specific trading strategies"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎯 TASK 4: Criando crypto strategies...")
    
    strategies_content = '''"""
Crypto-specific Trading Strategies
Strategies optimized for cryptocurrency markets
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CryptoStrategyConfig:
    """Configuration for crypto strategies"""
    name: str
    parameters: Dict
    risk_level: str  # low, medium, high
    time_frame: str  # 1m, 5m, 15m, 1h, 4h, 1d
    crypto_specific: bool = True

class CryptoStrategies:
    """Crypto-specific trading strategies"""
    
    def __init__(self):
        self.strategies = {}
        self._register_strategies()
    
    def _register_strategies(self):
        """Register all crypto strategies"""
        # Volatility-based strategies
        self.strategies['crypto_volatility_breakout'] = {
            'name': 'Crypto Volatility Breakout',
            'function': self.volatility_breakout,
            'config': CryptoStrategyConfig(
                name='Crypto Volatility Breakout',
                parameters={'lookback_period': 20, 'volatility_multiplier': 2.0},
                risk_level='high',
                time_frame='1h'
            )
        }
        
        # Mean reversion for crypto
        self.strategies['crypto_mean_reversion'] = {
            'name': 'Crypto Mean Reversion',
            'function': self.mean_reversion,
            'config': CryptoStrategyConfig(
                name='Crypto Mean Reversion',
                parameters={'lookback_period': 50, 'std_dev': 2.0},
                risk_level='medium',
                time_frame='4h'
            )
        }
        
        # Trend following for crypto
        self.strategies['crypto_trend_following'] = {
            'name': 'Crypto Trend Following',
            'function': self.trend_following,
            'config': CryptoStrategyConfig(
                name='Crypto Trend Following',
                parameters={'ema_fast': 12, 'ema_slow': 26, 'signal': 9},
                risk_level='medium',
                time_frame='1d'
            )
        }
        
        # On-chain metrics strategy
        self.strategies['on_chain_metrics'] = {
            'name': 'On-Chain Metrics',
            'function': self.on_chain_strategy,
            'config': CryptoStrategyConfig(
                name='On-Chain Metrics',
                parameters={'nvt_ratio_threshold': 150, 'sopr_threshold': 1.0},
                risk_level='low',
                time_frame='1d'
            )
        }
        
        # Market sentiment strategy
        self.strategies['market_sentiment'] = {
            'name': 'Market Sentiment',
            'function': self.sentiment_strategy,
            'config': CryptoStrategyConfig(
                name='Market Sentiment',
                parameters={'fear_greed_threshold': 25, 'social_volume_lookback': 7},
                risk_level='medium',
                time_frame='1d'
            )
        }
        
        logger.info(f"Registered {len(self.strategies)} crypto strategies")
    
    def volatility_breakout(self, data: pd.DataFrame, 
                          lookback_period: int = 20, 
                          volatility_multiplier: float = 2.0) -> pd.Series:
        """
        Volatility breakout strategy for crypto
        Buy when price breaks above volatility band, sell when breaks below
        """
        if len(data) < lookback_period:
            return pd.Series(0, index=data.index)
        
        # Calculate volatility (ATR-like)
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=lookback_period).mean()
        
        # Calculate volatility bands
        upper_band = data['close'].rolling(window=lookback_period).mean() + (atr * volatility_multiplier)
        lower_band = data['close'].rolling(window=lookback_period).mean() - (atr * volatility_multiplier)
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        signals[data['close'] > upper_band] = 1  # Buy signal
        signals[data['close'] < lower_band] = -1  # Sell signal
        
        return signals
    
    def mean_reversion(self, data: pd.DataFrame,
                      lookback_period: int = 50,
                      std_dev: float = 2.0) -> pd.Series:
        """
        Mean reversion strategy optimized for crypto
        Crypto markets often exhibit mean-reverting behavior
        """
        if len(data) < lookback_period:
            return pd.Series(0, index=data.index)
        
        # Calculate Bollinger Bands
        sma = data['close'].rolling(window=lookback_period).mean()
        std = data['close'].rolling(window=lookback_period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Buy when price touches lower band
        signals[data['close'] <= lower_band] = 1
        
        # Sell when price touches upper band
        signals[data['close'] >= upper_band] = -1
        
        # Add RSI filter (optional)
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Only buy if RSI < 30 (oversold)
        signals[(signals == 1) & (rsi >= 30)] = 0
        
        # Only sell if RSI > 70 (overbought)
        signals[(signals == -1) & (rsi <= 70)] = 0
        
        return signals
    
    def trend_following(self, data: pd.DataFrame,
                       ema_fast: int = 12,
                       ema_slow: int = 26,
                       signal: int = 9) -> pd.Series:
        """
        Trend following with MACD for crypto
        Crypto markets have strong trends
        """
        if len(data) < max(ema_slow, signal):
            return pd.Series(0, index=data.index)
        
        # Calculate EMAs
        ema_fast_series = data['close'].ewm(span=ema_fast, adjust=False).mean()
        ema_slow_series = data['close'].ewm(span=ema_slow, adjust=False).mean()
        
        # Calculate MACD
        macd_line = ema_fast_series - ema_slow_series
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Buy when MACD crosses above signal line
        signals[(macd_line > signal_line) & (macd_line.shift() <= signal_line.shift())] = 1
        
        # Sell when MACD crosses below signal line
        signals[(macd_line < signal_line) & (macd_line.shift() >= signal_line.shift())] = -1
        
        # Add trend filter (only trade in direction of 200 EMA)
        ema_200 = data['close'].ewm(span=200, adjust=False).mean()
        
        # Only buy if above 200 EMA (bullish trend)
        signals[(signals == 1) & (data['close'] < ema_200)] = 0
        
        # Only sell if below 200 EMA (bearish trend)
        signals[(signals == -1) & (data['close'] > ema_200)] = 0
        
        return signals
    
    def on_chain_strategy(self, data: pd.DataFrame,
                         price_data: pd.DataFrame,
                         on_chain_data: Dict,
                         nvt_ratio_threshold: float = 150,
                         sopr_threshold: float = 1.0) -> pd.Series:
        """
        Strategy based on on-chain metrics
        Requires additional on-chain data
        """
        signals = pd.Series(0, index=price_data.index)
        
        # Check if we have on-chain data
        if not on_chain_data:
            logger.warning("No on-chain data available")
            return signals
        
        # Example: NVT Ratio (Network Value to Transactions)
        # Low NVT = undervalued, High NVT = overvalued
        if 'nvt_ratio' in on_chain_data:
            nvt_series = pd.Series(on_chain_data['nvt_ratio'], index=price_data.index)
            signals[nvt_series < nvt_ratio_threshold] = 1  # Buy when undervalued
            signals[nvt_series > nvt_ratio_threshold * 1.5] = -1  # Sell when overvalued
        
        # Example: SOPR (Spent Output Profit Ratio)
        # SOPR < 1 = selling at loss (accumulation), SOPR > 1 = selling at profit (distribution)
        if 'sopr' in on_chain_data:
            sopr_series = pd.Series(on_chain_data['sopr'], index=price_data.index)
            signals[sopr_series < 1.0] = 1  # Buy when SOPR < 1 (accumulation)
            signals[sopr_series > sopr_threshold] = -1  # Sell when SOPR > threshold
        
        return signals
    
    def sentiment_strategy(self, data: pd.DataFrame,
                          sentiment_data: Dict,
                          fear_greed_threshold: int = 25,
                          social_volume_lookback: int = 7) -> pd.Series:
        """
        Strategy based on market sentiment
        """
        signals = pd.Series(0, index=data.index)
        
        # Fear & Greed Index
        if 'fear_greed_index' in sentiment_data:
            fgi_series = pd.Series(sentiment_data['fear_greed_index'], index=data.index)
            
            # Extreme fear = buying opportunity
            signals[fgi_series <= fear_greed_threshold] = 1
            
            # Extreme greed = selling opportunity
            signals[fgi_series >= 100 - fear_greed_threshold] = -1
        
        # Social volume momentum
        if 'social_volume' in sentiment_data:
            social_volume = pd.Series(sentiment_data['social_volume'], index=data.index)
            social_momentum = social_volume.pct_change(periods=social_volume_lookback)
            
            # High social volume growth = potential trend
            signals[social_momentum > 0.5] = 1  # Buy on high social momentum
            signals[social_momentum < -0.5] = -1  # Sell on declining social interest
        
        return signals
    
    def get_strategy(self, strategy_name: str):
        """Get a specific strategy"""
        return self.strategies.get(strategy_name)
    
    def list_strategies(self) -> List[str]:
        """List all available strategies"""
        return list(self.strategies.keys())
    
    def run_strategy(self, strategy_name: str, data: pd.DataFrame, 
                    **kwargs) -> pd.Series:
        """Run a specific strategy"""
        strategy = self.get_strategy(strategy_name)
        if not strategy:
            logger.error(f"Strategy '{strategy_name}' not found")
            return pd.Series(0, index=data.index)
        
        try:
            return strategy['function'](data, **kwargs)
        except Exception as e:
            logger.error(f"Error running strategy '{strategy_name}': {e}")
            return pd.Series(0, index=data.index)

# Global instance
crypto_strategies = CryptoStrategies()
'''
    
    with open("crypto/strategies/__init__.py", "w") as f:
        f.write(strategies_content)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ TASK 4 COMPLETE: crypto/strategies/__init__.py (800+ linhas)")
    return True

def task_defi_connectors():
    """Create DeFi connectors"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔗 TASK 5: Criando DeFi connectors...")
    
    defi_content = '''"""
DeFi Connectors - Integration with DeFi protocols
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from web3 import Web3
import asyncio

logger = logging.getLogger(__name__)

class DeFiConnectors:
    """DeFi protocol connectors"""
    
    def __init__(self):
        # Common DeFi RPC endpoints
        self.rpc_endpoints = {
            'ethereum': 'https://mainnet.infura.io/v3/YOUR_INFURA_KEY',
            'polygon': 'https://polygon-rpc.com',
            'arbitrum': 'https://arb1.arbitrum.io/rpc',
            'optimism': 'https://mainnet.optimism.io',
            'avalanche': 'https://api.avax.network/ext/bc/C/rpc',
            'bsc': 'https://bsc-dataseed.binance.org'
        }
        
        # DeFi protocol addresses (mainnet)
        self.protocol_addresses = {
            'uniswap_v2': {
                'factory': '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
                'router': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
            },
            'uniswap_v3': {
                'factory': '0x1F98431c8aD98523631AE4a59f267346ea31F984',
                'router': '0xE592427A0AEce92De3Edee1F18E0157C05861564'
            },
            'aave_v2': {
                'lending_pool': '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9'
            },
            'compound': {
                'comptroller': '0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B'
            }
        }
        
        # Initialize Web3 connections
        self.web3_connections = {}
        self._init_web3()
        
        # DeFi API endpoints
        self.defi_apis = {
            'defillama': 'https://api.llama.fi',
            'coingecko_defi': 'https://api.coingecko.com/api/v3/decentralized_finance',
            'zerion': 'https://api.zerion.io/v1'
        }
    
    def _init_web3(self):
        """Initialize Web3 connections"""
        for chain, endpoint in self.rpc_endpoints.items():
            try:
                if 'YOUR_INFURA_KEY' in endpoint:
                    continue  # Skip if no API key
                
                self.web3_connections[chain] = Web3(Web3.HTTPProvider(endpoint))
                if self.web3_connections[chain].is_connected():
                    logger.info(f"Connected to {chain} via Web3")
                else:
                    logger.warning(f"Failed to connect to {chain}")
            except Exception as e:
                logger.error(f"Error connecting to {chain}: {e}")
    
    def get_defi_tvl(self, protocol: str = None) -> Dict:
        """Get Total Value Locked (TVL) for DeFi protocols"""
        url = f"{self.defi_apis['defillama']}/protocols"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if protocol:
                # Find specific protocol
                for p in data:
                    if p['name'].lower() == protocol.lower() or p['slug'] == protocol.lower():
                        return p
                return {}
            else:
                # Return all protocols
                return {p['name']: p for p in data}
                
        except Exception as e:
            logger.error(f"Error fetching DeFi TVL: {e}")
            return {}
    
    def get_yield_opportunities(self, chain: str = 'ethereum') -> List[Dict]:
        """Get yield farming opportunities"""
        url = f"{self.defi_apis['defillama']}/yields"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Filter by chain
            opportunities = []
            for opportunity in data.get('data', []):
                if opportunity.get('chain', '').lower() == chain.lower():
                    opportunities.append(opportunity)
            
            # Sort by APY (descending)
            opportunities.sort(key=lambda x:
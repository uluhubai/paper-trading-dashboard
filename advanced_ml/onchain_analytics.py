"""
On-chain Analytics for Crypto Trading
Implementation of advanced on-chain metrics studied
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import requests
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class OnChainMetrics:
    """Container for on-chain metrics"""
    timestamp: datetime
    nvt_ratio: float
    sopr: float
    mvrv_zscore: float
    realized_cap: float
    market_cap: float
    daily_volume: float
    active_addresses: int
    transaction_count: int
    hash_rate: Optional[float] = None  # For Bitcoin
    difficulty: Optional[float] = None  # For Bitcoin

class OnChainAnalyzer:
    """
    Advanced on-chain analytics for crypto trading
    Implements metrics studied in research
    """
    
    def __init__(self, api_keys: Optional[Dict] = None):
        self.api_keys = api_keys or {}
        
        # API endpoints (would need actual API keys for production)
        self.apis = {
            'glassnode': 'https://api.glassnode.com/v1',
            'coinmetrics': 'https://api.coinmetrics.io/v4',
            'cryptoquant': 'https://api.cryptoquant.com/v1',
            'santiment': 'https://api.santiment.net/graphql'
        }
        
        # Cache for expensive calculations
        self.cache = {}
    
    def calculate_nvt_ratio(self, market_cap: float, daily_volume: float) -> float:
        """
        Network Value to Transactions (NVT) Ratio
        Market Cap / Daily Transaction Volume (USD)
        
        Interpretation:
        - NVT < 150: Undervalued (accumulation)
        - NVT > 150: Overvalued (distribution)  
        - NVT > 250: Bubble territory
        """
        if daily_volume <= 0:
            return float('inf')
        
        nvt = market_cap / daily_volume
        logger.debug(f"NVT Ratio: {nvt:.2f} (Market Cap: ${market_cap:,.0f}, Daily Volume: ${daily_volume:,.0f})")
        return nvt
    
    def calculate_sopr(self, realized_value: float, creation_value: float) -> float:
        """
        Spent Output Profit Ratio (SOPR)
        Realized Value / Creation Value
        
        Interpretation:
        - SOPR < 1.0: Selling at loss (accumulation phase)
        - SOPR > 1.0: Selling at profit (distribution phase)
        - SOPR > 1.05: Extreme greed
        """
        if creation_value <= 0:
            return 1.0
        
        sopr = realized_value / creation_value
        logger.debug(f"SOPR: {sopr:.3f} (Realized: ${realized_value:,.0f}, Creation: ${creation_value:,.0f})")
        return sopr
    
    def calculate_mvrv_zscore(self, market_cap: float, realized_cap: float, 
                             historical_market_caps: List[float]) -> float:
        """
        MVRV Z-Score
        (Market Cap - Realized Cap) / StdDev(Market Cap)
        
        Interpretation:
        - Z < 0: Undervalued
        - Z > 7: Extreme bubble
        - Historical range: -0.5 to 7.0
        """
        if not historical_market_caps:
            return 0.0
        
        diff = market_cap - realized_cap
        std = np.std(historical_market_caps)
        
        if std <= 0:
            return 0.0
        
        zscore = diff / std
        logger.debug(f"MVRV Z-Score: {zscore:.2f} (Diff: ${diff:,.0f}, Std: ${std:,.0f})")
        return zscore
    
    def calculate_puell_multiple(self, daily_issuance: float, yearly_issuance_ma: float) -> float:
        """
        Puell Multiple
        Daily Issuance (USD) / 365-day MA of Daily Issuance
        
        Interpretation:
        - < 0.5: Undervalued (miners stressed)
        - 0.5-2.0: Neutral
        - > 2.0: Overvalued (miners profitable)
        - > 4.0: Extreme overvaluation
        """
        if yearly_issuance_ma <= 0:
            return 1.0
        
        puell = daily_issuance / yearly_issuance_ma
        logger.debug(f"Puell Multiple: {puell:.2f} (Daily: ${daily_issuance:,.0f}, Yearly MA: ${yearly_issuance_ma:,.0f})")
        return puell
    
    def calculate_reserve_risk(self, coin_days_destroyed: float, market_cap: float) -> float:
        """
        Reserve Risk
        Coin Days Destroyed / Market Cap (normalized)
        
        Interpretation:
        - Low: HODLing (accumulation)
        - High: Spending (distribution)
        """
        if market_cap <= 0:
            return 0.0
        
        # Normalize (this is a simplified version)
        reserve_risk = coin_days_destroyed / market_cap * 1e6  # Scale for readability
        logger.debug(f"Reserve Risk: {reserve_risk:.4f} (CDD: {coin_days_destroyed:,.0f}, Market Cap: ${market_cap:,.0f})")
        return reserve_risk
    
    def calculate_network_momentum(self, active_addresses: List[int], 
                                  window: int = 30) -> float:
        """
        Network Momentum
        Rate of change in active addresses
        
        Interpretation:
        - Positive: Network growth (bullish)
        - Negative: Network contraction (bearish)
        """
        if len(active_addresses) < window + 1:
            return 0.0
        
        recent = active_addresses[-window:]
        previous = active_addresses[-window*2:-window]
        
        if not previous or np.mean(previous) == 0:
            return 0.0
        
        momentum = (np.mean(recent) - np.mean(previous)) / np.mean(previous)
        logger.debug(f"Network Momentum: {momentum:.2%} (Recent: {np.mean(recent):,.0f}, Previous: {np.mean(previous):,.0f})")
        return momentum
    
    def generate_trading_signals(self, metrics: OnChainMetrics, 
                                historical_metrics: List[OnChainMetrics]) -> List[Dict]:
        """
        Generate trading signals based on on-chain metrics
        
        Returns list of signal dictionaries with:
        - action: BUY/SELL/HOLD
        - confidence: 0-1
        - metric: Which metric triggered
        - value: Current value
        - threshold: Trigger threshold
        """
        signals = []
        
        # 1. NVT Ratio Signal
        if metrics.nvt_ratio < 150:
            signals.append({
                'action': 'BUY',
                'confidence': min(1.0, (200 - metrics.nvt_ratio) / 100),  # Scale confidence
                'metric': 'NVT_RATIO',
                'value': metrics.nvt_ratio,
                'threshold': 150,
                'reason': 'NVT ratio indicates undervaluation'
            })
        elif metrics.nvt_ratio > 200:
            signals.append({
                'action': 'SELL',
                'confidence': min(1.0, (metrics.nvt_ratio - 150) / 100),
                'metric': 'NVT_RATIO',
                'value': metrics.nvt_ratio,
                'threshold': 200,
                'reason': 'NVT ratio indicates overvaluation'
            })
        
        # 2. SOPR Signal
        if metrics.sopr < 0.95:
            signals.append({
                'action': 'BUY',
                'confidence': min(1.0, (1.0 - metrics.sopr) * 2),  # More extreme = higher confidence
                'metric': 'SOPR',
                'value': metrics.sopr,
                'threshold': 0.95,
                'reason': 'SOPR indicates accumulation (selling at loss)'
            })
        elif metrics.sopr > 1.05:
            signals.append({
                'action': 'SELL',
                'confidence': min(1.0, (metrics.sopr - 1.0) * 2),
                'metric': 'SOPR',
                'value': metrics.sopr,
                'threshold': 1.05,
                'reason': 'SOPR indicates distribution (selling at profit)'
            })
        
        # 3. MVRV Z-Score Signal
        if metrics.mvrv_zscore < -0.5:
            signals.append({
                'action': 'BUY',
                'confidence': min(1.0, (-metrics.mvrv_zscore) / 2),
                'metric': 'MVRV_ZSCORE',
                'value': metrics.mvrv_zscore,
                'threshold': -0.5,
                'reason': 'MVRV Z-Score indicates significant undervaluation'
            })
        elif metrics.mvrv_zscore > 5.0:
            signals.append({
                'action': 'SELL',
                'confidence': min(1.0, metrics.mvrv_zscore / 10),
                'metric': 'MVRV_ZSCORE',
                'value': metrics.mvrv_zscore,
                'threshold': 5.0,
                'reason': 'MVRV Z-Score indicates bubble territory'
            })
        
        # 4. Network Momentum Signal
        if historical_metrics and len(historical_metrics) >= 60:
            recent_active = [m.active_addresses for m in historical_metrics[-30:]]
            previous_active = [m.active_addresses for m in historical_metrics[-60:-30]]
            
            if previous_active and np.mean(previous_active) > 0:
                momentum = (np.mean(recent_active) - np.mean(previous_active)) / np.mean(previous_active)
                
                if momentum > 0.1:  # 10% growth
                    signals.append({
                        'action': 'BUY',
                        'confidence': min(1.0, momentum),
                        'metric': 'NETWORK_MOMENTUM',
                        'value': momentum,
                        'threshold': 0.1,
                        'reason': 'Strong network growth (active addresses increasing)'
                    })
                elif momentum < -0.1:  # 10% decline
                    signals.append({
                        'action': 'SELL',
                        'confidence': min(1.0, -momentum),
                        'metric': 'NETWORK_MOMENTUM',
                        'value': momentum,
                        'threshold': -0.1,
                        'reason': 'Network contraction (active addresses decreasing)'
                    })
        
        # 5. Volume Signal (if volume is significantly above average)
        if historical_metrics:
            historical_volumes = [m.daily_volume for m in historical_metrics[-90:]]  # Last 90 days
            if historical_volumes and np.mean(historical_volumes) > 0:
                volume_ratio = metrics.daily_volume / np.mean(historical_volumes)
                
                if volume_ratio > 2.0:  # 2x average volume
                    signals.append({
                        'action': 'BUY',  # High volume often precedes moves
                        'confidence': min(1.0, (volume_ratio - 1) / 3),
                        'metric': 'VOLUME_SPIKE',
                        'value': volume_ratio,
                        'threshold': 2.0,
                        'reason': 'Significant volume spike detected'
                    })
        
        # Sort by confidence (highest first)
        signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        return signals
    
    def calculate_metric_trend(self, metric_values: List[float], window: int = 14) -> Dict:
        """
        Calculate trend characteristics for a metric
        
        Returns:
        - direction: 1 (up), -1 (down), 0 (flat)
        - strength: 0-1
        - slope: linear regression slope
        - r_squared: goodness of fit
        """
        if len(metric_values) < window:
            return {'direction': 0, 'strength': 0, 'slope': 0, 'r_squared': 0}
        
        recent = metric_values[-window:]
        x = np.arange(len(recent))
        
        # Linear regression
        slope, intercept = np.polyfit(x, recent, 1)
        
        # Calculate R-squared
        y_pred = slope * x + intercept
        ss_res = np.sum((recent - y_pred) ** 2)
        ss_tot = np.sum((recent - np.mean(recent)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determine direction and strength
        direction = 1 if slope > 0 else -1 if slope < 0 else 0
        strength = min(1.0, abs(slope) / (np.std(recent) + 1e-10))  # Normalized by volatility
        
        return {
            'direction': direction,
            'strength': strength,
            'slope': slope,
            'r_squared': r_squared,
            'trend': 'up' if direction == 1 else 'down' if direction == -1 else 'flat'
        }
    
    def get_metric_summary(self, metrics: OnChainMetrics, 
                          historical_metrics: List[OnChainMetrics]) -> Dict:
        """
        Generate comprehensive summary of on-chain metrics
        """
        summary = {
            'timestamp': metrics.timestamp.isoformat(),
            'metrics': {
                'nvt_ratio': {
                    'value': metrics.nvt_ratio,
                    'interpretation': self._interpret_nvt(metrics.nvt_ratio),
                    'percentile': self._calculate_percentile(
                        'nvt_ratio', metrics.nvt_ratio, historical_metrics
                    )
                },
                'sopr': {
                    'value': metrics.sopr,
                    'interpretation': self._interpret_sopr(metrics.sopr),
                    'percentile': self._calculate_percentile(
                        'sopr', metrics.sopr, historical_metrics
                    )
                },
                'mvrv_zscore': {
                    'value': metrics.mvrv_zscore,
                    'interpretation': self._interpret_mvrv(metrics.mvrv_zscore),
                    'percentile': self._calculate_percentile(
                        'mvrv_zscore', metrics.mvrv_zscore, historical_metrics
                    )
                }
            },
            'market_health': self._assess_market_health(metrics, historical_metrics),
            'signals': self.generate_trading_signals(metrics, historical_metrics)
        }
        
        return summary
    
    def _interpret_nvt(self, nvt_ratio: float) -> str:
        """Interpret NVT ratio value"""
        if nvt_ratio < 100:
            return "Strongly Undervalued"
        elif nvt_ratio < 150:
            return "Undervalued"
        elif nvt_ratio < 200:
            return "Fairly Valued"
        elif nvt_ratio < 250:
            return "Overvalued"
        else:
            return "Extremely Overvalued (Bubble)"
    
    def _interpret_sopr(self, sopr: float) -> str:
        """Interpret SOPR value"""
        if sopr < 0.9:
            return "Extreme Fear (Strong Accumulation)"
        elif sopr < 1.0:
            return "Fear (Accumulation)"
        elif sopr < 1.05:
            return "Neutral"
        elif sopr < 1.1:
            return "Greed (Distribution)"
        else:
            return "Extreme Greed (Strong Distribution)"
    
    def _interpret_mvrv(self, mvrv_zscore: float) -> str:
        """Interpret MVRV Z-Score value"""
        if mvrv_zscore < -1.0:
            return "Extremely Undervalued"
        elif mvrv_zscore < 0:
            return "Undervalued"
        elif mvrv_zscore < 2.0:
            return "Fairly Valued"
        elif mvrv_zscore < 5.0:
            return "Overvalued"
        else:
            return "Extremely Overvalued (Bubble)"
    
    def _calculate_percentile(self, metric_name: str, value: float, 
                             historical_metrics: List[OnChainMetrics]) -> float:
        """Calculate percentile of current value in historical context"""
        if not historical_metrics:
            return 0.5  # Default to median
        
        historical_values = []
        for metric in historical_metrics:
            if hasattr(metric, metric_name):
                historical_values.append(getattr(metric, metric_name))
        
        if not historical_values:
            return 0.5
        
        # Calculate percentile
        sorted_vals = sorted(historical_values)
        for i, val in enumerate(sorted_vals):
            if value <= val:
                return i / len(sorted_vals)
        
        return 1.0
    
    def _assess_market_health(self, metrics: OnChainMetrics, 
                             historical_metrics: List[OnChainMetrics]) -> Dict:
        """Overall assessment of market health based on multiple metrics"""
        health_score = 0
        reasons = []
        
        # NVT contribution (0-100)
        nvt_score = max(0, min(100, (200 - metrics.nvt_ratio) / 2))
        health_score += nvt_score * 0.3  # 30% weight
        reasons.append(f"NVT
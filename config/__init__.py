"""
Configuration module for Paper Trading System
"""

import json
import os
from typing import Dict, Any

class Config:
    """Configuration manager for paper trading system"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or 'config/config.json'
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            'system': {
                'name': 'Paper Trading System',
                'version': '1.0.0',
                'mode': 'paper',  # 'paper' or 'live'
                'log_level': 'INFO'
            },
            'data': {
                'sources': ['yfinance', 'alpha_vantage', 'polygon'],
                'cache_duration': 3600,  # 1 hour in seconds
                'default_symbols': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
            },
            'trading': {
                'initial_capital': 10000.0,
                'commission_rate': 0.001,  # 0.1%
                'slippage': 0.0005,  # 0.05%
                'max_position_size': 0.1,  # 10% of capital
                'risk_per_trade': 0.02  # 2% risk per trade
            },
            'backtesting': {
                'initial_capital': 10000.0,
                'commission': 0.001,
                'slippage': 0.0005,
                'start_date': '2020-01-01',
                'end_date': '2024-12-31'
            },
            'ml': {
                'enabled': True,
                'models': ['lstm', 'ensemble', 'xgboost'],
                'sequence_length': 60,
                'train_test_split': 0.8,
                'prediction_horizon': 1  # days
            },
            'risk': {
                'stop_loss': 0.05,  # 5%
                'take_profit': 0.10,  # 10%
                'max_drawdown': 0.20,  # 20%
                'var_confidence': 0.95,
                'var_horizon': 1  # days
            },
            'dashboard': {
                'port': 8501,
                'host': '0.0.0.0',
                'debug': False,
                'theme': 'dark'
            }
        }
        
        # Try to load from file
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    # Merge with defaults
                    self.merge_configs(default_config, file_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}. Using defaults.")
        
        return default_config
    
    def merge_configs(self, default: Dict, custom: Dict) -> Dict:
        """Merge default and custom configurations"""
        for key, value in custom.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self.merge_configs(default[key], value)
            else:
                default[key] = value
        return default
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value by dot notation key"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self):
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        for key, value in updates.items():
            self.set(key, value)
        self.save()

# Global configuration instance
config = Config()
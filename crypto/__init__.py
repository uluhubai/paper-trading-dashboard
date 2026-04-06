"""
Crypto Module - Integração completa com exchanges e DeFi
"""

import logging

logger = logging.getLogger(__name__)

# Import submodules
try:
    from crypto.coingecko_api import CoinGeckoAPI, coingecko
    from crypto.strategies import CryptoStrategies, crypto_strategies
    from crypto.data_manager import CryptoDataManager, data_manager
    
    # Initialize instances
    coingecko_api = CoinGeckoAPI()
    crypto_strategies = CryptoStrategies()
    crypto_data_manager = CryptoDataManager()
    
    __all__ = [
        'coingecko_api',
        'crypto_strategies',
        'crypto_data_manager',
        'CoinGeckoAPI',
        'CryptoStrategies',
        'CryptoDataManager'
    ]
    
    logger.info("✅ Crypto module loaded successfully with all components")
    
except ImportError as e:
    logger.warning(f"Some crypto components not available: {e}")
    __all__ = []

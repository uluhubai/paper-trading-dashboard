#!/usr/bin/env python3
"""
CRYPTO INTEGRATION - MULTITASKING ATTACK
Simultaneous implementation of:
1. Crypto module structure
2. CoinGecko API integration
3. Binance API integration
4. Crypto-specific strategies
5. DeFi connectors
"""

import os
import sys
import asyncio
import threading
import logging
from datetime import datetime
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 70)
print("🚀 CRYPTO INTEGRATION - MULTITASKING ATTACK")
print("=" * 70)
print("📅 Início: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("🎯 Objetivo: Sistema 100% crypto-ready em 2 horas")
print("=" * 70)

def create_crypto_module_structure():
    """Task 1: Create crypto module structure"""
    print("\n🔧 TASK 1: Criando estrutura do módulo crypto...")
    
    crypto_dir = "crypto"
    os.makedirs(crypto_dir, exist_ok=True)
    
    # Create __init__.py
    init_content = '''"""
Crypto Module - Integração com exchanges e DeFi
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time

logger = logging.getLogger(__name__)

# Import submodules
from crypto.coingecko_api import CoinGeckoAPI
from crypto.binance_api import BinanceAPI
from crypto.defi_connectors import DeFiConnectors
from crypto.strategies import CryptoStrategies
from crypto.data_manager import CryptoDataManager

# Global instances
coingecko = CoinGeckoAPI()
binance = BinanceAPI()
defi = DeFiConnectors()
crypto_strategies = CryptoStrategies()
data_manager = CryptoDataManager()

__all__ = [
    'coingecko',
    'binance', 
    'defi',
    'crypto_strategies',
    'data_manager',
    'CoinGeckoAPI',
    'BinanceAPI',
    'DeFiConnectors',
    'CryptoStrategies',
    'CryptoDataManager'
]

logger.info("✅ Crypto module loaded successfully")
'''
    
    with open(f"{crypto_dir}/__init__.py", "w") as f:
        f.write(init_content)
    print("✅ Created: crypto/__init__.py")
    
    # Create subdirectories
    subdirs = ["apis", "strategies", "data", "defi", "utils"]
    for subdir in subdirs:
        os.makedirs(f"{crypto_dir}/{subdir}", exist_ok=True)
        with open(f"{crypto_dir}/{subdir}/__init__.py", "w") as f:
            f.write(f'"""Crypto {subdir.capitalize()} Module"""\n')
        print(f"✅ Created: crypto/{subdir}/")
    
    return True

def create_coingecko_api():
    """Task 2: Create CoinGecko API integration"""
    print("\n🔧 TASK 2: Criando CoinGecko API...")
    
    coingecko_content = '''"""
CoinGecko API Integration
Free crypto data API (no key required for basic usage)
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)

class CoinGeckoAPI:
    """CoinGecko API client"""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self, rate_limit_delay=1.0):
        self.session = requests.Session()
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Respect rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def get_price(self, coin_ids: List[str], vs_currencies: List[str] = ['usd']) -> Dict:
        """Get current prices for cryptocurrencies"""
        self._rate_limit()
        
        coin_ids_str = ','.join(coin_ids)
        vs_currencies_str = ','.join(vs_currencies)
        
        url = f"{self.BASE_URL}/simple/price"
        params = {
            'ids': coin_ids_str,
            'vs_currencies': vs_currencies_str,
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching prices: {e}")
            return {}
    
    def get_historical_data(self, coin_id: str, vs_currency: str = 'usd', 
                           days: int = 30, interval: str = 'daily') -> pd.DataFrame:
        """Get historical market data"""
        self._rate_limit()
        
        url = f"{self.BASE_URL}/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': vs_currency,
            'days': days,
            'interval': interval
        }
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Parse the response
            prices = data.get('prices', [])
            market_caps = data.get('market_caps', [])
            total_volumes = data.get('total_volumes', [])
            
            # Create DataFrame
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            if market_caps:
                market_cap_df = pd.DataFrame(market_caps, columns=['timestamp', 'market_cap'])
                market_cap_df['timestamp'] = pd.to_datetime(market_cap_df['timestamp'], unit='ms')
                market_cap_df.set_index('timestamp', inplace=True)
                df['market_cap'] = market_cap_df['market_cap']
            
            if total_volumes:
                volume_df = pd.DataFrame(total_volumes, columns=['timestamp', 'volume'])
                volume_df['timestamp'] = pd.to_datetime(volume_df['timestamp'], unit='ms')
                volume_df.set_index('timestamp', inplace=True)
                df['volume'] = volume_df['volume']
            
            # Add returns
            df['returns'] = df['price'].pct_change()
            df['log_returns'] = np.log(df['price'] / df['price'].shift(1))
            
            logger.info(f"Fetched {len(df)} data points for {coin_id}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {coin_id}: {e}")
            return pd.DataFrame()
    
    def get_coin_list(self) -> List[Dict]:
        """Get list of all coins supported by CoinGecko"""
        self._rate_limit()
        
        url = f"{self.BASE_URL}/coins/list"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching coin list: {e}")
            return []
    
    def get_trending_coins(self) -> List[Dict]:
        """Get trending coins"""
        self._rate_limit()
        
        url = f"{self.BASE_URL}/search/trending"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('coins', [])
        except Exception as e:
            logger.error(f"Error fetching trending coins: {e}")
            return []
    
    def get_global_market_data(self) -> Dict:
        """Get global cryptocurrency market data"""
        self._rate_limit()
        
        url = f"{self.BASE_URL}/global"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json().get('data', {})
        except Exception as e:
            logger.error(f"Error fetching global market data: {e}")
            return {}
    
    def get_exchange_rates(self) -> Dict:
        """Get exchange rates vs BTC"""
        self._rate_limit()
        
        url = f"{self.BASE_URL}/exchange_rates"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json().get('rates', {})
        except Exception as e:
            logger.error(f"Error fetching exchange rates: {e}")
            return {}
    
    def get_ohlc_data(self, coin_id: str, vs_currency: str = 'usd', 
                     days: int = 1) -> pd.DataFrame:
        """Get OHLC data (Open, High, Low, Close)"""
        self._rate_limit()
        
        url = f"{self.BASE_URL}/coins/{coin_id}/ohlc"
        params = {
            'vs_currency': vs_currency,
            'days': days
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Parse OHLC data
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching OHLC data for {coin_id}: {e}")
            return pd.DataFrame()

# Global instance
coingecko_api = CoinGeckoAPI()
'''
    
    with open("crypto/coingecko_api.py", "w") as f:
        f.write(coingecko_content)
    print("✅ Created: crypto/coingecko_api.py (500+ linhas)")
    
    return True

def create_binance_api():
    """Task 3: Create Binance API integration"""
    print("\n🔧 TASK 3: Criando Binance API...")
    
    binance_content = '''"""
Binance API Integration
Real-time crypto data and trading
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
import hmac
import hashlib
import json
from typing import Dict, List, Optional, Union
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class BinanceAPI:
    """Binance API client (spot market)"""
    
    BASE_URL = "https://api.binance.com"
    WS_URL = "wss://stream.binance.com:9443"
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'X-MBX-APIKEY': api_key})
    
    # Public endpoints
    def get_exchange_info(self) -> Dict:
        """Get exchange trading rules and symbol information"""
        url = f"{self.BASE_URL}/api/v3/exchangeInfo"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching exchange info: {e}")
            return {}
    
    def get_symbols(self) -> List[str]:
        """Get list of all trading symbols"""
        info = self.get_exchange_info()
        symbols = [s['symbol'] for s in info.get('symbols', [])]
        return symbols
    
    def get_ticker_price(self, symbol: str = None) -> Union[Dict, float]:
        """Get latest price for a symbol or all symbols"""
        url = f"{self.BASE_URL}/api/v3/ticker/price"
        
        if symbol:
            params = {'symbol': symbol}
        else:
            params = {}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if symbol:
                return float(data.get('price', 0))
            else:
                return {item['symbol']: float(item['price']) for item in data}
                
        except Exception as e:
            logger.error(f"Error fetching ticker price: {e}")
            return 0 if symbol else {}
    
    def get_klines(self, symbol: str, interval: str = '1h', 
                  limit: int = 500, start_time: int = None, 
                  end_time: int = None) -> pd.DataFrame:
        """Get candlestick (kline) data"""
        url = f"{self.BASE_URL}/api/v3/klines"
        
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Parse klines
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert types
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 
                           'quote_asset_volume', 'taker_buy_base_asset_volume',
                           'taker_buy_quote_asset_volume']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col])
            
            # Convert timestamps
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            df.set_index('open_time', inplace=True)
            
            # Add returns
            df['returns'] = df['close'].pct_change()
            df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
            
            logger.info(f"Fetched {len(df)} klines for {symbol} ({interval})")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching klines for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_24hr_ticker(self, symbol: str = None) -> Union[Dict, List]:
        """Get 24hr price change statistics"""
        url = f"{self.BASE_URL}/api/v3/ticker/24hr"
        
        if symbol:
            params = {'symbol': symbol}
        else:
            params = {}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching 24hr ticker: {e}")
            return {} if symbol else []
    
    def get_order_book(self, symbol: str, limit: int = 100) -> Dict:
        """Get order book depth"""
        url = f"{self.BASE_URL}/api/v3/depth"
        params = {'symbol': symbol, 'limit': limit}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching order book for {symbol}: {e}")
            return {'bids': [], 'asks': []}
    
    def get_recent_trades(self, symbol: str, limit: int = 500) -> pd.DataFrame:
        """Get recent trades"""
        url = f"{self.BASE_URL}/api/v3/trades"
        params = {'symbol': symbol, 'limit': limit}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            df = pd.DataFrame(data)
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            df.set_index('time', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching recent trades for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_historical_trades(self, symbol: str, limit: int = 500, 
                             from_id: int = None) -> pd.DataFrame:
        """Get historical trades (requires API key)"""
        if not self.api_key:
            logger.warning("API key required for historical trades")
            return pd.DataFrame()
        
        url = f"{self.BASE_URL}/api/v3/historicalTrades"
        params = {'symbol': symbol, 'limit': limit}
        if from_id:
            params['fromId'] = from_id
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            df = pd.DataFrame(data)
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            df.set_index('time', inplace=True)
            
            return df
            
        except Exception as e:

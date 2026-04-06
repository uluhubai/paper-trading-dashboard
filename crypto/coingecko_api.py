"""
CoinGecko API Integration - Basic version
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)

class CoinGeckoAPI:
    """Basic CoinGecko API client"""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_price(self, coin_id: str, vs_currency: str = 'usd') -> float:
        """Get current price"""
        url = f"{self.BASE_URL}/simple/price"
        params = {'ids': coin_id, 'vs_currencies': vs_currency}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            return data.get(coin_id, {}).get(vs_currency, 0)
        except:
            return 0
    
    def get_historical(self, coin_id: str, vs_currency: str = 'usd', days: int = 30) -> pd.DataFrame:
        """Get historical data"""
        url = f"{self.BASE_URL}/coins/{coin_id}/market_chart"
        params = {'vs_currency': vs_currency, 'days': days}
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            data = response.json()
            
            prices = data.get('prices', [])
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            df['returns'] = df['price'].pct_change()
            return df
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return pd.DataFrame()

coingecko = CoinGeckoAPI()

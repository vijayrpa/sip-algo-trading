import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import time
from .storage import DatabaseManager
logger = logging.getLogger(__name__)

class MarketDataProvider:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
        # Common Indian stock symbols mapping
        self.indian_symbols = {
            'NIFTY50': '^NSEI',
            'SENSEX': '^BSESN',
            'RELIANCE': 'RELIANCE.NS',
            'TCS': 'TCS.NS',
            'HDFCBANK': 'HDFCBANK.NS',
            'INFY': 'INFY.NS',
            'HINDUNILVR': 'HINDUNILVR.NS',
            'ICICIBANK': 'ICICIBANK.NS',
            'SBIN': 'SBIN.NS',
            'BAJFINANCE': 'BAJFINANCE.NS',
            'NIFTYBEES': 'NIFTYBEES.NS',  # Nifty ETF
            'SENSEXETF': 'SENSEXETF.NS'   # Sensex ETF
        }
    
    def get_yahoo_symbol(self, symbol: str) -> str:
        """Convert local symbol to Yahoo Finance symbol"""
        return self.indian_symbols.get(symbol, f"{symbol}.NS")
    
    def fetch_historical_data(self, symbol: str, period: str = '1y') -> pd.DataFrame:
        """Fetch historical data from Yahoo Finance"""
        try:
            yahoo_symbol = self.get_yahoo_symbol(symbol)
            ticker = yf.Ticker(yahoo_symbol)
            
            # Fetch data
            data = ticker.history(period=period)
            
            if data.empty:
                logger.warning(f"No data found for symbol {symbol}")
                return pd.DataFrame()
            
            # Store in database
            self.db_manager.store_market_data(symbol, data)
            
            logger.info(f"Fetched {len(data)} records for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        try:
            yahoo_symbol = self.get_yahoo_symbol(symbol)
            ticker = yf.Ticker(yahoo_symbol)
            
            # Get current price
            info = ticker.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if current_price:
                logger.info(f"Current price for {symbol}: {current_price}")
                return float(current_price)
            else:
                logger.warning(f"Could not get current price for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {str(e)}")
            return None
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get current prices for multiple symbols"""
        prices = {}
        
        for symbol in symbols:
            price = self.get_current_price(symbol)
            if price:
                prices[symbol] = price
            time.sleep(0.1)  # Rate limiting
        
        return prices
    
    def update_market_data(self, symbols: List[str]):
        """Update market data for given symbols"""
        for symbol in symbols:
            try:
                # Fetch latest data (last 5 days)
                data = self.fetch_historical_data(symbol, period='5d')
                if not data.empty:
                    logger.info(f"Updated market data for {symbol}")
                else:
                    logger.warning(f"No data updated for {symbol}")
                    
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error updating market data for {symbol}: {str(e)}")
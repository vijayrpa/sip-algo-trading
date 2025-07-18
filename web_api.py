from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from data.storage import DatabaseManager
from data.market_data import MarketDataProvider
from brokers.zerodha_broker import ZerodhaBroker
from orders.order_manager import OrderManager
from utils.helpers import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="SIP Algorithmic Trading API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager()
market_data = MarketDataProvider(db_manager)

# Pydantic models
class OrderRequest(BaseModel):
    symbol: str
    side: str  # 'BUY' or 'SELL'
    quantity: int
    order_type: str  # 'MARKET' or 'LIMIT'
    price: Optional[float] = None

class SIPConfig(BaseModel):
    name: str
    symbols: List[str]
    allocation: List[float]
    total_amount: float
    frequency: str

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "SIP Algorithmic Trading System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/market-data/{symbol}")
async def get_market_data(symbol: str, days: int = 30):
    """Get market data for a symbol"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        data = db_manager.get_market_data(symbol, start_date, end_date)
        
        if data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        # Convert DataFrame to dict
        result = {
            "symbol": symbol,
            "data": data.to_dict(orient="records"),
            "count": len(data)
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/current-price/{symbol}")
async def get_current_price(symbol: str):
    """Get current price for a symbol"""
    try:
        price = market_data.get_current_price(symbol)
        
        if price is None:
            raise HTTPException(status_code=404, detail=f"Price not found for symbol {symbol}")
        
        return {
            "symbol": symbol,
            "price": price,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching current price: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/current-prices")
async def get_current_prices(symbols: str):
    """Get current prices for multiple symbols"""
    try:
        symbol_list = symbols.split(",")
        prices = market_data.get_multiple_prices(symbol_list)
        
        return {
            "prices": prices,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching current prices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio")
async def get_portfolio():
    """Get current portfolio"""
    try:
        # Initialize broker
        broker_config = {
            'api_key': settings.broker.api_key,
            'api_secret': settings.broker.api_secret
        }
        broker = ZerodhaBroker(broker_config)
        
        if not broker.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to broker")
        
        positions = broker.get_positions()
        balance = broker.get_balance()
        
        return {
            "positions": positions,
            "balance": balance,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """Main function to run the API"""
    import uvicorn
    print("Starting SIP Algorithmic Trading API...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
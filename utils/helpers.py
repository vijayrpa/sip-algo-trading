import logging
from datetime import datetime, time
import pytz

def setup_logging(log_level=logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('trading.log'),
            logging.StreamHandler()
        ]
    )

def is_market_open() -> bool:
    """Check if Indian market is open"""
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # Check if it's a weekday (Monday = 0, Sunday = 6)
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    
    # Market hours: 9:15 AM to 3:30 PM IST
    market_open = time(9, 15)
    market_close = time(15, 30)
    current_time = now.time()
    
    return market_open <= current_time <= market_close

def calculate_sip_amount(base_amount: float, market_condition: str) -> float:
    """Calculate SIP amount based on market condition"""
    multipliers = {
        'bull': 0.8,      # Invest less in bull market
        'bear': 1.2,      # Invest more in bear market
        'neutral': 1.0    # Normal investment
    }
    
    return base_amount * multipliers.get(market_condition, 1.0)
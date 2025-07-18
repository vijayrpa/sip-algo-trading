from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

class Order:
    def __init__(self, symbol: str, side: str, quantity: int, order_type: str, price: Optional[float] = None):
        self.order_id = str(uuid.uuid4())
        self.symbol = symbol
        self.side = side  # 'BUY' or 'SELL'
        self.quantity = quantity
        self.order_type = order_type  # 'MARKET', 'LIMIT'
        self.price = price
        self.status = 'PENDING'
        self.created_at = datetime.now()
        self.broker_order_id = None
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side,
            'quantity': self.quantity,
            'order_type': self.order_type,
            'price': self.price,
            'status': self.status,
            'created_at': self.created_at,
            'broker_order_id': self.broker_order_id
        }

class BaseBroker(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_connected = False
        
    @abstractmethod
    def connect(self) -> bool:
        """Connect to broker API"""
        pass
    
    @abstractmethod
    def place_order(self, order: Order) -> bool:
        """Place an order"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> str:
        """Get order status"""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        pass
    
    @abstractmethod
    def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        pass
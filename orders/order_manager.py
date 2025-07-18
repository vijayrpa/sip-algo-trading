import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from data.storage import DatabaseManager
from brokers.base_broker import BaseBroker, Order

logger = logging.getLogger(__name__)

class OrderManager:
    def __init__(self, db_manager: DatabaseManager, broker: BaseBroker):
        self.db_manager = db_manager
        self.broker = broker
        self.active_orders = {}
        
    def place_market_order(self, symbol: str, side: str, quantity: int) -> Optional[str]:
        """Place a market order"""
        try:
            order = Order(symbol, side, quantity, 'MARKET')
            
            # Store in database
            self.db_manager.store_order(order.to_dict())
            
            # Place order with broker
            if self.broker.place_order(order):
                self.active_orders[order.order_id] = order
                logger.info(f"Market order placed: {order.order_id}")
                return order.order_id
            else:
                self.db_manager.update_order_status(order.order_id, 'FAILED')
                logger.error(f"Failed to place market order: {order.order_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error placing market order: {str(e)}")
            return None
    
    def place_limit_order(self, symbol: str, side: str, quantity: int, price: float) -> Optional[str]:
        """Place a limit order"""
        try:
            order = Order(symbol, side, quantity, 'LIMIT', price)
            
            # Store in database
            self.db_manager.store_order(order.to_dict())
            
            # Place order with broker
            if self.broker.place_order(order):
                self.active_orders[order.order_id] = order
                logger.info(f"Limit order placed: {order.order_id}")
                return order.order_id
            else:
                self.db_manager.update_order_status(order.order_id, 'FAILED')
                logger.error(f"Failed to place limit order: {order.order_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error placing limit order: {str(e)}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            if order_id in self.active_orders:
                if self.broker.cancel_order(order_id):
                    self.db_manager.update_order_status(order_id, 'CANCELLED')
                    del self.active_orders[order_id]
                    logger.info(f"Order cancelled: {order_id}")
                    return True
                else:
                    logger.error(f"Failed to cancel order: {order_id}")
                    return False
            else:
                logger.warning(f"Order not found in active orders: {order_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return False
    
    def update_order_statuses(self):
        """Update status of all active orders"""
        orders_to_remove = []
        
        for order_id, order in self.active_orders.items():
            try:
                current_status = self.broker.get_order_status(order_id)
                
                if current_status != order.status:
                    order.status = current_status
                    
                    if current_status in ['EXECUTED', 'CANCELLED', 'REJECTED']:
                        executed_at = datetime.now() if current_status == 'EXECUTED' else None
                        self.db_manager.update_order_status(order_id, current_status, executed_at)
                        orders_to_remove.append(order_id)
                        
            except Exception as e:
                logger.error(f"Error updating order status for {order_id}: {str(e)}")
        
        # Remove completed orders from active orders
        for order_id in orders_to_remove:
            del self.active_orders[order_id]
    
    def get_active_orders(self) -> List[Dict[str, Any]]:
        """Get all active orders"""
        return [order.to_dict() for order in self.active_orders.values()]
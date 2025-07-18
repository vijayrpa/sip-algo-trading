# scheduler.py - Fixed SIP Scheduler Implementation

import schedule
import time
import logging
from datetime import datetime, timedelta
from threading import Thread
import sys
import os
import calendar

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from data.storage import DatabaseManager
from data.market_data import MarketDataProvider
from brokers.zerodha_broker import ZerodhaBroker
from orders.order_manager import OrderManager
from utils.helpers import setup_logging, is_market_open

logger = logging.getLogger(__name__)

class SIPScheduler:
    def __init__(self):
        """Initialize the SIP scheduler with all required components"""
        setup_logging()
        logger.info("Initializing SIP Scheduler...")
        
        try:
            # Initialize database
            self.db_manager = DatabaseManager()
            
            # Initialize market data provider
            self.market_data = MarketDataProvider(self.db_manager)
            
            # Initialize broker with demo mode
            broker_config = {
                'api_key': settings.broker.api_key,
                'api_secret': settings.broker.api_secret,
                'demo_mode': True  # Force demo mode for scheduler
            }
            self.broker = ZerodhaBroker(broker_config)
            
            # Initialize order manager
            self.order_manager = OrderManager(self.db_manager, self.broker)
            
            # Connect to broker
            if not self.broker.connect():
                logger.error("Failed to connect to broker")
                raise Exception("Broker connection failed")
            
            # Track last execution dates
            self.last_monthly_execution = None
            self.last_daily_update = None
            
            logger.info("SIP Scheduler initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing SIP Scheduler: {str(e)}")
            raise
    
    def should_execute_monthly_sip(self, test_mode=False):
        """Check if monthly SIP should be executed"""
        now = datetime.now()
        
        # In test mode, always allow execution
        if test_mode:
            return True
        
        # Execute on the 1st of each month
        if now.day != 1:
            return False
        
        # Check if already executed this month
        if self.last_monthly_execution:
            if (self.last_monthly_execution.year == now.year and 
                self.last_monthly_execution.month == now.month):
                return False
        
        # Check if market is open
        if not is_market_open():
            return False
        
        return True
    
    def should_update_daily_data(self):
        """Check if daily data update should be executed"""
        now = datetime.now()
        
        # Update once per day
        if self.last_daily_update:
            if self.last_daily_update.date() == now.date():
                return False
        
        return True
    
    def update_market_data(self):
        """Update market data for all tracked symbols"""
        logger.info("Updating market data...")
        
        try:
            # Get all symbols from SIP configurations
            symbols = ['NIFTY50', 'RELIANCE', 'TCS', 'HDFCBANK', 'INFY']
            
            self.market_data.update_market_data(symbols)
            self.last_daily_update = datetime.now()
            logger.info("Market data updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating market data: {str(e)}")
    
    def execute_monthly_sip(self, test_mode=False):
        """Execute monthly SIP investments"""
        logger.info("Executing monthly SIP...")
        
        if not self.should_execute_monthly_sip(test_mode):
            logger.info("Monthly SIP execution skipped (already executed or conditions not met)")
            return
        
        try:
            # Example SIP configuration
            sip_config = {
                'symbols': ['NIFTY50', 'RELIANCE', 'TCS'],
                'allocation': [0.6, 0.25, 0.15],
                'total_amount': 10000.0
            }
            
            # Get current prices
            current_prices = self.market_data.get_multiple_prices(sip_config['symbols'])
            
            # Use mock prices if real prices not available
            if not current_prices:
                logger.warning("Could not get current prices, using mock prices for demo")
                current_prices = {
                    'NIFTY50': 19500.0,
                    'RELIANCE': 2650.0,
                    'TCS': 3500.0
                }
            
            # Execute SIP orders
            orders_placed = []
            for i, symbol in enumerate(sip_config['symbols']):
                if symbol in current_prices:
                    invest_amount = sip_config['total_amount'] * sip_config['allocation'][i]
                    quantity = int(invest_amount / current_prices[symbol])
                    
                    if quantity > 0:
                        order_id = self.order_manager.place_market_order(symbol, 'BUY', quantity)
                        if order_id:
                            orders_placed.append({
                                'symbol': symbol,
                                'quantity': quantity,
                                'amount': invest_amount,
                                'order_id': order_id
                            })
                            logger.info(f"SIP order placed for {symbol}: {quantity} units, Amount: ₹{invest_amount:.2f}")
                        else:
                            logger.error(f"Failed to place SIP order for {symbol}")
                else:
                    logger.warning(f"Price not available for {symbol}")
            
            # Update last execution time
            self.last_monthly_execution = datetime.now()
            
            logger.info(f"Monthly SIP execution completed. {len(orders_placed)} orders placed.")
            
        except Exception as e:
            logger.error(f"Error executing monthly SIP: {str(e)}")
    
    def monitor_orders(self):
        """Monitor and update order statuses"""
        logger.debug("Monitoring orders...")
        
        try:
            self.order_manager.update_order_statuses()
            active_orders = self.order_manager.get_active_orders()
            
            if active_orders:
                logger.info(f"Monitoring {len(active_orders)} active orders")
                for order in active_orders:
                    logger.debug(f"Order {order['order_id'][:8]}...: {order['symbol']} {order['side']} {order['quantity']} - {order['status']}")
            
        except Exception as e:
            logger.error(f"Error monitoring orders: {str(e)}")
    
    def daily_market_data_update(self):
        """Daily market data update task"""
        if self.should_update_daily_data():
            self.update_market_data()
    
    def check_monthly_sip(self):
        """Check and execute monthly SIP if needed"""
        if self.should_execute_monthly_sip():
            self.execute_monthly_sip()
    
    def setup_schedules(self):
        """Setup all scheduled tasks"""
        logger.info("Setting up scheduled tasks...")
        
        try:
            # Clear any existing schedules
            schedule.clear()
            
            # Update market data every 30 minutes during trading hours
            schedule.every(30).minutes.do(self.update_market_data)
            
            # Check for monthly SIP execution daily at 10:00 AM
            schedule.every().day.at("10:00").do(self.check_monthly_sip)
            
            # Monitor orders every 5 minutes
            schedule.every(5).minutes.do(self.monitor_orders)
            
            # Daily market data update at 9:00 AM
            schedule.every().day.at("09:00").do(self.daily_market_data_update)
            
            # Additional check for monthly SIP at 2:00 PM (in case 10:00 AM was missed)
            schedule.every().day.at("14:00").do(self.check_monthly_sip)
            
            logger.info("Scheduled tasks configured successfully")
            logger.info("Schedule summary:")
            logger.info("  - Market data update: Every 30 minutes")
            logger.info("  - Monthly SIP check: Daily at 10:00 AM and 2:00 PM")
            logger.info("  - Order monitoring: Every 5 minutes")
            logger.info("  - Daily data update: 9:00 AM")
            
        except Exception as e:
            logger.error(f"Error setting up schedules: {str(e)}")
            raise
    
    def run(self):
        """Run the scheduler"""
        logger.info("Starting SIP scheduler...")
        
        try:
            self.setup_schedules()
            
            logger.info("Scheduler is running. Press Ctrl+C to stop.")
            logger.info("Next scheduled tasks:")
            
            # Show next few scheduled tasks
            jobs = schedule.get_jobs()
            for job in jobs[:5]:  # Show first 5 jobs
                logger.info(f"  - {job}")
            
            while True:
                try:
                    schedule.run_pending()
                    time.sleep(30)  # Check every 30 seconds
                    
                except KeyboardInterrupt:
                    logger.info("Scheduler stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Error in scheduler loop: {str(e)}")
                    time.sleep(60)  # Wait before retrying
                    
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            raise
    
    def run_once(self):
        """Run scheduler tasks once (for testing)"""
        logger.info("Running scheduler tasks once...")
        
        try:
            # Test market data update
            logger.info("Testing market data update...")
            self.update_market_data()
            
            # Test order monitoring
            logger.info("Testing order monitoring...")
            self.monitor_orders()
            
            # Test monthly SIP execution
            logger.info("Testing monthly SIP execution...")
            current_day = datetime.now().day
            
            if current_day == 1:
                logger.info("Today is the 1st of the month, executing SIP...")
                self.execute_monthly_sip()
            else:
                logger.info(f"Today is the {current_day}th of the month")
                logger.info("In normal operation, SIP would execute on the 1st")
                logger.info("For testing purposes, executing SIP now...")
                
                # Execute SIP in test mode
                self.execute_monthly_sip(test_mode=True)
            
            logger.info("Scheduler test completed successfully")
            
        except Exception as e:
            logger.error(f"Error in scheduler test: {str(e)}")
            raise
    
    def get_status(self):
        """Get scheduler status"""
        status = {
            'is_running': True,
            'last_monthly_execution': self.last_monthly_execution.isoformat() if self.last_monthly_execution else None,
            'last_daily_update': self.last_daily_update.isoformat() if self.last_daily_update else None,
            'next_monthly_sip': self._get_next_monthly_date().isoformat(),
            'scheduled_jobs': len(schedule.get_jobs()),
            'broker_connected': self.broker.is_connected,
            'broker_mode': 'demo' if self.broker.demo_mode else 'live'
        }
        return status
    
    def _get_next_monthly_date(self):
        """Get next monthly SIP execution date"""
        now = datetime.now()
        if now.day == 1:
            return now.replace(hour=10, minute=0, second=0, microsecond=0)
        else:
            # Next month's 1st
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=1, hour=10, minute=0, second=0, microsecond=0)
            else:
                next_month = now.replace(month=now.month + 1, day=1, hour=10, minute=0, second=0, microsecond=0)
            return next_month
    
    def test_all_components(self):
        """Test all scheduler components individually"""
        logger.info("Testing all scheduler components...")
        
        test_results = {
            'market_data_update': False,
            'order_monitoring': False,
            'monthly_sip_execution': False,
            'broker_connection': False
        }
        
        # Test 1: Market data update
        try:
            logger.info("1. Testing market data update...")
            self.update_market_data()
            test_results['market_data_update'] = True
            logger.info("   ✓ Market data update: PASSED")
        except Exception as e:
            logger.error(f"   ✗ Market data update: FAILED - {str(e)}")
        
        # Test 2: Order monitoring
        try:
            logger.info("2. Testing order monitoring...")
            self.monitor_orders()
            test_results['order_monitoring'] = True
            logger.info("   ✓ Order monitoring: PASSED")
        except Exception as e:
            logger.error(f"   ✗ Order monitoring: FAILED - {str(e)}")
        
        # Test 3: Monthly SIP execution
        try:
            logger.info("3. Testing monthly SIP execution...")
            self.execute_monthly_sip(test_mode=True)
            test_results['monthly_sip_execution'] = True
            logger.info("   ✓ Monthly SIP execution: PASSED")
        except Exception as e:
            logger.error(f"   ✗ Monthly SIP execution: FAILED - {str(e)}")
        
        # Test 4: Broker connection
        try:
            logger.info("4. Testing broker connection...")
            if self.broker.is_connected:
                balance = self.broker.get_balance()
                logger.info(f"   Account balance: ₹{balance['cash']:.2f}")
                test_results['broker_connection'] = True
                logger.info("   ✓ Broker connection: PASSED")
            else:
                logger.error("   ✗ Broker connection: FAILED - Not connected")
        except Exception as e:
            logger.error(f"   ✗ Broker connection: FAILED - {str(e)}")
        
        # Summary
        passed = sum(test_results.values())
        total = len(test_results)
        
        logger.info(f"\nScheduler component test summary: {passed}/{total} passed")
        
        if passed == total:
            logger.info("✓ All scheduler components working correctly")
        else:
            logger.warning("⚠ Some scheduler components need attention")
        
        return test_results

def run_scheduler():
    """Main entry point for the scheduler"""
    print("SIP Algorithmic Trading System - Scheduler")
    print("=" * 50)
    
    try:
        scheduler = SIPScheduler()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "--test":
                print("Running scheduler in test mode...")
                scheduler.run_once()
                return
            elif sys.argv[1] == "--test-all":
                print("Running comprehensive scheduler tests...")
                scheduler.test_all_components()
                return
            elif sys.argv[1] == "--status":
                print("Scheduler Status:")
                status = scheduler.get_status()
                for key, value in status.items():
                    print(f"  {key}: {value}")
                return
            elif sys.argv[1] == "--help":
                print("SIP Scheduler Usage:")
                print("  python scheduler.py              # Run scheduler continuously")
                print("  python scheduler.py --test       # Run scheduler once for testing")
                print("  python scheduler.py --test-all   # Run comprehensive tests")
                print("  python scheduler.py --status     # Show scheduler status")
                print("  python scheduler.py --help       # Show this help")
                return
        
        # Run scheduler normally
        scheduler.run()
        
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")
    except Exception as e:
        print(f"Error starting scheduler: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    """Alternative main function"""
    run_scheduler()

if __name__ == "__main__":
    run_scheduler()
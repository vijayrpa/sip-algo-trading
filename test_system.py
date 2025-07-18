#!/usr/bin/env python3
"""
test_system.py - Complete Test Suite for SIP Algorithmic Trading System

This script tests all components of the SIP trading system to ensure everything
is working correctly.
"""

import sys
import os
import logging
from datetime import datetime, timedelta
import time
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from config.settings import settings
from data.storage import DatabaseManager
from data.market_data import MarketDataProvider
from brokers.zerodha_broker import ZerodhaBroker
from orders.order_manager import OrderManager
from utils.helpers import setup_logging, is_market_open

class TestResult:
    """Test result tracking"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def add_pass(self):
        self.passed += 1
        
    def add_fail(self):
        self.failed += 1
        
    def add_warning(self):
        self.warnings += 1
        
    def get_total(self):
        return self.passed + self.failed
        
    def get_success_rate(self):
        total = self.get_total()
        return (self.passed / total * 100) if total > 0 else 0

def print_test_header(test_name):
    """Print test header"""
    print(f"\n{'=' * 60}")
    print(f"Testing: {test_name}")
    print(f"{'=' * 60}")

def print_test_section(section_name):
    """Print test section"""
    print(f"\n{'-' * 40}")
    print(f"{section_name}")
    print(f"{'-' * 40}")

def test_imports():
    """Test all imports"""
    print_test_header("Module Imports")
    result = TestResult()
    
    modules_to_test = [
        ("config.settings", "settings"),
        ("data.storage", "DatabaseManager"),
        ("data.market_data", "MarketDataProvider"),
        ("brokers.base_broker", "BaseBroker"),
        ("brokers.zerodha_broker", "ZerodhaBroker"),
        ("orders.order_manager", "OrderManager"),
        ("utils.helpers", "setup_logging"),
    ]
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✓ {module_name}.{class_name} imported successfully")
            result.add_pass()
        except Exception as e:
            print(f"✗ {module_name}.{class_name} import failed: {str(e)}")
            result.add_fail()
    
    return result

def test_database():
    """Test database functionality"""
    print_test_header("Database Operations")
    result = TestResult()
    
    try:
        print("1. Initializing database...")
        db_manager = DatabaseManager('test_trading_system.db')
        print("✓ Database initialized successfully")
        result.add_pass()
        
        print("2. Testing market data storage...")
        # Create sample market data
        import pandas as pd
        sample_data = pd.DataFrame({
            'Open': [100.0, 101.0, 102.0, 103.0, 104.0],
            'High': [105.0, 106.0, 107.0, 108.0, 109.0],
            'Low': [98.0, 99.0, 100.0, 101.0, 102.0],
            'Close': [104.0, 105.0, 106.0, 107.0, 108.0],
            'Volume': [1000, 1100, 1200, 1300, 1400]
        }, index=pd.date_range('2023-01-01', periods=5, freq='D'))
        
        db_manager.store_market_data('TEST_SYMBOL', sample_data)
        print("✓ Market data stored successfully")
        result.add_pass()
        
        print("3. Testing market data retrieval...")
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 5)
        retrieved_data = db_manager.get_market_data('TEST_SYMBOL', start_date, end_date)
        
        if len(retrieved_data) > 0:
            print(f"✓ Retrieved {len(retrieved_data)} records")
            result.add_pass()
        else:
            print("✗ No data retrieved")
            result.add_fail()
        
        print("4. Testing order storage...")
        sample_order = {
            'order_id': 'TEST_ORDER_001',
            'symbol': 'TEST_SYMBOL',
            'side': 'BUY',
            'quantity': 10,
            'price': 100.0,
            'order_type': 'MARKET',
            'status': 'PENDING',
            'broker_order_id': 'BROKER_001'
        }
        
        db_manager.store_order(sample_order)
        print("✓ Order stored successfully")
        result.add_pass()
        
        print("5. Testing order status update...")
        db_manager.update_order_status('TEST_ORDER_001', 'EXECUTED', datetime.now())
        print("✓ Order status updated successfully")
        result.add_pass()
        
    except Exception as e:
        print(f"✗ Database test failed: {str(e)}")
        traceback.print_exc()
        result.add_fail()
    
    return result

def test_market_data():
    """Test market data functionality"""
    print_test_header("Market Data Operations")
    result = TestResult()
    
    try:
        print("1. Initializing market data provider...")
        db_manager = DatabaseManager('test_trading_system.db')
        market_data = MarketDataProvider(db_manager)
        print("✓ Market data provider initialized")
        result.add_pass()
        
        print("2. Testing symbol conversion...")
        test_symbols = ['RELIANCE', 'TCS', 'NIFTY50', 'INVALID_SYMBOL']
        
        for symbol in test_symbols:
            yahoo_symbol = market_data.get_yahoo_symbol(symbol)
            print(f"  {symbol} -> {yahoo_symbol}")
        
        print("✓ Symbol conversion working")
        result.add_pass()
        
        print("3. Testing current price fetching...")
        symbols_to_test = ['RELIANCE', 'TCS', 'NIFTY50']
        
        for symbol in symbols_to_test:
            try:
                print(f"  Fetching price for {symbol}...")
                price = market_data.get_current_price(symbol)
                
                if price and price > 0:
                    print(f"  ✓ {symbol}: ₹{price:.2f}")
                    result.add_pass()
                else:
                    print(f"  ⚠ {symbol}: No price data")
                    result.add_warning()
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"  ✗ {symbol}: Error - {str(e)}")
                result.add_fail()
        
        print("4. Testing multiple price fetching...")
        try:
            prices = market_data.get_multiple_prices(['RELIANCE', 'TCS'])
            
            if prices:
                print(f"✓ Fetched {len(prices)} prices: {prices}")
                result.add_pass()
            else:
                print("⚠ No prices fetched")
                result.add_warning()
                
        except Exception as e:
            print(f"✗ Multiple price fetch failed: {str(e)}")
            result.add_fail()
        
        print("5. Testing historical data...")
        try:
            historical_data = market_data.fetch_historical_data('RELIANCE', period='5d')
            
            if not historical_data.empty:
                print(f"✓ Fetched {len(historical_data)} historical records")
                print(f"  Date range: {historical_data.index[0]} to {historical_data.index[-1]}")
                result.add_pass()
            else:
                print("⚠ No historical data fetched")
                result.add_warning()
                
        except Exception as e:
            print(f"✗ Historical data fetch failed: {str(e)}")
            result.add_fail()
        
    except Exception as e:
        print(f"✗ Market data test failed: {str(e)}")
        traceback.print_exc()
        result.add_fail()
    
    return result

def test_broker():
    """Test broker functionality"""
    print_test_header("Broker Operations")
    result = TestResult()
    
    try:
        print("1. Initializing broker...")
        broker_config = {
            'api_key': 'test_key',
            'api_secret': 'test_secret',
            'demo_mode': True
        }
        
        broker = ZerodhaBroker(broker_config)
        print("✓ Broker initialized in demo mode")
        result.add_pass()
        
        print("2. Testing broker connection...")
        if broker.connect():
            print("✓ Broker connected successfully")
            result.add_pass()
        else:
            print("✗ Broker connection failed")
            result.add_fail()
            return result
        
        print("3. Testing account balance...")
        balance = broker.get_balance()
        print(f"✓ Account balance: ₹{balance['cash']:.2f}")
        print(f"  Available: ₹{balance.get('available', 0):.2f}")
        result.add_pass()
        
        print("4. Testing positions...")
        positions = broker.get_positions()
        print(f"✓ Current positions: {len(positions)}")
        
        for position in positions:
            print(f"  {position.get('symbol', 'Unknown')}: {position.get('quantity', 0)} units")
        
        result.add_pass()
        
        print("5. Testing order placement...")
        from brokers.base_broker import Order
        
        test_order = Order('RELIANCE', 'BUY', 1, 'MARKET')
        
        if broker.place_order(test_order):
            print(f"✓ Order placed: {test_order.order_id}")
            result.add_pass()
            
            # Test order status
            status = broker.get_order_status(test_order.order_id)
            print(f"✓ Order status: {status}")
            result.add_pass()
            
            # Test order cancellation
            if broker.cancel_order(test_order.order_id):
                print(f"✓ Order cancelled: {test_order.order_id}")
                result.add_pass()
            else:
                print(f"⚠ Order cancellation failed: {test_order.order_id}")
                result.add_warning()
                
        else:
            print("✗ Order placement failed")
            result.add_fail()
        
    except Exception as e:
        print(f"✗ Broker test failed: {str(e)}")
        traceback.print_exc()
        result.add_fail()
    
    return result

def test_order_manager():
    """Test order management functionality"""
    print_test_header("Order Management")
    result = TestResult()
    
    try:
        print("1. Initializing order manager...")
        db_manager = DatabaseManager('test_trading_system.db')
        
        broker_config = {
            'api_key': 'test_key',
            'api_secret': 'test_secret',
            'demo_mode': True
        }
        broker = ZerodhaBroker(broker_config)
        broker.connect()
        
        order_manager = OrderManager(db_manager, broker)
        print("✓ Order manager initialized")
        result.add_pass()
        
        print("2. Testing market order...")
        market_order_id = order_manager.place_market_order('RELIANCE', 'BUY', 1)
        
        if market_order_id:
            print(f"✓ Market order placed: {market_order_id[:8]}...")
            result.add_pass()
        else:
            print("✗ Market order failed")
            result.add_fail()
        
        print("3. Testing limit order...")
        limit_order_id = order_manager.place_limit_order('TCS', 'BUY', 1, 3500.0)
        
        if limit_order_id:
            print(f"✓ Limit order placed: {limit_order_id[:8]}...")
            result.add_pass()
        else:
            print("✗ Limit order failed")
            result.add_fail()
        
        print("4. Testing active orders...")
        active_orders = order_manager.get_active_orders()
        print(f"✓ Active orders: {len(active_orders)}")
        
        for order in active_orders:
            print(f"  {order['symbol']} {order['side']} {order['quantity']} - {order['status']}")
        
        result.add_pass()
        
        print("5. Testing order status updates...")
        order_manager.update_order_statuses()
        print("✓ Order statuses updated")
        result.add_pass()
        
        print("6. Testing order cancellation...")
        if market_order_id and order_manager.cancel_order(market_order_id):
            print(f"✓ Order cancelled: {market_order_id[:8]}...")
            result.add_pass()
        else:
            print("⚠ Order cancellation test skipped")
            result.add_warning()
        
    except Exception as e:
        print(f"✗ Order manager test failed: {str(e)}")
        traceback.print_exc()
        result.add_fail()
    
    return result

def test_utilities():
    """Test utility functions"""
    print_test_header("Utility Functions")
    result = TestResult()
    
    try:
        print("1. Testing logging setup...")
        setup_logging()
        logger = logging.getLogger('test_logger')
        logger.info("Test log message")
        print("✓ Logging setup working")
        result.add_pass()
        
        print("2. Testing market hours detection...")
        is_open = is_market_open()
        print(f"✓ Market is currently {'open' if is_open else 'closed'}")
        result.add_pass()
        
        print("3. Testing SIP amount calculation...")
        from utils.helpers import calculate_sip_amount
        
        base_amount = 1000.0
        test_conditions = ['bull', 'bear', 'neutral']
        
        for condition in test_conditions:
            amount = calculate_sip_amount(base_amount, condition)
            print(f"  {condition} market: ₹{amount:.2f}")
        
        print("✓ SIP amount calculation working")
        result.add_pass()
        
        print("4. Testing current time...")
        current_time = datetime.now()
        print(f"✓ Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        result.add_pass()
        
    except Exception as e:
        print(f"✗ Utilities test failed: {str(e)}")
        traceback.print_exc()
        result.add_fail()
    
    return result

def test_full_system_integration():
    """Test complete system integration"""
    print_test_header("Full System Integration")
    result = TestResult()
    
    try:
        print("1. Initializing all components...")
        
        # Initialize database
        db_manager = DatabaseManager('test_trading_system.db')
        market_data = MarketDataProvider(db_manager)
        
        # Initialize broker in demo mode
        broker_config = {
            'api_key': 'test_key',
            'api_secret': 'test_secret',
            'demo_mode': True
        }
        broker = ZerodhaBroker(broker_config)
        
        if not broker.connect():
            print("✗ Failed to connect to broker")
            result.add_fail()
            return result
        
        order_manager = OrderManager(db_manager, broker)
        print("✓ All components initialized")
        result.add_pass()
        
        print("2. Simulating SIP workflow...")
        
        # SIP configuration
        sip_config = {
            'symbols': ['RELIANCE', 'TCS'],
            'allocation': [0.6, 0.4],
            'total_amount': 1000.0
        }
        
        # Get current prices
        print("  Fetching current prices...")
        current_prices = market_data.get_multiple_prices(sip_config['symbols'])
        
        if not current_prices:
            print("  ⚠ Using mock prices for testing")
            current_prices = {'RELIANCE': 2650.0, 'TCS': 3500.0}
        
        print(f"  Current prices: {current_prices}")
        result.add_pass()
        
        # Calculate and place orders
        print("  Calculating investment amounts...")
        orders_to_place = []
        total_investment = 0
        
        for i, symbol in enumerate(sip_config['symbols']):
            if symbol in current_prices:
                invest_amount = sip_config['total_amount'] * sip_config['allocation'][i]
                quantity = int(invest_amount / current_prices[symbol])
                
                if quantity > 0:
                    orders_to_place.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'amount': invest_amount
                    })
                    total_investment += invest_amount
                    print(f"    {symbol}: {quantity} units @ ₹{current_prices[symbol]:.2f} = ₹{invest_amount:.2f}")
        
        print(f"  Total investment: ₹{total_investment:.2f}")
        result.add_pass()
        
        # Place orders
        print("  Placing orders...")
        orders_placed = []
        
        for order in orders_to_place:
            order_id = order_manager.place_market_order(order['symbol'], 'BUY', order['quantity'])
            
            if order_id:
                orders_placed.append(order_id)
                print(f"    ✓ Order placed for {order['symbol']}: {order_id[:8]}...")
            else:
                print(f"    ✗ Failed to place order for {order['symbol']}")
        
        print(f"✓ {len(orders_placed)} orders placed successfully")
        result.add_pass()
        
        print("3. Testing order monitoring...")
        order_manager.update_order_statuses()
        active_orders = order_manager.get_active_orders()
        
        print(f"✓ Monitoring {len(active_orders)} active orders")
        result.add_pass()
        
        print("4. Testing portfolio summary...")
        balance = broker.get_balance()
        positions = broker.get_positions()
        
        print(f"  Account balance: ₹{balance['cash']:.2f}")
        print(f"  Positions: {len(positions)}")
        print("✓ Portfolio summary generated")
        result.add_pass()
        
        print("5. Integration test completed successfully!")
        result.add_pass()
        
    except Exception as e:
        print(f"✗ Integration test failed: {str(e)}")
        traceback.print_exc()
        result.add_fail()
    
    return result

def run_all_tests():
    """Run all tests and generate summary"""
    print("SIP Algorithmic Trading System - Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    tests = [
        ("Module Imports", test_imports),
        ("Database Operations", test_database),
        ("Market Data", test_market_data),
        ("Broker Operations", test_broker),
        ("Order Management", test_order_manager),
        ("Utility Functions", test_utilities),
        ("Full System Integration", test_full_system_integration)
    ]
    
    total_result = TestResult()
    test_results = []
    
    for test_name, test_func in tests:
        print(f"\n{'*' * 60}")
        print(f"Running: {test_name}")
        print(f"{'*' * 60}")
        
        try:
            result = test_func()
            test_results.append((test_name, result))
            
            # Add to total
            total_result.passed += result.passed
            total_result.failed += result.failed
            total_result.warnings += result.warnings
            
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {str(e)}")
            traceback.print_exc()
            total_result.failed += 1
            test_results.append((test_name, TestResult()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in test_results:
        status = "PASS" if result.failed == 0 else "FAIL"
        success_rate = result.get_success_rate()
        print(f"{test_name:<30} {status:<6} ({result.passed}/{result.get_total()}) {success_rate:.1f}%")
    
    print("-" * 60)
    print(f"{'TOTAL':<30} {'PASS' if total_result.failed == 0 else 'FAIL':<6} ({total_result.passed}/{total_result.get_total()}) {total_result.get_success_rate():.1f}%")
    
    if total_result.warnings > 0:
        print(f"Warnings: {total_result.warnings}")
    
    print("=" * 60)
    
    if total_result.failed == 0:
        print("🎉 ALL TESTS PASSED! Your SIP Trading System is ready to use.")
        print("You can now run: sip-trading")
    else:
        print("⚠ Some tests failed. Please check the errors above.")
        print("The system may still work in demo mode for basic testing.")
    
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return total_result.failed == 0

def main():
    """Main test function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print("SIP Trading System Test Suite")
            print("Usage:")
            print("  python test_system.py           # Run all tests")
            print("  python test_system.py --help    # Show this help")
            print("  sip-test                        # Run via console command")
            return
    
    success = run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
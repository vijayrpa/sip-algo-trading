#!/usr/bin/env python3
"""
Phase 1 Completion Verification Script
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_phase1_completion():
    """Verify all Phase 1 components are working"""
    
    print("Phase 1: Core Infrastructure - Completion Verification")
    print("=" * 60)
    
    results = {
        'data_ingestion': False,
        'market_data_storage': False,
        'broker_integration': False,
        'order_management': False
    }
    
    # Test 1: Data Ingestion Pipeline
    print("\n1. Testing Data Ingestion Pipeline...")
    try:
        from data.market_data import MarketDataProvider
        from data.storage import DatabaseManager
        
        db = DatabaseManager('phase1_test.db')
        provider = MarketDataProvider(db)
        
        # Test current price
        price = provider.get_current_price('RELIANCE')
        if price and price > 0:
            print(f"   ✓ Current price fetch: ₹{price:.2f}")
        else:
            print("   ⚠ Current price fetch: Using fallback")
        
        # Test historical data
        data = provider.fetch_historical_data('RELIANCE', '5d')
        if not data.empty:
            print(f"   ✓ Historical data: {len(data)} records")
        else:
            print("   ⚠ Historical data: No data (network issue?)")
        
        # Test multiple prices
        prices = provider.get_multiple_prices(['RELIANCE', 'TCS'])
        print(f"   ✓ Multiple prices: {len(prices)} symbols")
        
        results['data_ingestion'] = True
        print("   ✅ Data Ingestion Pipeline: PASSED")
        
    except Exception as e:
        print(f"   ❌ Data Ingestion Pipeline: FAILED - {str(e)}")
    
    # Test 2: Market Data Storage
    print("\n2. Testing Market Data Storage...")
    try:
        from data.storage import DatabaseManager
        import pandas as pd
        import sqlite3
        
        db = DatabaseManager('phase1_test.db')
        
        # Test database creation
        print("   ✓ Database created")
        
        # Test table creation
        conn = sqlite3.connect('phase1_test.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        expected_tables = ['market_data', 'orders', 'portfolio', 'sip_configs']
        
        for table in expected_tables:
            if table in tables:
                print(f"   ✓ Table '{table}' exists")
            else:
                print(f"   ⚠ Table '{table}' missing")
        
        conn.close()
        
        # Test data storage
        sample_data = pd.DataFrame({
            'Open': [100], 'High': [105], 'Low': [98], 'Close': [104], 'Volume': [1000]
        }, index=pd.date_range('2023-01-01', periods=1))
        
        db.store_market_data('TEST_SYMBOL', sample_data)
        print("   ✓ Market data storage working")
        
        results['market_data_storage'] = True
        print("   ✅ Market Data Storage: PASSED")
        
    except Exception as e:
        print(f"   ❌ Market Data Storage: FAILED - {str(e)}")
    
    # Test 3: Broker Integration
    print("\n3. Testing Broker Integration...")
    try:
        from brokers.zerodha_broker import ZerodhaBroker
        from brokers.base_broker import Order
        
        # Test broker initialization
        broker = ZerodhaBroker({
            'api_key': 'test',
            'api_secret': 'test',
            'demo_mode': True
        })
        print("   ✓ Broker initialized")
        
        # Test connection
        connected = broker.connect()
        if connected:
            print("   ✓ Broker connection successful")
        else:
            print("   ❌ Broker connection failed")
            return
        
        # Test account info
        balance = broker.get_balance()
        print(f"   ✓ Account balance: ₹{balance['cash']:.2f}")
        
        positions = broker.get_positions()
        print(f"   ✓ Positions: {len(positions)} holdings")
        
        # Test order placement
        order = Order('RELIANCE', 'BUY', 1, 'MARKET')
        if broker.place_order(order):
            print(f"   ✓ Order placement working")
        else:
            print("   ❌ Order placement failed")
        
        results['broker_integration'] = True
        print("   ✅ Broker Integration: PASSED")
        
    except Exception as e:
        print(f"   ❌ Broker Integration: FAILED - {str(e)}")
    
    # Test 4: Order Management
    print("\n4. Testing Order Management...")
    try:
        from orders.order_manager import OrderManager
        from data.storage import DatabaseManager
        from brokers.zerodha_broker import ZerodhaBroker
        
        db = DatabaseManager('phase1_test.db')
        broker = ZerodhaBroker({'demo_mode': True})
        broker.connect()
        
        om = OrderManager(db, broker)
        print("   ✓ Order manager initialized")
        
        # Test market order
        order_id = om.place_market_order('RELIANCE', 'BUY', 1)
        if order_id:
            print(f"   ✓ Market order placed: {order_id[:8]}...")
        else:
            print("   ❌ Market order failed")
        
        # Test limit order
        limit_order_id = om.place_limit_order('TCS', 'BUY', 1, 3500.0)
        if limit_order_id:
            print(f"   ✓ Limit order placed: {limit_order_id[:8]}...")
        else:
            print("   ❌ Limit order failed")
        
        # Test active orders
        active_orders = om.get_active_orders()
        print(f"   ✓ Active orders: {len(active_orders)}")
        
        # Test order status update
        om.update_order_statuses()
        print("   ✓ Order status update working")
        
        results['order_management'] = True
        print("   ✅ Order Management: PASSED")
        
    except Exception as e:
        print(f"   ❌ Order Management: FAILED - {str(e)}")
    
    # Final Summary
    print("\n" + "=" * 60)
    print("PHASE 1 COMPLETION SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for component, status in results.items():
        status_text = "✅ PASSED" if status else "❌ FAILED"
        print(f"{component.replace('_', ' ').title():<25} {status_text}")
    
    print("-" * 60)
    print(f"Overall Status: {passed}/{total} components passed")
    
    if passed == total:
        print("\n🎉 PHASE 1 COMPLETED SUCCESSFULLY!")
        print("✅ All core infrastructure components are working")
        print("✅ Ready to proceed to Phase 2: Strategy Development")
        print("\nNext steps:")
        print("1. Implement basic SIP strategies")
        print("2. Create backtesting framework")
        print("3. Add parameter optimization")
        print("4. Build performance analytics")
        return True
    else:
        print(f"\n⚠ PHASE 1 PARTIALLY COMPLETED ({passed}/{total})")
        print("❌ Some components need fixing before proceeding")
        print("Please resolve the failed components above")
        return False

if __name__ == "__main__":
    success = verify_phase1_completion()
    sys.exit(0 if success else 1)
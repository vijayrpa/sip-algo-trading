import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = 'trading_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Market data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                open_price REAL,
                high_price REAL,
                low_price REAL,
                close_price REAL,
                volume INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp)
            )
        ''')
        
        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL,
                order_type TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                executed_at DATETIME,
                broker_order_id TEXT
            )
        ''')
        
        # Portfolio table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                average_price REAL NOT NULL,
                current_price REAL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol)
            )
        ''')
        
        # SIP configurations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sip_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                symbols TEXT NOT NULL,
                amount REAL NOT NULL,
                frequency TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def store_market_data(self, symbol: str, data: pd.DataFrame):
        """Store market data in database"""
        conn = sqlite3.connect(self.db_path)
        
        # Prepare data for insertion
        data_to_insert = []
        for index, row in data.iterrows():
            data_to_insert.append((
                symbol,
                index.strftime('%Y-%m-%d %H:%M:%S'),
                row.get('Open', 0),
                row.get('High', 0),
                row.get('Low', 0),
                row.get('Close', 0),
                row.get('Volume', 0)
            ))
        
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT OR REPLACE INTO market_data 
            (symbol, timestamp, open_price, high_price, low_price, close_price, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', data_to_insert)
        
        conn.commit()
        conn.close()
        logger.info(f"Stored {len(data_to_insert)} records for {symbol}")
    
    def get_market_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Retrieve market data from database"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT timestamp, open_price, high_price, low_price, close_price, volume
            FROM market_data
            WHERE symbol = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        '''
        
        df = pd.read_sql_query(
            query, 
            conn, 
            params=(symbol, start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S')),
            parse_dates=['timestamp'],
            index_col='timestamp'
        )
        
        conn.close()
        return df
    
    def store_order(self, order_data: Dict[str, Any]):
        """Store order in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO orders (order_id, symbol, side, quantity, price, order_type, status, broker_order_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_data['order_id'],
            order_data['symbol'],
            order_data['side'],
            order_data['quantity'],
            order_data.get('price', 0),
            order_data['order_type'],
            order_data['status'],
            order_data.get('broker_order_id', '')
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Stored order {order_data['order_id']}")
    
    def update_order_status(self, order_id: str, status: str, executed_at: Optional[datetime] = None):
        """Update order status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if executed_at:
            cursor.execute('''
                UPDATE orders 
                SET status = ?, executed_at = ?, updated_at = CURRENT_TIMESTAMP
                WHERE order_id = ?
            ''', (status, executed_at.strftime('%Y-%m-%d %H:%M:%S'), order_id))
        else:
            cursor.execute('''
                UPDATE orders 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE order_id = ?
            ''', (status, order_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Updated order {order_id} status to {status}")
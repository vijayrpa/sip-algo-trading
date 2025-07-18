# config/settings.py - Updated with better defaults and validation

import os
from dataclasses import dataclass
from typing import Dict, Any
import json

@dataclass
class DatabaseConfig:
    host: str = 'localhost'
    port: int = 5432
    username: str = 'postgres'
    password: str = 'password'
    database: str = 'sip_trading'

@dataclass
class BrokerConfig:
    name: str = 'zerodha'
    api_key: str = 'hpycfxf32uefnxku'
    api_secret: str = 'v0r1oa69cz3xstc8a7wqffvecuzw0reu'
    redirect_url: str = 'http://localhost:8080/callback'
    demo_mode: bool = True  # Add demo mode flag
    
@dataclass
class TradingConfig:
    market_open_time: str = '09:15'
    market_close_time: str = '15:30'
    timezone: str = 'Asia/Kolkata'
    max_orders_per_day: int = 100
    default_sip_amount: float = 1000.0
    demo_mode: bool = True  # Add demo mode flag

class Settings:
    def __init__(self):
        self.database = DatabaseConfig()
        self.broker = BrokerConfig()
        self.trading = TradingConfig()
        self.load_from_env()
        
    def load_from_env(self):
        """Load configuration from environment variables"""
        self.broker.api_key = os.getenv('ZERODHA_API_KEY', '')
        self.broker.api_secret = os.getenv('ZERODHA_API_SECRET', '')
        self.database.password = os.getenv('DB_PASSWORD', 'password')
        
        # Set demo mode based on whether we have real credentials
        self.broker.demo_mode = not (self.broker.api_key and self.broker.api_secret)
        self.trading.demo_mode = self.broker.demo_mode
        
    def save_config(self, filepath: str = 'config.json'):
        """Save configuration to file"""
        config_dict = {
            'database': self.database.__dict__,
            'broker': self.broker.__dict__,
            'trading': self.trading.__dict__
        }
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
            
    def load_config(self, filepath: str = 'config.json'):
        """Load configuration from file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                config_dict = json.load(f)
                self.database = DatabaseConfig(**config_dict.get('database', {}))
                self.broker = BrokerConfig(**config_dict.get('broker', {}))
                self.trading = TradingConfig(**config_dict.get('trading', {}))

# Global settings instance
settings = Settings()

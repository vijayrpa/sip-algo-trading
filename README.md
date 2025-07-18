# SIP Algorithmic Trading System

A comprehensive algorithmic trading system for Systematic Investment Plans (SIPs) in the Indian stock market.

## Features

- **Automated SIP Execution**: Schedule and execute SIP investments automatically
- **Multiple Brokers Support**: Zerodha integration with extensible broker interface
- **Real-time Data**: Market data from Yahoo Finance and broker APIs
- **Risk Management**: Built-in risk controls and position limits
- **Web API**: REST API for monitoring and control
- **Database Storage**: SQLite for development, PostgreSQL for production
- **Backtesting**: Test strategies on historical data
- **Monitoring**: Real-time order and portfolio monitoring

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ItsMePatidar/sip-algo-trading.git
cd sip-algo-trading

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### Configuration

1. Copy the environment template:
```bash
cp .env.template .env
```

2. Update `.env` with your broker credentials:
```
ZERODHA_API_KEY=your_api_key_here
ZERODHA_API_SECRET=your_api_secret_here
```

3. Update `config.json` with your SIP preferences

### Running the System

```bash
# Run tests
sip-test

# Start the main system
sip-trading

# Start the scheduler
sip-scheduler

# Start the web API
sip-api
```

## Project Structure

```
sip-algo-trading/
├── setup.py                    # Package configuration
├── requirements.txt            # Dependencies
├── main.py                     # Main application
├── scheduler.py                # SIP scheduler
├── web_api.py                  # Web API
├── config/                     # Configuration modules
├── data/                       # Data handling
├── brokers/                    # Broker integrations
├── orders/                     # Order management
└── utils/                      # Utilities
```

## Documentation

- [Installation Guide](docs/installation.md)
- [Configuration](docs/configuration.md)
- [API Documentation](docs/api.md)
- [Strategy Development](docs/strategies.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Use at your own risk. The authors are not responsible for any financial losses.
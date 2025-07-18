import os
from setuptools import setup, find_packages

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as fh:
            return fh.read()
    return "SIP Algorithmic Trading System for Indian Markets"

# Read version from a version file
def read_version():
    version_path = os.path.join(os.path.dirname(__file__), 'VERSION')
    if os.path.exists(version_path):
        with open(version_path, 'r', encoding='utf-8') as fh:
            return fh.read().strip()
    return "0.1.0"

# Core dependencies
INSTALL_REQUIRES = [
    "yfinance>=0.2.18",
    "pandas>=2.0.3",
    "numpy>=1.24.3",
    "pytz>=2023.3",
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
    "SQLAlchemy>=2.0.19",
    "fastapi>=0.103.1",
    "uvicorn>=0.23.2",
    "pydantic>=2.3.0",
    "celery>=5.3.1",
    "redis>=4.6.0",
    "schedule>=1.2.0",
    "structlog>=23.1.0",
    "httpx>=0.24.1",
    "pyyaml>=6.0.1",
    "marshmallow>=3.20.1",
    "python-dateutil>=2.8.2",
    "click>=8.1.7",
    "tqdm>=4.66.1",
]

# Optional dependencies
EXTRAS_REQUIRE = {
    "dev": [
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.1",
        "pytest-cov>=4.1.0",
        "black>=23.7.0",
        "flake8>=6.0.0",
        "isort>=5.12.0",
        "mypy>=1.5.1",
        "pre-commit>=3.3.3",
    ],
    "zerodha": [
        "kiteconnect>=4.0.0",
    ],
    "analysis": [
        "scipy>=1.11.1",
        "scikit-learn>=1.3.0",
        "matplotlib>=3.7.2",
        "seaborn>=0.12.2",
        "jupyter>=1.0.0",
        "plotly>=5.15.0",
    ],
    "excel": [
        "openpyxl>=3.1.2",
        "xlsxwriter>=3.1.2",
    ],
    "database": [
        "psycopg2-binary>=2.9.7",  # PostgreSQL
        "influxdb-client>=1.37.0",  # InfluxDB for time series
    ],
    "monitoring": [
        "prometheus-client>=0.17.1",
        "grafana-api>=1.0.3",
    ],
}

# All optional dependencies
EXTRAS_REQUIRE["all"] = list(set(sum(EXTRAS_REQUIRE.values(), [])))

setup(
    name="sip-algo-trading",
    version=read_version(),
    author="Priyansh Patidar",
    author_email="p.priyansh.p@gmail.com",
    description="SIP Algorithmic Trading System for Indian Stock Markets",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ItsMePatidar/sip-algo-trading",
    project_urls={
        "Bug Reports": "https://github.com/ItsMePatidar/sip-algo-trading/issues",
        "Source": "https://github.com/ItsMePatidar/sip-algo-trading",
        "Documentation": "https://github.com/ItsMePatidar/sip-algo-trading/wiki",
    },
    packages=find_packages(exclude=["tests*", "docs*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    
    # FIXED ENTRY POINTS - These should work from any directory
    entry_points={
        "console_scripts": [
            # Method 1: Direct function calls (if functions are in root files)
            "sip-trading=main:main",
            "sip-scheduler=scheduler:run_scheduler", 
            "sip-api=web_api:main",
            "sip-test=test_system:main",
            
            # Method 2: Module-based entry points (alternative)
            # "sip-trading=sip_trading.main:main",
            # "sip-scheduler=sip_trading.scheduler:run_scheduler",
            # "sip-api=sip_trading.web_api:main",
            # "sip-test=sip_trading.test_system:main",
        ],
    },
    
    # This helps with imports
    package_dir={"": "."},
    
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml", "*.cfg", "*.ini"],
    },
    zip_safe=False,
    keywords=[
        "algorithmic trading",
        "SIP",
        "systematic investment plan",
        "indian stock market",
        "NSE",
        "BSE",
        "zerodha",
        "trading bot",
        "investment automation",
        "portfolio management",
    ],
)
"""
Example configuration for trading strategies and data sources.
"""

# Exchange API configurations
EXCHANGES = {
    "deribit": {
        "base_url": "https://www.deribit.com/api/v2",
        "testnet_url": "https://test.deribit.com/api/v2",
        "use_testnet": True,
    },
    "binance": {
        "base_url": "https://eapi.binance.com",
        "use_testnet": False,
    }
}

# Trading parameters
TRADING = {
    "default_asset": "BTC",
    "risk_free_rate": 0.03,  # 3% annual
    "max_leverage": 2.0,
    "rebalance_frequency": "1H",  # Hourly rebalancing
}

# Strategy parameters
STRATEGIES = {
    "volatility_arbitrage": {
        "enabled": True,
        "lookback_window": 30,
        "entry_threshold": 0.20,
        "exit_threshold": 0.05,
    },
    "delta_neutral": {
        "enabled": True,
        "rebalance_threshold": 0.10,
    }
}

# Risk limits
RISK_LIMITS = {
    "max_portfolio_delta": 1000.0,
    "max_portfolio_vega": 5000.0,
    "max_portfolio_gamma": 100.0,
    "max_position_size": 0.05,  # 5% of portfolio
    "max_single_option_notional": 50000.0,
}

# Data collection
DATA_COLLECTION = {
    "update_frequency": "5m",
    "symbols": ["BTC-USD", "ETH-USD"],
    "save_raw": True,
    "save_processed": True,
}

# Backtesting
BACKTESTING = {
    "initial_capital": 100000.0,
    "commission_rate": 0.0003,  # 0.03%
    "slippage_bps": 5,  # 5 basis points
}

# Systematic Crypto Options Trading

*A research framework for cryptocurrency options volatility modeling and systematic trading strategies*

## Overview

This project develops a systematic approach to trading cryptocurrency options, with a focus on volatility modeling, surface construction, and quantitative strategy development. The framework is designed to be modular and research-friendly, enabling rapid experimentation with different models, data sources, and trading strategies.

The cryptocurrency options market presents unique opportunities and challenges compared to traditional equity options. Higher volatility levels, 24/7 trading, fragmented liquidity across exchanges, and evolving market microstructure create a rich environment for quantitative research and systematic trading strategies.

### Project Objectives

1. **Data Infrastructure**: Build robust pipelines for collecting, cleaning, and storing options market data from centralized and decentralized exchanges
2. **Volatility Modeling**: Develop models to construct and analyze implied volatility surfaces across different cryptocurrencies
3. **Strategy Development**: Design and backtest systematic trading strategies including volatility arbitrage, delta-neutral strategies, and market-making
4. **Risk Management**: Implement comprehensive risk models accounting for crypto-specific risks (liquidation, exchange risk, gas fees)

<!-- ### Key Research Questions

- How do crypto implied volatility surfaces differ from traditional equity options?
- What are the risk premia in crypto options markets?
- Can volatility arbitrage strategies be profitably implemented?
- How do market microstructure factors affect option pricing in decentralized markets?
- What are the optimal hedging strategies given high spot volatility and funding costs? -->

## Repository Architecture

The project follows a modular structure designed for research portability and reproducibility:

```
systematic-crypto-options-trading/
├── src/                      # Core library modules
│   ├── data/                 # Data collection and processing
│   ├── logging/              # Centralized logging configuration
│   ├── models/               # Pricing and volatility models
│   ├── strategies/           # Trading strategy implementations
│   ├── risk/                 # Risk management and analytics
│   └── utils/                # Helper functions and utilities
├── notebooks/                # Jupyter notebooks for research
│   ├── exploratory/          # Data exploration and analysis
│   ├── modeling/             # Model development and testing
│   └── backtesting/          # Strategy backtesting
├── tests/                    # Unit and integration tests
├── data/                     # Local data storage (gitignored)
│   ├── raw/                  # Raw market data
│   ├── processed/            # Cleaned and processed data
│   ├── results/              # Backtest results and outputs
│   └── logs/                 # Application logs
├── configs/                  # Configuration files
└── scripts/                  # Utility scripts and automation
```

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/systematic-crypto-options-trading.git
cd systematic-crypto-options-trading

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Install package in development mode
uv pip install -e .
```
## Development Roadmap

- [ ] Phase 1: Data infrastructure and collection pipelines. Frontend dashboard for management.
- [ ] Phase 2: Volatility surface modeling and calibration. Frontend dashboard for data visualization.
- [ ] Phase 3: Strategy development and backtesting framework. Frontend dashboard for strategy visualization.
- [ ] Phase 4: Risk management and portfolio analytics. Frontend dashboard for risk management.
- [ ] Phase 5: Live trading integration. Frontend dashboard for live trading.

## Contributing

This is a research project developed as part of Warwick Quant. Contributions and suggestions are welcome.

## License

TBD


## Acknowledgments

Developed as part of Warwick Quant research initiative.
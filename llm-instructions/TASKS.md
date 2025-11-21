# Systematic Crypto Options Trading - Implementation Tasks

## Project Goal
Build a comprehensive options volatility surface modeling system for Deribit BTC options, enabling real-time volatility analysis, greeks computation, and systematic trading strategy development.

---

## Key Requirements

### Data Requirements
1. **BTC Spot Price** - Real-time spot prices for BTC/USD
2. **BTC Futures/Perpetuals Price** - Front month futures and perpetual swap prices
3. **BTC Options Market Data**
   - Best Bid/Ask prices and quantities
   - Option contract specifications (strike, expiry, type)
   - Implied volatility (IV) from exchange
   - Open interest and volume
   - Greeks (if provided by exchange)
4. **Risk-Free Rate** - Treasury rates or SOFR for pricing models
5. **Market Microstructure Data** - Order book depth, trade flow (optional for Phase 1-2)

### System Requirements
1. **Low Latency** - WebSocket connections for real-time data ingestion (<100ms)
2. **High Availability** - 99.5% uptime target for data collection
3. **Data Integrity** - Validation, deduplication, and error handling
4. **Scalability** - Handle 1000+ option contracts with multiple expiries
5. **Historical Storage** - Minimum 1 year of tick data retention
6. **Query Performance** - Sub-second queries for volatility surface reconstruction

---

## Tech Stack

### Core Infrastructure
- **Python 3.13.5** - Primary programming language
- **AWS EC2** - Cloud compute (t3.medium or t3.large recommended)
- **Docker** - Containerization for reproducibility
- **Git/GitHub** - Version control and CI/CD

### Data Layer
- **Primary Database**: TimescaleDB (PostgreSQL-based, excellent for time-series)
  - Alternative: QuestDB (higher throughput) or ClickHouse (better for analytics)
  - **Recommendation**: Start with TimescaleDB for SQL compatibility and ease of use
- **Redis** - In-memory cache for real-time greeks and surface state
- **S3** - Long-term archival storage for raw data backups

### Data Ingestion
- **WebSocket Libraries**: `websocket-client`, `asyncio`, `aiohttp`
- **CCXT** - Unified exchange API wrapper (fallback for REST endpoints)
- **Apache Kafka** (Optional) - Message queue for production-grade streaming

### Analytics & Modeling
- **NumPy** - Numerical computations
- **Polars** - High-performance dataframe operations (preferred over Pandas)
- **SciPy** - Options pricing (Black-Scholes, numerical methods)
- **QuantLib** (Optional) - Advanced options pricing library
- **Scikit-learn** - Volatility surface interpolation/fitting

### Visualization & Monitoring
- **Grafana** - Real-time dashboards for volatility surfaces and greeks
- **Plotly/Matplotlib** - Static analysis plots in Jupyter notebooks
- **Prometheus** - Metrics collection for system monitoring

### Alerting & Notifications
- **Telegram Bot API** - Trading signals and system alerts
- **Python-telegram-bot** library

### Development Tools
- **Jupyter Lab** - Interactive research environment
- **pytest** - Unit and integration testing
- **black/ruff** - Code formatting and linting
- **mypy** - Static type checking

---

## Phase 1: Data Infrastructure & Collection Pipeline

**Goal**: Establish robust, real-time data pipelines for spot, futures, and options market data from Deribit.

### 1.1 Environment Setup & Project Structure
- [x] Initialize Git repository
- [x] Create virtual environment with `uv`
- [x] Set up project directory structure (`src/`, `data/`, `configs/`, `tests/`)
- [ ] Create `.env` template for API keys and database credentials
- [ ] Set up logging configuration (`src/logging/`)
- [ ] Write project setup documentation in README

### 1.2 Database Design & Deployment
- [ ] **Database Selection**: Finalize choice between TimescaleDB/QuestDB/ClickHouse
  - Evaluate based on: write throughput, query latency, SQL support, operational complexity
- [ ] **Schema Design**:
  - Design `spot_prices` table (timestamp, symbol, price, volume)
  - Design `futures_prices` table (timestamp, symbol, contract_type, price, funding_rate, open_interest)
  - Design `options_quotes` table (timestamp, instrument_name, strike, expiry, option_type, bid, ask, bid_size, ask_size, mark_iv, underlying_price)
  - Design `options_metadata` table (instrument_name, strike, expiry, option_type, settlement_type, tick_size)
  - Add indexes on timestamp, symbol, strike, expiry for fast queries
- [ ] **Database Deployment**:
  - Deploy TimescaleDB on AWS EC2 or AWS RDS for PostgreSQL
  - Enable TimescaleDB extension and create hypertables
  - Set up automated backups and retention policies (e.g., 7-day snapshots, 1-year retention)
  - Configure connection pooling (pgBouncer recommended)
- [ ] **Testing**: Write integration tests to verify table creation and data insertion

### 1.3 Deribit API Integration
- [ ] **API Research**:
  - Read Deribit API documentation (both REST and WebSocket)
  - Identify required endpoints:
    - `/public/get_instruments` - Fetch all BTC options
    - `/public/ticker` - Get spot and futures tickers
    - WebSocket channels: `book.{instrument}.{group}.{depth}`, `ticker.{instrument}.100ms`
- [ ] **Authentication Setup**:
  - Register Deribit account (testnet for development)
  - Generate API keys and store in `.env`
  - Test authentication with REST API
- [ ] **REST Client Development** (`src/data/deribit_rest.py`):
  - Implement `DeribitRestClient` class
  - Methods: `get_instruments()`, `get_ticker()`, `get_order_book()`, `get_trade_history()`
  - Add error handling, rate limiting (10 req/sec limit), and retry logic
- [ ] **WebSocket Client Development** (`src/data/deribit_ws.py`):
  - Implement `DeribitWebSocketClient` class with asyncio
  - Subscription methods: `subscribe_ticker()`, `subscribe_order_book()`
  - Heartbeat handling and automatic reconnection logic
  - Message parsing and validation
- [ ] **Testing**: 
  - Unit tests for REST client with mocked responses
  - Integration test with Deribit testnet WebSocket

### 1.4 Real-Time Data Ingestion Pipeline
- [ ] **Spot Price Ingestion** (`src/data/ingest_spot.py`):
  - Subscribe to BTC spot price via WebSocket
  - Parse incoming messages and extract price, volume, timestamp
  - Batch writes to database (every 1 second or 100 records)
  - Monitor connection health and log errors
- [ ] **Futures Price Ingestion** (`src/data/ingest_futures.py`):
  - Subscribe to BTC-PERPETUAL and front-month futures
  - Extract price, funding rate, open interest
  - Implement batched database writes
- [ ] **Options Data Ingestion** (`src/data/ingest_options.py`):
  - Fetch list of active BTC option instruments (REST API)
  - Filter by expiry (e.g., only next 6 expirations)
  - Subscribe to ticker updates for all active options (WebSocket)
  - Parse bid/ask, mark IV, underlying price
  - Efficient bulk inserts (use PostgreSQL COPY or batch inserts)
- [ ] **Process Management**:
  - Create supervisor script to run all ingestion processes (`scripts/start_ingestion.sh`)
  - Implement graceful shutdown handlers
  - Add systemd service files for auto-restart on EC2

### 1.5 Data Validation & Quality Checks
- [ ] **Validation Rules**:
  - Check for stale data (timestamp freshness)
  - Validate bid <= ask for options
  - Detect and flag outliers (e.g., IV > 300% or price spikes)
  - Ensure referential integrity (option quotes must have valid spot/futures prices)
- [ ] **Data Quality Dashboard**:
  - Grafana dashboard showing: ingestion rate, data gaps, error counts
  - Alerts for missing data or connection failures (integrate with Telegram bot)
- [ ] **Error Logging**:
  - Centralized logging to `data/logs/` and CloudWatch
  - Structured logs with severity levels (INFO, WARNING, ERROR)

### 1.6 Historical Data Backfill (Optional)
- [ ] **Backfill Strategy**:
  - Identify required historical period (e.g., last 3 months)
  - Use Deribit REST API `/public/get_tradingview_chart_data` or third-party providers
  - Download and process historical spot, futures, options data
  - Load into database with proper timestamping
- [ ] **Validation**: Compare backfilled data with known historical events (e.g., large moves)

### 1.7 Phase 1 Testing & Validation
- [ ] **End-to-End Test**:
  - Run ingestion pipeline for 24 hours
  - Verify data completeness (no gaps > 5 seconds)
  - Query database to reconstruct option chain at specific timestamp
- [ ] **Performance Benchmarking**:
  - Measure database write throughput (target: 1000 inserts/sec)
  - Measure query latency for volatility surface reconstruction (target: <1 sec)
- [ ] **Documentation**:
  - Document database schema with ER diagrams
  - Write runbook for starting/stopping ingestion pipeline
  - Create troubleshooting guide for common issues

---

## Phase 2: Volatility Surface Modeling & Calibration

**Goal**: Develop pricing models to compute greeks, construct implied volatility surfaces, and enable term structure analysis.

### 2.1 Options Pricing Framework
- [ ] **Pricing Model Selection**:
  - Implement Black-Scholes-Merton (BSM) model as baseline
  - Plan for future: Black-76 (for futures options), Heston, SABR
- [ ] **Greeks Computation** (`src/models/greeks.py`):
  - Implement analytical greeks for European options:
    - First-order: Delta, Vega, Theta, Rho, Gamma
    - Second-order: Vanna, Volga, Charm, Vomma
  - Vectorized implementation using NumPy for performance
  - Input validation (spot > 0, strike > 0, time to expiry > 0, IV > 0)
- [ ] **Implied Volatility Solver** (`src/models/implied_vol.py`):
  - Implement Newton-Raphson method for IV extraction from market prices
  - Handle edge cases: deep ITM/OTM, near expiry, zero bid/ask
  - Use Brent's method as fallback
  - Benchmark against exchange-provided mark IV
- [ ] **Testing**:
  - Unit tests with known BSM solutions
  - Validate greeks against QuantLib or online calculators
  - Test IV solver convergence on real market data

### 2.2 Forward Curve & Discounting
- [ ] **Forward Price Calculation** (`src/models/forward_curve.py`):
  - Extract forward prices from futures market (BTC-PERPETUAL + dated futures)
  - Implement put-call parity checks to infer forwards from options
  - Handle basis risk between spot and futures
- [ ] **Risk-Free Rate Handling**:
  - Fetch US Treasury rates from FRED API or manual updates
  - Interpolate yield curve for option expiries
  - Alternative: Use 0% rate (common in crypto due to no true risk-free rate)
  - Store rates in database (`interest_rates` table)

### 2.3 Volatility Surface Construction
- [ ] **Surface Representation** (`src/models/vol_surface.py`):
  - Choose parameterization: strike vs. moneyness (K/S or delta)
  - Grid structure: maturity (days to expiry) x strike (or delta)
  - Store surface as 2D array with metadata (timestamp, underlying price)
- [ ] **Arbitrage-Free Constraints**:
  - Check for call/put parity violations
  - Detect calendar arbitrage (implied forward drifts)
  - Flag butterfly arbitrage (convexity violations)
- [ ] **Interpolation Methods**:
  - Implement cubic spline interpolation along strike dimension
  - Implement linear interpolation along time dimension
  - Alternative: SVI (Stochastic Volatility Inspired) parameterization for smoothness
  - Compare interpolation methods on historical data
- [ ] **Extrapolation Handling**:
  - Flat extrapolation beyond observed strikes
  - Research: use tail models (e.g., SABR, power law) for OTM wings

### 2.4 Surface Calibration & Fitting
- [ ] **Data Preparation**:
  - Filter options by liquidity (e.g., min bid/ask size, max spread)
  - Remove stale quotes (last update > 10 seconds)
  - Group by expiry and compute moneyness metrics
- [ ] **Calibration Algorithm** (`src/models/calibrate.py`):
  - Fit SVI or SABR parameters to market IV smile per expiry
  - Use least-squares optimization (scipy.optimize.minimize)
  - Regularization to prevent overfitting (e.g., penalize wing curvature)
  - Multi-expiry calibration with term structure constraints
- [ ] **Validation**:
  - Out-of-sample testing: calibrate on morning data, test on afternoon data
  - Residual analysis: plot fitted IV vs. market IV
  - Stability tests: track parameter evolution over time

### 2.5 Greeks Surface Generation
- [ ] **Greeks Calculation Pipeline** (`src/models/surface_greeks.py`):
  - For each option in database: compute greeks using fitted IV surface
  - Store greeks in database (`options_greeks` table: timestamp, instrument, delta, gamma, vega, theta, rho)
  - Redis caching for real-time greeks lookup
- [ ] **Aggregated Greeks**:
  - Compute portfolio-level greeks (net delta, net gamma, net vega)
  - Term structure of greeks by expiry
- [ ] **Performance Optimization**:
  - Vectorize greeks computation across all strikes/expiries
  - Use Numba JIT compilation for critical loops
  - Target: compute full greeks surface (<5 seconds)

### 2.6 Term Structure Analysis
- [ ] **Volatility Term Structure** (`src/models/term_structure.py`):
  - Extract ATM IV for each expiry (interpolate to 50 delta or ATM strike)
  - Plot term structure: ATM IV vs. days to expiry
  - Compute volatility slope (near-term vs. far-term)
  - Historical tracking: store daily term structure snapshots
- [ ] **Skew Analysis**:
  - Compute 25-delta risk reversal (25D call IV - 25D put IV)
  - Compute 25-delta butterfly (average 25D IV - ATM IV)
  - Track skew evolution across market regimes
- [ ] **Regime Detection**:
  - Detect volatility regimes: low-vol, high-vol, crash scenarios
  - Use rolling statistics (30-day ATM IV percentile)

### 2.7 Grafana Visualization Dashboard
- [ ] **Dashboard Design**:
  - Panel 1: Real-time volatility surface (3D heatmap or contour plot)
  - Panel 2: Volatility term structure (line chart)
  - Panel 3: Volatility smile by expiry (multi-line chart)
  - Panel 4: Time series of ATM IV, skew, and convexity
  - Panel 5: Greeks heatmap (delta, gamma, vega by strike/expiry)
- [ ] **Grafana Setup**:
  - Install Grafana on EC2 or use Grafana Cloud
  - Configure TimescaleDB as data source
  - Create SQL queries for each visualization
  - Implement auto-refresh (every 10 seconds)
- [ ] **Alerts Configuration**:
  - Alert 1: ATM IV spike > 20% from 7-day average
  - Alert 2: Skew inversion (negative risk reversal)
  - Alert 3: Data staleness (no updates in 60 seconds)
  - Send alerts to Telegram bot

### 2.8 Telegram Bot for Monitoring
- [ ] **Bot Setup** (`src/utils/telegram_bot.py`):
  - Register bot with BotFather and get API token
  - Implement command handlers:
    - `/surface` - Send current volatility surface plot
    - `/greeks {instrument}` - Get greeks for specific option
    - `/atm` - Get ATM IV for all expiries
    - `/alert {condition}` - Configure custom alerts
- [ ] **Scheduled Reports**:
  - Daily summary: ATM IV levels, skew metrics, largest movers
  - Alert forwarding from Grafana to Telegram

### 2.9 Phase 2 Testing & Documentation
- [ ] **Backtesting Surface Model**:
  - Reconstruct volatility surfaces from historical data
  - Validate pricing accuracy: compare model prices vs. market mid
  - Measure pricing errors (RMSE, MAE) across strikes and expiries
- [ ] **Research Notebook** (`notebooks/modeling/vol_surface_analysis.ipynb`):
  - Explore volatility surface dynamics during major events (e.g., ETF approval, halvings)
  - Compare crypto IV surfaces to equity options (SPY, QQQ)
  - Document findings and insights
- [ ] **Code Documentation**:
  - Docstrings for all functions (NumPy style)
  - Type hints for function signatures
  - Update README with Phase 2 components
- [ ] **Performance Report**:
  - End-to-end latency: market data → database → greeks → Grafana
  - Database query performance for surface reconstruction
  - System resource utilization (CPU, memory, disk I/O)

---

## Recommendations

### Technical Recommendations

1. **Database Choice - TimescaleDB** ✅
   - **Why**: Best balance of SQL familiarity, time-series optimization, and community support
   - Excellent compression (up to 90% with continuous aggregates)
   - Native PostgreSQL compatibility enables rich querying
   - Consider QuestDB only if write throughput exceeds 100k inserts/sec

2. **Use Polars over Pandas** ✅
   - 10-100x faster for large datasets
   - Better memory efficiency with lazy evaluation
   - Already in requirements.txt - prioritize for all data processing

3. **Implement Redis Caching**
   - Cache latest greeks and volatility surface in Redis
   - Target: <10ms read latency for real-time trading signals
   - Reduces database load for high-frequency queries

4. **Asynchronous WebSocket Handling**
   - Use `asyncio` and `aiohttp` for concurrent WebSocket connections
   - Single Python process can handle 100+ concurrent subscriptions
   - More efficient than multi-threading for I/O-bound tasks

5. **Docker Containerization**
   - Create Dockerfile for reproducible deployment
   - Docker Compose for local development (database + Grafana + app)
   - Simplifies EC2 deployment and scaling

6. **Version Control for Schemas**
   - Use Alembic or Flyway for database migrations
   - Track schema changes in Git alongside code
   - Enables rollback and testing of schema updates

### Research & Modeling Recommendations

1. **Start with Black-Scholes, Iterate to Advanced Models**
   - BSM is sufficient for Phase 1-2 validation
   - Phase 3: Implement SABR for better smile fitting
   - Phase 4: Explore stochastic volatility models (Heston, Bates)

2. **Forward Price from Futures, Not Spot**
   - BTC spot-futures basis can be significant (±5%)
   - Use BTC-PERPETUAL or front-month futures as underlying for option pricing
   - Reduces model risk in forward rate assumptions

3. **Liquidity Filtering is Critical**
   - Wide bid-ask spreads (>5% of mid) contaminate IV surface
   - Filter by min volume (e.g., 1 BTC notional) and max spread
   - Separate analysis for liquid vs. illiquid options

4. **Monitor for Crypto-Specific Anomalies**
   - Weekend/holiday effects (24/7 trading vs. 5-day decay assumptions)
   - Funding rate shocks impact perpetual-based forwards
   - Exchange downtime and liquidation cascades

5. **Expiry Cadence**
   - Deribit has weekly and monthly expiries
   - Focus on monthlies for term structure (more liquid)
   - Use weeklies for short-term trading signals

### Operational Recommendations

1. **Start with Deribit Testnet**
   - Testnet has same API structure, no financial risk
   - Test end-to-end pipeline before mainnet
   - Transition to mainnet only after 1 week stable operation

2. **Incremental Rollout**
   - Phase 1A: Spot + Futures only (simpler)
   - Phase 1B: Add options for single expiry (next monthly)
   - Phase 1C: Scale to all expiries
   - Reduces debugging complexity

3. **Monitoring Before Modeling**
   - Establish data quality metrics before building models
   - 80% of failure modes are data issues, not model issues
   - Grafana dashboard for data pipeline health is highest priority

4. **Cost Optimization**
   - EC2 t3.medium ($30/month) sufficient for Phase 1-2
   - TimescaleDB compression reduces storage costs by 10x
   - S3 Glacier for archival data (95% cheaper than EBS)

5. **Telegram Bot as Primary Interface**
   - Faster than SSH-ing to EC2 for quick checks
   - Mobile-first monitoring enables rapid response
   - Build comprehensive command set early

### Documentation & Workflow Recommendations

1. **Jupyter Notebooks for Experimentation**
   - `notebooks/exploratory/` for ad-hoc analysis
   - `notebooks/modeling/` for surface calibration experiments
   - Export finalized code to `src/` modules

2. **Test-Driven Development for Pricing**
   - Options pricing has known analytical solutions
   - Write unit tests first, then implementations
   - Prevents regressions when optimizing performance

3. **Configuration Management**
   - Use YAML configs for: database connection, Deribit API keys, model parameters
   - Separate `configs/dev.yaml`, `configs/prod.yaml`
   - Never hardcode configuration in source files

4. **Git Workflow**
   - Feature branches for each Phase 1/2 subtask
   - Pull requests with self-review before merge
   - Tag releases: `v1.0.0-phase1`, `v2.0.0-phase2`

5. **Incremental Documentation**
   - Update README after each major milestone
   - Maintain `docs/troubleshooting.md` as issues arise
   - Screenshot Grafana dashboards for documentation

---

## Success Criteria

### Phase 1 Completion Criteria
- ✅ 24/7 data ingestion with <1% downtime
- ✅ Real-time spot, futures, and options data in database
- ✅ Query latency <1 second for full option chain reconstruction
- ✅ Grafana dashboard showing ingestion metrics
- ✅ Automated backups and monitoring alerts

### Phase 2 Completion Criteria
- ✅ Volatility surface reconstructed in real-time (<5 second lag)
- ✅ Greeks computed for all liquid options
- ✅ Grafana dashboard with surface visualization and term structure
- ✅ Pricing error <5% vs. market mid for ATM options
- ✅ Telegram bot operational with core commands
- ✅ Documented codebase with >80% test coverage for pricing modules
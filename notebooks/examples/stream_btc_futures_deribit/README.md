# Stream BTC Futures with Expiries - Deribit

Real-time streaming of Bitcoin futures contracts with expiration dates from Deribit exchange. This example demonstrates comprehensive data collection, monitoring, and storage for quantitative research.

## Overview

This script streams orderbook data for **all BTC futures with expiry dates** (excludes perpetuals) from Deribit via WebSocket using CCXT Pro. It provides:

- ✅ **Auto-discovery** of all BTC futures with expiries
- ✅ **Real-time streaming** via WebSocket (low latency)
- ✅ **Price monitoring** with change detection
- ✅ **Spread analytics** and update rate tracking
- ✅ **Multi-format storage** (JSONL, Parquet)
- ✅ **Comprehensive logging** with colored console output
- ✅ **Graceful error handling** with auto-reconnection

## Features

### Market Discovery
- Automatically discovers all BTC futures contracts with expiration dates
- Filters by expiry month (e.g., DEC24, MAR25, JUN25)
- Excludes perpetual contracts (focuses on dated futures)

### Real-Time Monitoring
- Tracks price movements with percentage change calculations
- Logs significant price moves (>= 0.1%)
- Calculates bid-ask spreads and spread statistics
- Monitors update rates per contract and overall
- Tracks min/max prices during session

### Data Storage
- **JSONL Format**: Append-only, easy to process line-by-line
- **Parquet Format**: Columnar storage for efficient analytics
- Configurable storage (enable/disable, choose format)
- Automatic file organization by symbol and date

### Logging
- Colored console output for easy monitoring
- Detailed log files with timestamps
- Per-contract statistics and summaries
- Session summary with comprehensive metrics

## Installation

Ensure you have the virtual environment activated and dependencies installed:

```bash
# From project root
source .venv/bin/activate

# Verify CCXT Pro is installed
python -c "import ccxt.pro; print('✅ CCXT Pro installed')"
```

If CCXT Pro is not installed:
```bash
uv pip install ccxt[pro]
```

## Usage

### Basic Usage

**Stream all BTC futures for 60 seconds (no storage):**
```bash
python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py
```

**Stream with data storage enabled:**
```bash
python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --store
```

### Advanced Usage

**Stream for 5 minutes with storage:**
```bash
python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --duration 300 --store
```

**Filter by specific expiry months:**
```bash
python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --expiries DEC24 MAR25 --store
```

**Use JSONL format only:**
```bash
python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --store --format jsonl
```

**Long-running data collection (1 hour):**
```bash
python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --duration 3600 --store --format both
```

**Stream only Q1 2025 contracts:**
```bash
python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --expiries JAN25 FEB25 MAR25 --store
```

### Command-Line Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--duration` | int | 60 | Duration to stream in seconds |
| `--store` | flag | False | Enable data storage to disk |
| `--format` | choice | both | Storage format: `jsonl`, `parquet`, or `both` |
| `--expiries` | list | None | Filter by expiry months (e.g., `DEC24 MAR25`) |

## Output

### Console Output

Real-time streaming updates with colored output:

```
🚀 BTC FUTURES STREAMING - DERIBIT
======================================================================
⏱️  Duration: 300 seconds (5.0 minutes)
💾 Data storage: Enabled
📁 Storage format: both
----------------------------------------------------------------------
🔍 Discovering BTC futures contracts...
✅ Found 8 BTC futures with expiries
   - BTC-27DEC24
   - BTC-31JAN25
   - BTC-28FEB25
   - BTC-28MAR25
   - BTC-27JUN25
   - BTC-26SEP25
   - BTC-26DEC25
   - BTC-27MAR26
📡 Subscribing to 8 futures contracts...
⏱️  Streaming started... (Press Ctrl+C to stop early)
----------------------------------------------------------------------
🎯 Started streaming BTC-27DEC24
💰 BTC-27DEC24: Initial price $95,432.50 | Spread: $0.50
🎯 Started streaming BTC-31JAN25
💰 BTC-31JAN25: Initial price $96,120.00 | Spread: $1.00
📈 BTC-27DEC24: $95,478.00 (+0.15%) | Spread: $0.50
📊 BTC-27DEC24: 100 updates (~2.1/sec) | Avg spread: $0.52
...
```

### Summary Statistics

After streaming completes, detailed statistics are displayed:

```
======================================================================
📈 BTC FUTURES STREAMING SESSION SUMMARY
======================================================================
⏱️  Duration: 300.2 seconds (5.0 minutes)
🎯 Contracts tracked: 8
📡 Total updates: 2,431
📊 Avg update rate: 8.1 updates/sec

Per-Contract Statistics:
----------------------------------------------------------------------
  BTC-27DEC24:
    Updates: 523 (~1.7/sec)
    Last price: $95,512.50
    Price range: $95,398.00 - $95,612.00 ($214.00)
    Avg spread: $0.54
  
  BTC-31JAN25:
    Updates: 312 (~1.0/sec)
    Last price: $96,234.00
    Price range: $96,089.00 - $96,345.00 ($256.00)
    Avg spread: $1.12
  ...
======================================================================

📦 DATA STORAGE STATISTICS
  Total snapshots recorded: 2,431
  JSONL files: 8
  Parquet files: 0

📄 JSONL files stored in: examples/stream_btc_futures_deribit/data/orderbooks/jsonl
📝 Session log: examples/stream_btc_futures_deribit/logs/btc_futures_20241116_143022.log
======================================================================
```

### Data Files

Stored data is organized by format:

**JSONL files** (`data/orderbooks/jsonl/`):
- One file per symbol per day: `BTC-27DEC24_20241116.jsonl`
- Append-only format (can stream continuously)
- Each line is a complete JSON object

**Parquet files** (`data/orderbooks/parquet/`):
- Efficient columnar storage for analytics
- Created when using `--format parquet` or `--format both`
- Optimized for reading with Polars/Pandas

**Log files** (`logs/`):
- Timestamped log files: `btc_futures_20241116_143022.log`
- Complete session history with all events

## Data Format

### JSONL Entry Structure

Each line in JSONL files contains:

```json
{
  "symbol": "BTC-27DEC24",
  "timestamp": "2024-11-16T14:30:45.123456",
  "best_bid": 95512.0,
  "best_ask": 95512.5,
  "mid_price": 95512.25,
  "spread": 0.5,
  "bid_depth": 10,
  "ask_depth": 10,
  "exchange": "deribit"
}
```

### Loading Data for Analysis

**Using Polars (recommended):**
```python
import polars as pl

# Read JSONL data
df = pl.read_ndjson("data/orderbooks/jsonl/BTC-27DEC24_20241116.jsonl")

# Filter and analyze
df_filtered = df.filter(pl.col("spread") < 1.0)
print(df_filtered.select(["timestamp", "mid_price", "spread"]))
```

**Using Pandas:**
```python
import pandas as pd

# Read JSONL
df = pd.read_json("data/orderbooks/jsonl/BTC-27DEC24_20241116.jsonl", lines=True)

# Convert timestamp
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

# Analyze spreads
print(df['spread'].describe())
```

## Use Cases

### Research Applications

1. **Volatility Surface Construction**
   - Collect data across multiple expiries
   - Calculate implied volatility term structure
   - Build volatility surfaces

2. **Basis Trading**
   - Monitor spot-futures basis
   - Track term structure evolution
   - Identify arbitrage opportunities

3. **Liquidity Analysis**
   - Analyze spread dynamics across expiries
   - Measure market depth
   - Study liquidity patterns

4. **Market Microstructure**
   - Study orderbook dynamics
   - Analyze price discovery
   - Measure market impact

### Example Analysis Workflow

```bash
# 1. Collect data for 30 minutes
python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py \
  --duration 1800 --store --format both

# 2. Load and analyze in Python
python -c "
import polars as pl
df = pl.read_ndjson('data/orderbooks/jsonl/BTC-27DEC24_*.jsonl')
print(f'Total records: {len(df)}')
print(f'Avg spread: ${df[\"spread\"].mean():.2f}')
print(f'Price range: ${df[\"mid_price\"].min():.2f} - ${df[\"mid_price\"].max():.2f}')
"
```

## Architecture

### Component Overview

```
stream_btc_futures_deribit.py
├── BTCFuturesMonitor          # Monitoring and statistics
│   ├── on_orderbook_update()  # Process each update
│   ├── on_error()             # Handle errors
│   └── print_summary()        # Display statistics
│
├── get_btc_futures_with_expiry()  # Market discovery
│
└── stream_btc_futures()       # Main streaming loop
    ├── CCXTProCollector       # WebSocket streaming
    ├── OrderbookDataStore     # Multi-format storage
    └── StreamingDataRecorder  # Data persistence
```

### Data Flow

```
Deribit Exchange (WebSocket)
    ↓
CCXTProCollector (ccxt.pro)
    ↓
OrderbookSnapshot (dataclass)
    ↓
┌─────────────────┬──────────────────┐
│ BTCFuturesMonitor │ StreamingDataRecorder │
│ (monitoring/logs) │   (data storage)      │
└─────────────────┴──────────────────┘
    ↓                    ↓
Console Output      data/orderbooks/
logs/                ├── jsonl/
                     └── parquet/
```

## Technical Details

### WebSocket Streaming
- Uses CCXT Pro's `watch_order_book()` for low-latency updates
- Auto-reconnection on connection drops
- Configurable reconnect attempts (default: 10)
- Graceful degradation on errors

### Performance
- Typical update rates: 1-5 updates/sec per contract
- Memory efficient (bounded history per symbol)
- Non-blocking async architecture
- Minimal CPU overhead

### Error Handling
- Automatic reconnection with exponential backoff
- Per-symbol error isolation (one failure doesn't affect others)
- Comprehensive error logging
- Graceful shutdown on Ctrl+C

## Troubleshooting

### Common Issues

**"Module 'ccxt.pro' not found"**
```bash
uv pip install ccxt[pro]
```

**"No BTC futures found matching criteria"**
- Check your expiry filters (`--expiries`)
- Verify Deribit market availability
- Check network connectivity

**High spreads or low update rates**
- Check market hours (crypto trades 24/7 but some contracts have lower activity)
- Verify network latency
- Consider market liquidity

### Debug Mode

Enable debug logging for troubleshooting:
```python
# In stream_btc_futures_deribit.py, change:
setup_logging(level="DEBUG", ...)
```

## Related Examples

- **`stream_perpetuals_deribit/`** - Stream perpetual futures (BTC/ETH-PERPETUAL)
- See `src/data/ccxt_collector/README.md` for CCXT collector documentation

## Next Steps

1. **Collect historical data** - Run for extended periods to build datasets
2. **Analyze term structure** - Compare prices across different expiries
3. **Build models** - Use data for volatility surface fitting
4. **Backtest strategies** - Test trading strategies on collected data

## License

Part of systematic-crypto-options-trading framework. See project root for license.

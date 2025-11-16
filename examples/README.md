# Examples

This directory contains example scripts demonstrating how to use the systematic crypto options trading framework.

Each example has its own folder with dedicated logs and data directories.

## Directory Structure

```
examples/
├── README.md                          # This file
├── stream_perpetuals_deribit/         # BTC/ETH perpetuals streaming
│   ├── stream_futures_deribit.py      # Main script
│   ├── logs/                          # Unique log file for each run
│   └── data/                          # Data storage (when --store is used)
│       └── orderbooks/
│           ├── jsonl/                 # JSONL format
│           └── parquet/               # Parquet format
├── stream_btc_futures_deribit/        # BTC futures with expiries streaming
│   ├── stream_btc_futures_deribit.py  # Main script
│   ├── README.md                      # Detailed documentation
│   ├── logs/                          # Unique log file for each run
│   └── data/                          # Data storage (when --store is used)
│       └── orderbooks/
│           ├── jsonl/                 # JSONL format
│           └── parquet/               # Parquet format
└── [future examples...]
```

## Examples

### 1. Stream Perpetuals Data - Deribit

**Location:** `stream_perpetuals_deribit/stream_futures_deribit.py`

Stream real-time orderbook data for BTC and ETH perpetual futures from Deribit exchange using CCXT Pro.

**Features:**
- Real-time WebSocket streaming of orderbook data
- Automatic logging to file and console (unique log per session)
- Optional data storage in JSONL and Parquet formats
- Price change monitoring and alerts (≥0.1%)
- Summary statistics
- Automatic reconnection on errors

**Requirements:**
```bash
uv pip install ccxt[pro]
```

**Usage:**

Activate virtual environment first:
```bash
source .venv/bin/activate
```

Basic usage (stream for 60 seconds, no data storage):
```bash
python examples/stream_perpetuals_deribit/stream_futures_deribit.py
```

Stream for 5 minutes with data storage:
```bash
python examples/stream_perpetuals_deribit/stream_futures_deribit.py --duration 300 --store
```

Stream specific futures contracts:
```bash
python examples/stream_perpetuals_deribit/stream_futures_deribit.py --symbols BTC-PERPETUAL ETH-PERPETUAL
```

**Command Line Options:**

- `--symbols`: List of futures symbols to stream (default: BTC-PERPETUAL ETH-PERPETUAL)
- `--duration`: Duration to stream in seconds (default: 60)
- `--store`: Enable data storage to disk (default: disabled)
- `--format`: Storage format - `jsonl`, `parquet`, or `both` (default: both)

---

### 2. Stream BTC Futures with Expiries - Deribit

**Location:** `stream_btc_futures_deribit/stream_btc_futures_deribit.py`

Stream real-time orderbook data for **all BTC futures with expiration dates** (excludes perpetuals) from Deribit. Comprehensive monitoring, analytics, and multi-format storage.

**Features:**
- Auto-discovers all BTC futures with expiry dates
- Filter by specific expiry months (e.g., DEC24, MAR25)
- Real-time price monitoring with change detection
- Spread analytics and update rate tracking
- Multi-format storage (JSONL, Parquet)
- Comprehensive logging and session summaries
- Graceful error handling with auto-reconnection

**Quick Start:**

```bash
# Activate environment
source .venv/bin/activate

# Stream all BTC futures for 60 seconds (no storage)
python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py

# Stream for 5 minutes with storage enabled
python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --duration 300 --store

# Filter specific expiry months
python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --expiries DEC24 MAR25 --store

# Long-running data collection (1 hour)
python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --duration 3600 --store
```

**Command Line Options:**

- `--duration`: Duration to stream in seconds (default: 60)
- `--store`: Enable data storage to disk (default: disabled)
- `--format`: Storage format - `jsonl`, `parquet`, or `both` (default: both)
- `--expiries`: Filter by expiry months (e.g., `DEC24 MAR25 JUN25`)

**Output:**

Each run creates:
- Unique log file: `logs/btc_futures_YYYYMMDD_HHMMSS.log`
- Data files (when `--store` is enabled):
  - JSONL: `data/orderbooks/jsonl/SYMBOL_YYYYMMDD.jsonl`
  - Parquet: `data/orderbooks/parquet/SYMBOL_YYYYMMDD.parquet`

**Example Output:**

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
⏱️  Streaming started...
----------------------------------------------------------------------
🎯 Started streaming BTC-27DEC24
💰 BTC-27DEC24: Initial price $95,432.50 | Spread: $0.50
📈 BTC-27DEC24: $95,478.00 (+0.15%) | Spread: $0.50
...

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
  ...
======================================================================
```

**Use Cases:**
- Volatility surface construction across expiries
- Term structure analysis
- Basis trading research
- Liquidity analysis
- Market microstructure studies

See `stream_btc_futures_deribit/README.md` for detailed documentation.

---

### 1. Stream Futures Data - Deribit (DEPRECATED - Use examples above)

**Location:** `stream_futures_deribit/stream_futures_deribit.py`

Stream real-time orderbook data for BTC and ETH futures from Deribit exchange using CCXT Pro.

**Features:**
- Real-time WebSocket streaming of orderbook data
- Automatic logging to file and console (unique log per session)
- Optional data storage in JSONL and CSV formats
- Price change monitoring and alerts (≥0.1%)
- Summary statistics
- Automatic reconnection on errors

**Requirements:**
```bash
pip install ccxt[pro]
```

**Usage:**

Activate virtual environment first:
```bash
source .venv/bin/activate
```

Basic usage (stream for 60 seconds, no data storage):
```bash
python examples/stream_futures_deribit/stream_futures_deribit.py
```

Stream for 5 minutes with data storage:
```bash
python examples/stream_futures_deribit/stream_futures_deribit.py --duration 300 --store
```

Stream specific futures contracts:
```bash
python examples/stream_futures_deribit/stream_futures_deribit.py --symbols BTC-PERPETUAL ETH-PERPETUAL BTC-27DEC24
```

Store data in CSV format only:
```bash
python examples/stream_futures_deribit/stream_futures_deribit.py --store --format csv
```

Store data in JSONL format only:
```bash
python examples/stream_futures_deribit/stream_futures_deribit.py --store --format jsonl
```

Store data in both formats (default when --store is used):
```bash
python examples/stream_futures_deribit/stream_futures_deribit.py --store --format both
```

**Command Line Options:**

- `--symbols`: List of futures symbols to stream (default: BTC-PERPETUAL ETH-PERPETUAL)
- `--duration`: Duration to stream in seconds (default: 60)
- `--store`: Enable data storage to disk (default: disabled)
- `--format`: Storage format - `jsonl`, `csv`, or `both` (default: both)

**Output:**

Each run creates:
- A unique log file: `logs/stream_YYYYMMDD_HHMMSS.log`
- Data files (only when `--store` is used):
  - JSONL: `data/orderbooks/jsonl/SYMBOL_YYYYMMDD.jsonl`
  - CSV: `data/orderbooks/csv/SYMBOL_YYYYMMDD.csv`

**Data Format:**

Each orderbook snapshot includes:
- Timestamp (ISO format)
- Symbol
- Best bid/ask prices
- Mid price
- Spread
- Orderbook depth (up to 10 levels when using CSV with depth)

**Monitoring:**

The script provides real-time monitoring:
- Price updates when changes ≥ 0.1%
- Periodic statistics (every 50 updates)
- Session summary on completion
- Error logging and automatic reconnection attempts

**Example Output:**
```
🚀 Starting Deribit Futures Data Stream
Symbols: BTC-PERPETUAL, ETH-PERPETUAL
Duration: 10 seconds
Data storage: Enabled
Storage format: both
------------------------------------------------------------
📁 Data will be stored in: .../examples/stream_futures_deribit/data
📡 Subscribing to 2 futures symbols...
🎯 Started receiving data for BTC-PERPETUAL
💰 BTC-PERPETUAL: Initial price $94370.25 | Spread: $0.50
🎯 Started receiving data for ETH-PERPETUAL
💰 ETH-PERPETUAL: Initial price $3102.97 | Spread: $0.05
🛑 Stopping data stream...
============================================================
📈 STREAMING SESSION SUMMARY
============================================================
Duration: 10.8 seconds
Symbols tracked: 2
  BTC-PERPETUAL: 31 updates (~2.9/sec) | Last price: $94370.25
  ETH-PERPETUAL: 31 updates (~2.9/sec) | Last price: $3102.47
============================================================

📦 STORAGE STATISTICS
  Total snapshots recorded: 62
  JSONL files: 2
  CSV files: 2

📄 Session log saved to: .../logs/stream_20251116_191357.log
```

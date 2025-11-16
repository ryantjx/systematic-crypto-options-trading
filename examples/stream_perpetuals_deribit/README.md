# Stream Futures Data - Deribit

Real-time streaming of BTC and ETH futures orderbook data from Deribit using CCXT Pro.

## Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Basic streaming (60 seconds, no data storage)
python stream_futures_deribit.py

# Stream with data storage
python stream_futures_deribit.py --store

# Stream for 5 minutes with data storage
python stream_futures_deribit.py --duration 300 --store
```

## Features

✅ Real-time WebSocket streaming via CCXT Pro  
✅ Unique log file per session  
✅ Optional data storage (JSONL/CSV)  
✅ Price monitoring with alerts (≥0.1% changes)  
✅ Session statistics and summaries  
✅ Automatic error handling and reconnection  

## Usage

```bash
python stream_futures_deribit.py [OPTIONS]
```

### Options

- `--symbols SYMBOL [SYMBOL ...]` - Futures symbols to stream (default: BTC-PERPETUAL ETH-PERPETUAL)
- `--duration SECONDS` - Duration to stream in seconds (default: 60)
- `--store` - Enable data storage to disk (default: disabled)
- `--format {jsonl,csv,both}` - Storage format when --store is used (default: both)

### Examples

```bash
# Stream default symbols for 60 seconds (no storage)
python stream_futures_deribit.py

# Stream for 10 minutes with data storage in both formats
python stream_futures_deribit.py --duration 600 --store

# Stream specific contracts
python stream_futures_deribit.py --symbols BTC-PERPETUAL ETH-PERPETUAL BTC-27DEC24

# Store only CSV format
python stream_futures_deribit.py --store --format csv

# Store only JSONL format  
python stream_futures_deribit.py --store --format jsonl
```

## Output Structure

```
stream_futures_deribit/
├── stream_futures_deribit.py    # Main script
├── logs/                        # Unique log per session
│   └── stream_YYYYMMDD_HHMMSS.log
└── data/                        # Created when --store is used
    └── orderbooks/
        ├── jsonl/
        │   ├── BTC-PERPETUAL_YYYYMMDD.jsonl
        │   └── ETH-PERPETUAL_YYYYMMDD.jsonl
        └── csv/
            ├── BTC-PERPETUAL_YYYYMMDD.csv
            └── ETH-PERPETUAL_YYYYMMDD.csv
```

## Data Format

### JSONL Format
Each line is a JSON object with:
```json
{
  "symbol": "BTC-PERPETUAL",
  "timestamp": "2025-11-16T19:13:58.123456",
  "best_bid": 94370.25,
  "best_ask": 94370.75,
  "mid_price": 94370.50,
  "spread": 0.50,
  "bid_depth": 10,
  "ask_depth": 10,
  "exchange": "deribit"
}
```

### CSV Format
Columns include:
- `timestamp` - ISO format timestamp
- `symbol` - Futures symbol
- `exchange` - Exchange name
- `best_bid` - Best bid price
- `best_ask` - Best ask price
- `mid_price` - Mid price
- `spread` - Bid-ask spread
- `bid_depth` - Number of bid levels
- `ask_depth` - Number of ask levels
- `bid_price_0` to `bid_price_9` - Top 10 bid prices
- `bid_size_0` to `bid_size_9` - Top 10 bid sizes
- `ask_price_0` to `ask_price_9` - Top 10 ask prices
- `ask_size_0` to `ask_size_9` - Top 10 ask sizes

## Sample Output

```
🚀 Starting Deribit Futures Data Stream
Symbols: BTC-PERPETUAL, ETH-PERPETUAL
Duration: 10 seconds
Data storage: Enabled
Storage format: both
------------------------------------------------------------
📁 Data will be stored in: .../stream_futures_deribit/data
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

## Requirements

- Python 3.8+
- ccxt[pro] - `pip install ccxt[pro]`
- Dependencies from project requirements.txt

## Notes

- **Data storage is opt-in** - Use `--store` flag to save data
- Each run creates a **unique log file** with timestamp
- Data files are **appended** if they already exist for the same date
- The script handles connection errors and automatically reconnects
- Press Ctrl+C to stop streaming early

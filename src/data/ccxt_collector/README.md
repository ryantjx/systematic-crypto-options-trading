# CCXT Pro WebSocket Data Collector

**Comprehensive Guide & Reference**

Real-time streaming data collector for cryptocurrency futures and options using CCXT Pro's WebSocket functionality.

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Architecture](#architecture)
5. [Core Features](#core-features)
6. [Configuration Reference](#configuration-reference)
7. [API Reference](#api-reference)
8. [Data Structures](#data-structures)
9. [Storage & Persistence](#storage--persistence)
10. [Multi-Exchange Support](#multi-exchange-support)
11. [Advanced Usage](#advanced-usage)
12. [Performance & Scalability](#performance--scalability)
13. [Examples](#examples)
14. [Troubleshooting](#troubleshooting)
15. [Project Structure](#project-structure)
16. [License](#license)

---

## Overview

The `CCXTProCollector` class provides a robust, production-ready solution for streaming orderbook data from crypto derivatives exchanges. It supports:

- ✅ **Real-time orderbook streaming** via WebSockets
- ✅ **Futures and Options support** across multiple exchanges
- ✅ **Multi-instrument subscriptions** - monitor hundreds of symbols simultaneously
- ✅ **Automatic reconnection** with configurable retry logic
- ✅ **Historical snapshot storage** for analysis
- ✅ **Multi-exchange support** for cross-exchange comparison
- ✅ **Async/await architecture** for high performance

---

## Installation

### 1. Install CCXT Pro (Required for WebSocket support)

```bash
pip install ccxt[pro]
```

**Note:** CCXT Pro is free for non-commercial use. For commercial use, check [CCXT Pro licensing](https://ccxt.com/pro).

### 2. Install other dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Setup

```bash
python tests/test_ccxt_setup.py
```

---

## Quick Start

### Basic Futures Streaming

```python
import asyncio
from src.data.ccxt_collector import CCXTProCollector, StreamConfig

async def stream_futures():
    # Configure the collector
    config = StreamConfig(
        exchange_id='deribit',
        orderbook_limit=10
    )
    
    # Create collector
    collector = CCXTProCollector(config)
    
    # Start and subscribe
    await collector.start()
    await collector.subscribe_futures(['BTC/USD:BTC', 'ETH/USD:ETH'])
    
    # Get latest orderbooks
    await asyncio.sleep(5)
    btc_ob = collector.get_latest_orderbook('BTC/USD:BTC')
    print(f"BTC Mid Price: ${btc_ob.mid_price:.2f}")
    
    await collector.stop()

asyncio.run(stream_futures())
```

### Streaming Options Orderbooks

```python
async def stream_options():
    config = StreamConfig(exchange_id='deribit')
    collector = CCXTProCollector(config)
    
    await collector.start()
    
    # Get available options
    btc_calls = collector.get_available_options(
        base_currency='BTC',
        option_type='C'
    )
    
    # Subscribe to first 10 calls
    await collector.subscribe_options(btc_calls[:10])
    
    # Monitor for 60 seconds
    await asyncio.sleep(60)
    
    # Export to DataFrame
    df = collector.get_orderbooks_as_dataframe()
    print(df)
    
    await collector.stop()

asyncio.run(stream_options())
```

### Using Callbacks for Real-time Processing

```python
async def callback_example():
    async def on_orderbook_update(orderbook):
        print(f"{orderbook.symbol}: "
              f"Bid=${orderbook.best_bid:.2f} "
              f"Ask=${orderbook.best_ask:.2f}")
    
    config = StreamConfig(
        exchange_id='deribit',
        on_orderbook_update=on_orderbook_update
    )
    
    collector = CCXTProCollector(config)
    await collector.start()
    await collector.subscribe_futures(['BTC/USD:BTC'])
    
    await asyncio.sleep(30)
    await collector.stop()

asyncio.run(callback_example())
```

---

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Application                         │
│  (Trading Strategy, Analysis, Backtesting, etc.)            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              CCXTProCollector / MultiExchangeCollector       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Market Discovery (futures/options)                │   │
│  │  • Subscription Management                           │   │
│  │  • Orderbook Snapshot Storage                        │   │
│  │  • Callbacks & Event Handling                        │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌──────────────────────┐    ┌──────────────────────┐
│   CCXT Pro Library   │    │  OrderbookDataStore  │
│  (WebSocket Client)  │    │  (Data Persistence)  │
└──────────┬───────────┘    └──────────────────────┘
           │                         │
           ▼                         ▼
┌──────────────────────┐    ┌──────────────────────┐
│  Exchange WebSocket  │    │   File System        │
│  (Deribit, etc.)     │    │   (JSONL/CSV/Parquet)│
└──────────────────────┘    └──────────────────────┘
```

### Core Components

#### 1. CCXTProCollector

The main data collection class that handles WebSocket streaming.

**Responsibilities:**
- Initialize and manage exchange connections
- Load and cache market metadata
- Subscribe/unsubscribe to instrument orderbooks
- Maintain real-time orderbook snapshots
- Handle reconnection logic
- Execute user callbacks on updates

**Key Methods:**
- `start()` - Initialize exchange connection
- `subscribe_futures(symbols)` - Subscribe to futures orderbooks
- `subscribe_options(symbols)` - Subscribe to options orderbooks
- `get_latest_orderbook(symbol)` - Retrieve current snapshot
- `get_snapshot_history(symbol)` - Retrieve historical snapshots

#### 2. OrderbookSnapshot

Data structure representing a point-in-time orderbook state.

**Properties:**
- `symbol` - Instrument identifier
- `timestamp` - Snapshot time
- `bids` - List of [price, size] bid levels
- `asks` - List of [price, size] ask levels
- `exchange` - Exchange identifier

**Computed Properties:**
- `best_bid` - Top bid price
- `best_ask` - Top ask price
- `mid_price` - Average of best bid/ask
- `spread` - Bid-ask spread

#### 3. StreamConfig

Configuration object for the collector.

**Key Parameters:**
- Exchange settings (id, credentials, testnet)
- Connection settings (reconnect, rate limits)
- Data storage settings (history size)
- Callbacks (orderbook updates, errors)

#### 4. OrderbookDataStore

Persistence layer for orderbook data.

**Supports:**
- JSONL format (append-only, one JSON per line)
- CSV format (tabular, easy to analyze)
- Parquet format (columnar, efficient storage)

**Features:**
- Automatic file organization by symbol and date
- Load/save operations
- File listing and cleanup

#### 5. MultiExchangeCollector

Orchestrates multiple collectors across exchanges.

**Use Cases:**
- Cross-exchange arbitrage monitoring
- Liquidity comparison
- Price discovery analysis

### Design Decisions

#### Why Async/Await?

- **Concurrency**: Stream hundreds of symbols simultaneously
- **Efficiency**: Non-blocking I/O for WebSocket connections
- **Scalability**: Easy to add more symbols without threading complexity

#### Why Separate Futures and Options?

- **Market Discovery**: Different filtering requirements
- **Data Organization**: Separate tracking of instrument types
- **Analysis**: Simplifies type-specific analytics

#### Why Store Snapshots?

- **Historical Analysis**: Track price movements over time
- **Backtesting**: Replay market conditions
- **Debugging**: Investigate data quality issues

#### Why Multiple Storage Formats?

- **JSONL**: Great for streaming/appending, easy to parse
- **CSV**: Compatible with spreadsheets, simple analysis
- **Parquet**: Efficient for large datasets, fast queries

### Data Flow

#### Subscription Flow

```
User calls subscribe_futures(['BTC/USD:BTC'])
    ↓
CCXTProCollector adds symbol to subscribed_futures set
    ↓
Creates asyncio task for _stream_orderbook(symbol, 'future')
    ↓
Task calls exchange.watch_order_book(symbol) in loop
    ↓
On each update:
    - Create OrderbookSnapshot
    - Store in self.orderbooks[symbol]
    - Append to snapshot_history (if enabled)
    - Call on_orderbook_update callback (if set)
```

#### Error Handling Flow

```
WebSocket error occurs
    ↓
Exception caught in _stream_orderbook
    ↓
Increment reconnect_attempts counter
    ↓
Call on_error callback (if set)
    ↓
Wait reconnect_delay seconds
    ↓
Retry connection (if attempts < max_reconnect_attempts)
```

---

## Core Features

### 1. Market Discovery

```python
await collector.start()

# Get all available futures
all_futures = collector.get_available_futures()
btc_futures = collector.get_available_futures(base_currency='BTC')

# Get all available options
all_options = collector.get_available_options()
btc_calls = collector.get_available_options(base_currency='BTC', option_type='C')
dec_options = collector.get_available_options(expiry='DEC24')
```

### 2. Flexible Subscriptions

```python
# Subscribe to specific symbols
await collector.subscribe_futures(['BTC/USD:BTC', 'ETH/USD:ETH'])
await collector.subscribe_options(['BTC-30DEC24-50000-C', 'BTC-30DEC24-50000-P'])

# Subscribe to all futures
await collector.subscribe_all_futures(base_currency='BTC')

# Subscribe to filtered options
await collector.subscribe_all_options(
    base_currency='BTC',
    option_type='C',
    expiry='DEC24'
)

# Unsubscribe
await collector.unsubscribe('BTC/USD:BTC')
```

### 3. Data Access

```python
# Get latest snapshot for a symbol
orderbook = collector.get_latest_orderbook('BTC/USD:BTC')
print(f"Best Bid: {orderbook.best_bid}")
print(f"Best Ask: {orderbook.best_ask}")
print(f"Mid Price: {orderbook.mid_price}")
print(f"Spread: {orderbook.spread}")

# Get all orderbooks
all_orderbooks = collector.get_all_orderbooks()

# Get only futures or options
futures_obs = collector.get_futures_orderbooks()
options_obs = collector.get_options_orderbooks()

# Export to DataFrame
df = collector.get_orderbooks_as_dataframe()
```

### 4. Historical Analysis

```python
config = StreamConfig(
    exchange_id='deribit',
    store_snapshots=True,
    max_snapshots_per_symbol=1000
)

collector = CCXTProCollector(config)
await collector.start()
await collector.subscribe_futures(['BTC/USD:BTC'])

# Wait to collect data
await asyncio.sleep(300)  # 5 minutes

# Analyze historical snapshots
history = collector.get_snapshot_history('BTC/USD:BTC')
mid_prices = [s.mid_price for s in history]
spreads = [s.spread for s in history]

print(f"Average price: ${sum(mid_prices)/len(mid_prices):.2f}")
print(f"Price volatility: ${max(mid_prices) - min(mid_prices):.2f}")
```

---

## Configuration Reference

### StreamConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `exchange_id` | str | `'deribit'` | Exchange identifier (deribit, binance, okx, etc.) |
| `api_key` | str | `None` | API key for authenticated requests |
| `api_secret` | str | `None` | API secret for authenticated requests |
| `testnet` | bool | `False` | Use testnet/sandbox environment |
| `orderbook_limit` | int | `20` | Number of orderbook levels to fetch |
| `reconnect_delay` | int | `5` | Seconds to wait before reconnecting |
| `max_reconnect_attempts` | int | `10` | Maximum reconnection attempts per symbol |
| `rate_limit` | bool | `True` | Enable rate limiting |
| `store_snapshots` | bool | `True` | Store historical snapshots |
| `max_snapshots_per_symbol` | int | `1000` | Maximum snapshots to store per symbol |
| `on_orderbook_update` | Callable | `None` | Callback for orderbook updates |
| `on_error` | Callable | `None` | Callback for errors |

### Example Configuration

```python
config = StreamConfig(
    exchange_id='deribit',
    testnet=False,
    orderbook_limit=10,
    reconnect_delay=5,
    max_reconnect_attempts=10,
    store_snapshots=True,
    max_snapshots_per_symbol=500,
    on_orderbook_update=my_callback,
    on_error=my_error_handler
)
```

---

## API Reference

### CCXTProCollector

#### Initialization

```python
collector = CCXTProCollector(config: StreamConfig)
```

#### Core Methods

##### `async start()`
Initialize exchange connection and load markets.

```python
await collector.start()
```

##### `async stop()`
Close all connections and cleanup resources.

```python
await collector.stop()
```

##### `async subscribe_futures(symbols: List[str])`
Subscribe to futures orderbook streams.

```python
await collector.subscribe_futures(['BTC/USD:BTC', 'ETH/USD:ETH'])
```

##### `async subscribe_options(symbols: List[str])`
Subscribe to options orderbook streams.

```python
await collector.subscribe_options(['BTC-30DEC24-50000-C'])
```

##### `async subscribe_all_futures(base_currency: Optional[str] = None)`
Subscribe to all available futures, optionally filtered by currency.

```python
await collector.subscribe_all_futures(base_currency='BTC')
```

##### `async subscribe_all_options(**filters)`
Subscribe to all available options with optional filtering.

```python
await collector.subscribe_all_options(
    base_currency='BTC',
    option_type='C',
    expiry='DEC24'
)
```

##### `async unsubscribe(symbol: str)`
Unsubscribe from a symbol.

```python
await collector.unsubscribe('BTC/USD:BTC')
```

#### Data Access Methods

##### `get_latest_orderbook(symbol: str) -> OrderbookSnapshot`
Get the most recent orderbook snapshot.

```python
orderbook = collector.get_latest_orderbook('BTC/USD:BTC')
print(f"Mid Price: ${orderbook.mid_price}")
```

##### `get_all_orderbooks() -> Dict[str, OrderbookSnapshot]`
Get all current orderbook snapshots.

```python
all_obs = collector.get_all_orderbooks()
```

##### `get_futures_orderbooks() -> Dict[str, OrderbookSnapshot]`
Get only futures orderbooks.

```python
futures_obs = collector.get_futures_orderbooks()
```

##### `get_options_orderbooks() -> Dict[str, OrderbookSnapshot]`
Get only options orderbooks.

```python
options_obs = collector.get_options_orderbooks()
```

##### `get_orderbooks_as_dataframe() -> pd.DataFrame`
Export all orderbooks to a pandas DataFrame.

```python
df = collector.get_orderbooks_as_dataframe()
```

##### `get_snapshot_history(symbol: str) -> List[OrderbookSnapshot]`
Get historical snapshots for a symbol.

```python
history = collector.get_snapshot_history('BTC/USD:BTC')
```

#### Market Discovery Methods

##### `get_available_futures(base_currency: Optional[str] = None) -> List[str]`
List available futures symbols.

```python
all_futures = collector.get_available_futures()
btc_futures = collector.get_available_futures(base_currency='BTC')
```

##### `get_available_options(**filters) -> List[str]`
List available options symbols with filtering.

```python
btc_calls = collector.get_available_options(
    base_currency='BTC',
    option_type='C'
)
dec_options = collector.get_available_options(expiry='DEC24')
```

##### `async get_market_info(symbol: str) -> dict`
Get detailed market information.

```python
info = await collector.get_market_info('BTC/USD:BTC')
```

---

## Data Structures

### OrderbookSnapshot

```python
@dataclass
class OrderbookSnapshot:
    symbol: str              # 'BTC/USD:BTC'
    timestamp: datetime      # Snapshot timestamp
    bids: List[List[float]] # [[price, size], ...]
    asks: List[List[float]] # [[price, size], ...]
    exchange: str           # 'deribit'
    
    # Properties
    @property
    def best_bid(self) -> float:
        """Best bid price"""
        
    @property
    def best_ask(self) -> float:
        """Best ask price"""
        
    @property
    def mid_price(self) -> float:
        """(best_bid + best_ask) / 2"""
        
    @property
    def spread(self) -> float:
        """best_ask - best_bid"""
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
```

### Usage Example

```python
orderbook = collector.get_latest_orderbook('BTC/USD:BTC')

print(f"Symbol: {orderbook.symbol}")
print(f"Exchange: {orderbook.exchange}")
print(f"Timestamp: {orderbook.timestamp}")
print(f"Best Bid: ${orderbook.best_bid:.2f}")
print(f"Best Ask: ${orderbook.best_ask:.2f}")
print(f"Mid Price: ${orderbook.mid_price:.2f}")
print(f"Spread: ${orderbook.spread:.2f}")
print(f"Bid Levels: {len(orderbook.bids)}")
print(f"Ask Levels: {len(orderbook.asks)}")
```

---

## Storage & Persistence

### OrderbookDataStore

The `OrderbookDataStore` class provides data persistence in multiple formats.

#### Initialization

```python
from src.data.storage import OrderbookDataStore

store = OrderbookDataStore(base_path="data/raw/orderbooks")
```

#### Saving Data

##### JSONL Format

```python
store.save_snapshot_jsonl(orderbook)
# Saves to: base_path/jsonl/BTC_USD_BTC_20241116.jsonl
```

##### CSV Format

```python
store.save_snapshot_csv(orderbook)
# Saves to: base_path/csv/BTC_USD_BTC_20241116.csv
```

##### Parquet Format

```python
store.save_snapshot_parquet(orderbook)
# Saves to: base_path/parquet/BTC_USD_BTC_20241116.parquet
```

#### Loading Data

```python
# Load JSONL
snapshots = store.load_snapshots_jsonl("BTC_USD_BTC_20241116.jsonl")

# Load CSV
df = store.load_snapshots_csv("BTC_USD_BTC_20241116.csv")

# Load Parquet
df = store.load_snapshots_parquet("BTC_USD_BTC_20241116.parquet")
```

#### File Management

```python
# List files by format
jsonl_files = store.list_files('jsonl')
csv_files = store.list_files('csv')
parquet_files = store.list_files('parquet')

# List all files
all_files = store.list_all_files()
```

### StreamingDataRecorder

Helper class for automatic data recording.

```python
from src.data.storage import StreamingDataRecorder

# Create recorder
recorder = StreamingDataRecorder(
    base_path="data/raw/orderbooks",
    format='both'  # 'jsonl', 'csv', 'parquet', or 'both'
)

# Use as callback
config = StreamConfig(
    exchange_id='deribit',
    on_orderbook_update=recorder.record_snapshot
)

collector = CCXTProCollector(config)
await collector.start()
await collector.subscribe_futures(['BTC/USD:BTC'])

# Data is automatically saved to disk
await asyncio.sleep(3600)

# Get statistics
stats = recorder.get_stats()
print(f"Total snapshots: {stats['total_snapshots']}")
print(f"Symbols recorded: {stats['symbols']}")
```

---

## Multi-Exchange Support

### MultiExchangeCollector

Manage multiple exchanges simultaneously for comparison and arbitrage monitoring.

```python
from src.data.ccxt_collector import MultiExchangeCollector

multi = MultiExchangeCollector()

# Add multiple exchanges
await multi.add_exchange(StreamConfig(exchange_id='deribit'))
await multi.add_exchange(StreamConfig(exchange_id='binance'))

# Subscribe to same symbol on different exchanges
deribit = multi.get_collector('deribit')
binance = multi.get_collector('binance')

await deribit.subscribe_futures(['BTC/USDT:USDT'])
await binance.subscribe_futures(['BTC/USDT:USDT'])

# Compare orderbooks across exchanges
comparison = multi.compare_orderbooks('BTC/USDT:USDT')
print(comparison)
```

### API Methods

#### `async add_exchange(config: StreamConfig)`
Add a new exchange collector.

```python
await multi.add_exchange(StreamConfig(exchange_id='okx'))
```

#### `get_collector(exchange_id: str) -> CCXTProCollector`
Get a specific exchange collector.

```python
okx = multi.get_collector('okx')
```

#### `get_all_collectors() -> Dict[str, CCXTProCollector]`
Get all exchange collectors.

```python
all_collectors = multi.get_all_collectors()
```

#### `compare_orderbooks(symbol: str) -> dict`
Compare orderbooks across all exchanges for a symbol.

```python
comparison = multi.compare_orderbooks('BTC/USD:BTC')
# Returns: {
#     'deribit': OrderbookSnapshot(...),
#     'okx': OrderbookSnapshot(...),
#     ...
# }
```

#### `async stop_all()`
Stop all exchange collectors.

```python
await multi.stop_all()
```

---

## Advanced Usage

### Custom Error Handling

```python
async def handle_error(symbol: str, error: Exception):
    print(f"Error streaming {symbol}: {error}")
    # Log to database, send alert, etc.
    if isinstance(error, NetworkError):
        # Handle network errors
        pass
    elif isinstance(error, ExchangeError):
        # Handle exchange-specific errors
        pass

config = StreamConfig(
    exchange_id='deribit',
    on_error=handle_error
)
```

### Custom Data Processing

```python
async def process_orderbook(orderbook: OrderbookSnapshot):
    # Calculate custom metrics
    imbalance = sum(b[1] for b in orderbook.bids[:5]) / sum(a[1] for a in orderbook.asks[:5])
    
    # Store in database
    await db.save({
        'symbol': orderbook.symbol,
        'mid_price': orderbook.mid_price,
        'imbalance': imbalance,
        'timestamp': orderbook.timestamp
    })
    
    # Send alerts
    if orderbook.spread > 100:
        await send_alert(f"Wide spread on {orderbook.symbol}")

config = StreamConfig(on_orderbook_update=process_orderbook)
```

### Monitoring Multiple Expiries

```python
# Subscribe to options across multiple expiries
for expiry in ['DEC24', 'JAN25', 'FEB25']:
    options = collector.get_available_options(
        base_currency='BTC',
        expiry=expiry,
        option_type='C'
    )
    # Subscribe to top 10 by volume
    await collector.subscribe_options(options[:10])
```

### Building a Volatility Surface

```python
async def build_vol_surface():
    collector = CCXTProCollector(StreamConfig(exchange_id='deribit'))
    await collector.start()
    
    # Get all BTC options
    all_options = collector.get_available_options(base_currency='BTC')
    await collector.subscribe_options(all_options)
    
    # Wait for data
    await asyncio.sleep(10)
    
    # Export to DataFrame
    df = collector.get_orderbooks_as_dataframe()
    
    # Filter options only
    options_df = df[df['symbol'].str.contains('-')]
    
    # Your vol surface calculation here
    # ...
    
    await collector.stop()
```

### Real-time Arbitrage Detection

```python
async def detect_arbitrage():
    multi = MultiExchangeCollector()
    
    await multi.add_exchange(StreamConfig(exchange_id='deribit'))
    await multi.add_exchange(StreamConfig(exchange_id='okx'))
    
    # Subscribe to same symbols
    for exchange_id in ['deribit', 'okx']:
        collector = multi.get_collector(exchange_id)
        await collector.subscribe_futures(['BTC/USD:BTC'])
    
    while True:
        await asyncio.sleep(1)
        
        comparison = multi.compare_orderbooks('BTC/USD:BTC')
        
        if len(comparison) == 2:
            deribit_mid = comparison['deribit'].mid_price
            okx_mid = comparison['okx'].mid_price
            
            diff = abs(deribit_mid - okx_mid)
            if diff > 50:  # $50 arbitrage opportunity
                print(f"Arbitrage: ${diff:.2f} between exchanges")
```

---

## Performance & Scalability

### Performance Characteristics

- **Memory Usage**: ~1-2 KB per symbol per snapshot
- **Network Usage**: ~1-5 KB/s per symbol (depends on update frequency)
- **CPU Usage**: Minimal (async I/O is event-driven)
- **Throughput**: 100+ symbols simultaneously

### Memory Management

For 100 symbols with snapshot history enabled:

```python
# Conservative settings
config = StreamConfig(
    orderbook_limit=5,              # Reduce orderbook depth
    max_snapshots_per_symbol=100,   # Limit history
    store_snapshots=True
)
# ~10-20 MB total memory
```

```python
# Aggressive settings
config = StreamConfig(
    orderbook_limit=20,
    max_snapshots_per_symbol=1000,
    store_snapshots=True
)
# ~100-200 MB total memory
```

### Scalability Considerations

#### Vertical Scaling
- Single collector can handle 100s of symbols
- Limited by: network bandwidth, callback processing time
- Optimize: reduce snapshot history, use faster storage

#### Horizontal Scaling
```python
# Machine 1: BTC instruments
collector1 = CCXTProCollector(StreamConfig(exchange_id='deribit'))
await collector1.subscribe_all_futures(base_currency='BTC')
await collector1.subscribe_all_options(base_currency='BTC')

# Machine 2: ETH instruments
collector2 = CCXTProCollector(StreamConfig(exchange_id='deribit'))
await collector2.subscribe_all_futures(base_currency='ETH')
await collector2.subscribe_all_options(base_currency='ETH')

# Aggregate data centrally
```

### Performance Tips

1. **Limit orderbook depth**: Use `orderbook_limit=5` for faster updates
2. **Disable history**: Set `store_snapshots=False` if not needed
3. **Optimize callbacks**: Keep callback logic fast and non-blocking
4. **Use appropriate symbols**: Don't subscribe to illiquid instruments
5. **Monitor memory**: Periodically clear old snapshots

---

## Examples

### Example 1: Simple Futures Streaming

```python
import asyncio
from src.data.ccxt_collector import CCXTProCollector, StreamConfig

async def simple_futures():
    config = StreamConfig(exchange_id='deribit')
    collector = CCXTProCollector(config)
    
    await collector.start()
    await collector.subscribe_futures(['BTC/USD:BTC'])
    
    # Monitor for 30 seconds
    for i in range(30):
        await asyncio.sleep(1)
        ob = collector.get_latest_orderbook('BTC/USD:BTC')
        print(f"BTC Mid: ${ob.mid_price:.2f}, Spread: ${ob.spread:.2f}")
    
    await collector.stop()

asyncio.run(simple_futures())
```

### Example 2: Options with Auto-Save

```python
from src.data.storage import StreamingDataRecorder

async def options_with_save():
    recorder = StreamingDataRecorder(format='jsonl')
    
    config = StreamConfig(
        exchange_id='deribit',
        on_orderbook_update=recorder.record_snapshot
    )
    
    collector = CCXTProCollector(config)
    await collector.start()
    
    # Get BTC call options
    calls = collector.get_available_options(
        base_currency='BTC',
        option_type='C'
    )[:10]
    
    await collector.subscribe_options(calls)
    
    # Collect for 1 hour
    await asyncio.sleep(3600)
    
    stats = recorder.get_stats()
    print(f"Recorded {stats['total_snapshots']} snapshots")
    
    await collector.stop()

asyncio.run(options_with_save())
```

### Example 3: Multi-Exchange Comparison

```python
from src.data.ccxt_collector import MultiExchangeCollector

async def multi_exchange():
    multi = MultiExchangeCollector()
    
    await multi.add_exchange(StreamConfig(exchange_id='deribit'))
    await multi.add_exchange(StreamConfig(exchange_id='okx'))
    
    # Subscribe to same symbols
    for exchange_id in ['deribit', 'okx']:
        collector = multi.get_collector(exchange_id)
        await collector.subscribe_futures(['BTC/USD:BTC'])
    
    # Monitor for 60 seconds
    for i in range(60):
        await asyncio.sleep(1)
        
        comparison = multi.compare_orderbooks('BTC/USD:BTC')
        
        for exchange, ob in comparison.items():
            print(f"{exchange}: ${ob.mid_price:.2f}", end="  ")
        print()
    
    await multi.stop_all()

asyncio.run(multi_exchange())
```

See `examples/ccxt_streaming_examples.py` for more comprehensive examples.

---

## Troubleshooting

### Common Issues

#### Import Error for ccxt.pro

**Problem:**
```
ImportError: cannot import name 'pro' from 'ccxt'
```

**Solution:**
```bash
pip install ccxt[pro]
```

#### Connection Issues

**Problem:** No data received, connection timeouts

**Solutions:**
- Check internet connection
- Verify `exchange_id` is correct and supported
- Try testnet mode first: `StreamConfig(testnet=True)`
- Check API credentials if using authenticated endpoints
- Increase reconnect delay: `StreamConfig(reconnect_delay=10)`

#### Symbol Not Found

**Problem:**
```
Exchange.BadSymbol: Symbol 'XXX' not found
```

**Solution:**
```python
# List available symbols
futures = collector.get_available_futures()
print(futures[:10])  # See correct format

# Symbol formats vary by exchange
# Deribit: 'BTC/USD:BTC'
# Binance: 'BTC/USDT:USDT'
# OKX: 'BTC/USD:BTC'
```

#### High Memory Usage

**Problem:** Application consuming too much memory

**Solutions:**
```python
# Reduce snapshot history
config = StreamConfig(
    max_snapshots_per_symbol=100,
    orderbook_limit=5
)

# Or disable history
config = StreamConfig(store_snapshots=False)

# Periodically clear old snapshots
collector.snapshot_history.clear()
```

#### Slow Callback Execution

**Problem:** Callbacks blocking the event loop

**Solution:**
```python
# Make callbacks async and fast
async def fast_callback(orderbook):
    # Quick processing only
    print(orderbook.mid_price)
    
    # For heavy processing, use separate task
    asyncio.create_task(heavy_processing(orderbook))

async def heavy_processing(orderbook):
    # Long-running computation
    pass
```

#### Rate Limit Errors

**Problem:**
```
ccxt.RateLimitExceeded: Rate limit exceeded
```

**Solution:**
```python
# Enable rate limiting
config = StreamConfig(rate_limit=True)

# Reduce number of simultaneous subscriptions
# Subscribe in batches instead of all at once
```

### Debugging Tips

#### Enable Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ccxt')
logger.setLevel(logging.DEBUG)
```

#### Test Connection

```python
# Minimal test
async def test():
    config = StreamConfig(exchange_id='deribit')
    collector = CCXTProCollector(config)
    
    try:
        await collector.start()
        print("✓ Connection successful")
        
        futures = collector.get_available_futures()
        print(f"✓ Found {len(futures)} futures")
        
        await collector.subscribe_futures([futures[0]])
        await asyncio.sleep(5)
        
        ob = collector.get_latest_orderbook(futures[0])
        print(f"✓ Received data: {ob.mid_price}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        await collector.stop()

asyncio.run(test())
```

#### Verify Setup

```bash
python tests/test_ccxt_setup.py
```

### Getting Help

1. **Check Documentation**
   - This README for usage
   - Examples for patterns
   - Architecture docs for internals

2. **Run Diagnostics**
   ```bash
   python tests/test_ccxt_setup.py
   ```

3. **CCXT Resources**
   - [CCXT Pro Manual](https://github.com/ccxt/ccxt/wiki/ccxt.pro.manual)
   - [CCXT Issues](https://github.com/ccxt/ccxt/issues)
   
4. **Exchange Documentation**
   - [Deribit API](https://docs.deribit.com/)
   - [Binance API](https://binance-docs.github.io/apidocs/)
   - [OKX API](https://www.okx.com/docs-v5/)

---

## Project Structure

### Directory Layout

```
src/data/ccxt_collector/
├── __init__.py                     # Module exports
├── ccxt_collector.py              # Main collector implementation
├── storage.py                      # Data persistence
└── README.md                       # This file (comprehensive guide)

examples/
└── ccxt_streaming_examples.py     # Working examples

tests/
└── test_ccxt_setup.py             # Setup verification

data/raw/orderbooks/
├── jsonl/                         # JSONL format data
├── csv/                           # CSV format data
└── parquet/                       # Parquet format data
```

### Implementation Files

- **`ccxt_collector.py`** (720 lines) - Core streaming collector
  - `CCXTProCollector` class
  - `OrderbookSnapshot` dataclass
  - `StreamConfig` dataclass
  - `MultiExchangeCollector` class

- **`storage.py`** (350 lines) - Data persistence
  - `OrderbookDataStore` class
  - `StreamingDataRecorder` class

### What Was Created

✅ Full-featured WebSocket streaming collector  
✅ Real-time futures and options support  
✅ Data persistence in multiple formats  
✅ Multi-exchange orchestration  
✅ Comprehensive documentation  
✅ Working examples  
✅ Testing utilities  

### Supported Exchanges

- **Deribit** - Full support (futures + options) ✅
- **OKX** - Full support (futures + options) ✅
- **Binance** - Futures support, limited options ✅
- **Bybit** - Futures support ✅
- **Huobi** - Futures support ✅
- Any CCXT Pro compatible exchange

Check [CCXT Pro documentation](https://github.com/ccxt/ccxt/wiki/ccxt.pro) for the complete list.

---

## License

### CCXT Licensing

- **CCXT**: MIT License (free for all use)
- **CCXT Pro**: Free for non-commercial use
  - Commercial use requires a license
  - See: https://ccxt.com/pro

### This Implementation

This collector implementation follows your project's license terms.

---

## Contributing

Contributions welcome! Please ensure:
- Code follows existing patterns
- Add tests for new features
- Update documentation
- Follow async/await best practices

---

## Support

For issues with:
- **This collector**: Open an issue in this repository
- **CCXT Pro**: Check [CCXT GitHub](https://github.com/ccxt/ccxt/issues)
- **Exchange APIs**: Refer to exchange documentation

---

## Summary

You now have a complete, production-ready system for collecting real-time crypto derivatives data. This implementation provides:

✅ Real-time WebSocket streaming  
✅ Futures and options support  
✅ Multi-exchange capabilities  
✅ Flexible data persistence  
✅ Comprehensive error handling  
✅ Historical analysis tools  
✅ Production-ready architecture  

Ready to build sophisticated crypto options trading strategies! 🚀

---

**Created**: November 16, 2024  
**Status**: Production-ready  
**Version**: 1.0.0

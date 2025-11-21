# Deribit Data Collection Schemas

Schema definitions for data collection from Deribit exchange.

## Files

### `futures.py`
Futures ticker data (perpetuals and dated futures)
- **Instruments**: BTC-PERPETUAL, ETH-PERPETUAL, BTC-27DEC24, etc.
- **Required fields**: 8
- **Optional fields**: 14 (includes funding rates, volume, delivery price)

### `options.py`
Options ticker data (calls and puts)
- **Instruments**: BTC-27DEC24-50000-C, ETH-29NOV24-3000-P, etc.
- **Required fields**: 12
- **Optional fields**: 10 (includes greeks and implied volatility)

### `spot.py`
Spot ticker data (not currently supported by Deribit)
- **Status**: Placeholder for future compatibility
- **Required fields**: 7

## Futures Schema

### Required (8)
```
timestamp, instrument_name, exchange,
best_bid, best_bid_amount, best_ask, best_ask_amount,
index_price
```

### Optional (14)
```
last_price, mark_price,
current_funding, funding_8h, next_funding_time,
volume_24h, volume_24h_usd, open_interest,
delivery_price, settlement_price,
price_change_24h, price_change_24h_pct,
high_24h, low_24h
```

## Options Schema

### Required (12)
```
timestamp, instrument_name, exchange,
best_bid, best_bid_amount, best_ask, best_ask_amount,
underlying_price, index_price,
strike_price, option_type, expiry_timestamp
```

### Optional (10)
```
last_price, mark_price,
delta, gamma, vega, theta, rho,
implied_volatility,
volume_24h, open_interest
```

## Orderbook Schema

All instrument types use the same orderbook format:
- **Levels**: 10 (hard-coded)
- **Fields**: 43 total (3 core + 40 orderbook)
- **Core**: `timestamp`, `instrument_name`, `exchange`
- **Orderbook**: `bid1, bidamt1, ask1, askamt1, ..., bid10, bidamt10, ask10, askamt10`

## Usage

```python
from schema.deribit import futures, options

# Check required fields for futures
print(futures.REQUIRED_FIELDS)

# Validate data
data = {"timestamp": 1700000000000, ...}
missing = [f for f in futures.REQUIRED_FIELDS if f not in data]
if missing:
    print(f"Missing: {missing}")
```

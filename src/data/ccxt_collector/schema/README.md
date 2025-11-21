# Exchange Schema Definitions

This directory contains exchange-specific schema definitions for data collection.

## Structure

```
schema/
├── deribit/          # Deribit exchange schemas
│   ├── futures.py    # Futures ticker fields
│   ├── options.py    # Options ticker fields
│   ├── spot.py       # Spot ticker fields (not currently used)
│   └── README.md     # Deribit-specific documentation
└── binance/          # Binance exchange schemas (if needed)
```

## Usage

Import schemas for validation and data collection:

```python
from schema.deribit import futures, options

# Access field definitions
print(futures.REQUIRED_FIELDS)
print(options.ALL_FIELDS)
```

## Schema Format

Each exchange directory contains Python files that define:
- `REQUIRED_FIELDS` - Fields that must be present
- `OPTIONAL_FIELDS` - Fields that are nice to have
- `ALL_FIELDS` - Combined list of all fields

## Orderbook Schema

All exchanges use the same orderbook snapshot format:
- **10 levels** hard-coded
- **Naming**: `bid1, bidamt1, ask1, askamt1, bid2, bidamt2, ...`
- Defined in `ccxt_collector.OrderbookSnapshot.to_dict()`

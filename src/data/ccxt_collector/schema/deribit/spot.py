"""
Deribit Spot Ticker Schema

Fields to collect for spot trading pairs.

Note: Deribit does not currently support spot trading.
This schema is included for completeness and future compatibility.
"""

# Pattern: ticker.{instrument_name}.{interval}
# Examples: BTC/USDT, ETH/USDT (hypothetical)

REQUIRED_FIELDS = [
    "timestamp",              # Unix timestamp in milliseconds
    "instrument_name",        # e.g., BTC/USDT
    "exchange",               # "deribit"
    "best_bid",               # Best bid price
    "best_bid_amount",        # Size at best bid
    "best_ask",               # Best ask price
    "best_ask_amount",        # Size at best ask
]

OPTIONAL_FIELDS = [
    "last_price",             # Last traded price
    "volume_24h",             # 24h volume in base currency
    "volume_24h_usd",         # 24h volume in USD
    "price_change_24h",       # Absolute price change
    "price_change_24h_pct",   # Percentage price change
    "high_24h",               # 24h high
    "low_24h",                # 24h low
]

ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS

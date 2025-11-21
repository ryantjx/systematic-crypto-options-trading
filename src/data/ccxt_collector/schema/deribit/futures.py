"""
Deribit Futures Ticker Schema

Fields to collect for futures contracts (perpetuals and dated futures).
"""

# Pattern: ticker.{instrument_name}.{interval}
# Examples: BTC-PERPETUAL, ETH-27DEC24

REQUIRED_FIELDS = [
    "timestamp",              # Unix timestamp in milliseconds
    "instrument_name",        # e.g., BTC-PERPETUAL, ETH-27DEC24
    "exchange",               # "deribit"
    "best_bid",               # Best bid price
    "best_bid_amount",        # Size at best bid
    "best_ask",               # Best ask price
    "best_ask_amount",        # Size at best ask
    "index_price",            # Underlying index price
]

OPTIONAL_FIELDS = [
    "last_price",             # Last traded price
    "mark_price",             # Mark price for margin
    "current_funding",        # Current funding rate (perpetuals)
    "funding_8h",             # Predicted 8h funding rate
    "next_funding_time",      # Timestamp of next funding
    "volume_24h",             # 24h volume in base currency
    "volume_24h_usd",         # 24h volume in USD
    "open_interest",          # Total outstanding contracts
    "delivery_price",         # Settlement price (dated futures)
    "settlement_price",       # Daily settlement price
    "price_change_24h",       # Absolute price change
    "price_change_24h_pct",   # Percentage price change
    "high_24h",               # 24h high
    "low_24h",                # 24h low
]

ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS

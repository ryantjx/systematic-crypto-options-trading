"""
Deribit Options Ticker Schema

Fields to collect for options contracts (calls and puts).
"""

# Pattern: ticker.{instrument_name}.{interval}
# Examples: BTC-27DEC24-50000-C, ETH-29NOV24-3000-P

REQUIRED_FIELDS = [
    "timestamp",              # Unix timestamp in milliseconds
    "instrument_name",        # e.g., BTC-27DEC24-50000-C
    "exchange",               # "deribit"
    "best_bid",               # Best bid price
    "best_bid_amount",        # Size at best bid
    "best_ask",               # Best ask price
    "best_ask_amount",        # Size at best ask
    "underlying_price",       # Current underlying asset price
    "index_price",            # Underlying index price
    "strike_price",           # Option strike price
    "option_type",            # 'C' for call, 'P' for put
    "expiry_timestamp",       # Expiration timestamp
]

OPTIONAL_FIELDS = [
    "last_price",             # Last traded price
    "mark_price",             # Mark price
    "delta",                  # Option delta
    "gamma",                  # Option gamma
    "vega",                   # Option vega
    "theta",                  # Option theta
    "rho",                    # Option rho
    "implied_volatility",     # Implied volatility (%)
    "volume_24h",             # 24h trading volume
    "open_interest",          # Current open interest
]

ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS
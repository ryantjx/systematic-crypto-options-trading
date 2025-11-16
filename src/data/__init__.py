# """
# Data collection and processing modules.
# """

# from .collectors import (
#     BaseDataCollector,
#     DeribitCollector,
#     BinanceCollector,
# )

# try:
#     from .ccxt_collector import (
#         CCXTProCollector,
#         StreamConfig,
#         OrderbookSnapshot,
#         MultiExchangeCollector,
#     )
#     from .storage import (
#         OrderbookDataStore,
#         StreamingDataRecorder,
#     )
#     CCXT_PRO_AVAILABLE = True
# except ImportError:
#     CCXT_PRO_AVAILABLE = False

# __all__ = [
#     'BaseDataCollector',
#     'DeribitCollector',
#     'BinanceCollector',
# ]

# if CCXT_PRO_AVAILABLE:
#     __all__.extend([
#         'CCXTProCollector',
#         'StreamConfig',
#         'OrderbookSnapshot',
#         'MultiExchangeCollector',
#         'OrderbookDataStore',
#         'StreamingDataRecorder',
#     ])

# This package handles:
# - Market data collection from exchanges (Deribit, Binance, etc.)
# - Data cleaning and validation
# - Storage and retrieval
# - Real-time and historical data pipelines
# """

# from .collectors import *
# from .processors import *
# from .loaders import *

from .ccxt_collector.ccxt_collector import CCXTProCollector, StreamConfig, OrderbookSnapshot, MultiExchangeCollector
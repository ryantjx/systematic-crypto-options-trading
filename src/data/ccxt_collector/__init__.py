"""
CCXT Pro WebSocket Data Collection Module

Real-time streaming data collector for cryptocurrency futures and options.
"""

try:
    from .ccxt_collector import (
        CCXTProCollector,
        StreamConfig,
        OrderbookSnapshot,
        MultiExchangeCollector,
    )
    from .storage import (
        OrderbookDataStore,
        StreamingDataRecorder,
    )
    CCXT_PRO_AVAILABLE = True
except ImportError as e:
    CCXT_PRO_AVAILABLE = False
    _import_error = str(e)

__all__ = [
    'CCXTProCollector',
    'StreamConfig',
    'OrderbookSnapshot',
    'MultiExchangeCollector',
    'OrderbookDataStore',
    'StreamingDataRecorder',
    'CCXT_PRO_AVAILABLE',
]

if not CCXT_PRO_AVAILABLE:
    import warnings
    warnings.warn(
        f"CCXT Pro not available: {_import_error}\n"
        "Install with: pip install ccxt[pro]",
        ImportWarning
    )

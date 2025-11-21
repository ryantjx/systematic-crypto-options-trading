"""
CCXT Pro WebSocket-based data collector for futures and options markets.

This module provides real-time streaming of orderbook data for crypto derivatives
using CCXT Pro's websocket functionality.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Callable, Any
from datetime import datetime
from collections import defaultdict
import pandas as pd
from dataclasses import dataclass, field
import logging

try:
    import ccxt.pro as ccxtpro
except ImportError:
    raise ImportError(
        "ccxt.pro is required for streaming data collection. "
        "Install with: pip install ccxt[pro]"
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import schema definitions
try:
    from schema.deribit import futures as deribit_futures_schema
    from schema.deribit import options as deribit_options_schema
except ImportError:
    logger.warning(
        "Schema definitions not found. Running without schema validation. "
        "Ensure schema directory is in the Python path."
    )
    deribit_futures_schema = None
    deribit_options_schema = None


@dataclass
class OrderbookSnapshot:
    """Represents a snapshot of an orderbook at a point in time."""
    
    symbol: str
    timestamp: datetime
    bids: List[List[float]]  # [[price, size], ...]
    asks: List[List[float]]  # [[price, size], ...]
    exchange: str
    

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format with flattened orderbook levels (10 levels).
        
        Returns:
            Dictionary with symbol, timestamp, exchange, and flattened bid/ask data.
            Format: bid1, bidamt1, ask1, askamt1, bid2, bidamt2, ask2, askamt2, ...
        """
        result = {
            'symbol': self.symbol,
            'timestamp': self.timestamp,
            'exchange': self.exchange
        }
        
        # Add 10 levels of bid/ask data
        for i in range(10):
            result[f'bid{i+1}'] = self.bids[i][0] if i < len(self.bids) else None
            result[f'bidamt{i+1}'] = self.bids[i][1] if i < len(self.bids) else None
            result[f'ask{i+1}'] = self.asks[i][0] if i < len(self.asks) else None
            result[f'askamt{i+1}'] = self.asks[i][1] if i < len(self.asks) else None
        
        return result


@dataclass
class TickerSnapshot:
    """Represents a snapshot of ticker data at a point in time."""
    
    symbol: str
    timestamp: datetime
    exchange: str
    instrument_type: str  # 'future' or 'option'
    data: Dict[str, Any]  # Raw ticker data
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format with all ticker fields.
        
        Returns:
            Dictionary with ticker data including timestamp and metadata.
        """
        result = {
            'symbol': self.symbol,
            'timestamp': self.timestamp,
            'exchange': self.exchange,
            'instrument_type': self.instrument_type,
        }
        result.update(self.data)
        return result
    
    def validate_schema(self, exchange: str = 'deribit') -> tuple[bool, List[str]]:
        """
        Validate ticker data against the appropriate schema.
        
        Args:
            exchange: Exchange name (default: 'deribit')
            
        Returns:
            Tuple of (is_valid, missing_required_fields)
        """
        if exchange == 'deribit':
            if self.instrument_type == 'future':
                if deribit_futures_schema:
                    required = deribit_futures_schema.REQUIRED_FIELDS
                else:
                    return True, []  # Skip validation if schema not available
            elif self.instrument_type == 'option':
                if deribit_options_schema:
                    required = deribit_options_schema.REQUIRED_FIELDS
                else:
                    return True, []
            else:
                return True, []  # Unknown type, skip validation
            
            # Check for missing required fields
            missing = [f for f in required if f not in self.data]
            return len(missing) == 0, missing
        
        return True, []  # Unknown exchange, skip validation


@dataclass
class StreamConfig:
    """Configuration for the streaming data collector."""
    
    exchange_id: str = 'deribit'
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    testnet: bool = False
    orderbook_limit: int = 20  # Number of orderbook levels to fetch
    reconnect_delay: int = 5  # Seconds to wait before reconnecting
    max_reconnect_attempts: int = 10
    rate_limit: bool = True
    
    # Callback settings
    on_orderbook_update: Optional[Callable] = None
    on_error: Optional[Callable] = None


class CCXTProCollector:
    """
    Real-time data collector using CCXT Pro websockets.
    
    Supports streaming orderbook data for futures and options across
    multiple instruments simultaneously.
    
    Example:
        ```python
        config = StreamConfig(
            exchange_id='deribit',
            api_key='your_key',
            api_secret='your_secret'
        )
        
        collector = CCXTProCollector(config)
        
        # Define callback for orderbook updates
        def on_update(orderbook: OrderbookSnapshot):
            print(f"{orderbook.symbol}: {orderbook.mid_price}")
        
        collector.config.on_orderbook_update = on_update
        
        # Start streaming
        await collector.start()
        await collector.subscribe_futures(['BTC/USDT:USDT'])
        await collector.subscribe_options(['BTC-30DEC24-50000-C'])
        ```
    """
    
    def __init__(self, config: StreamConfig):
        """
        Initialize the CCXT Pro collector.
        
        Args:
            config: StreamConfig object with exchange and connection settings
        """
        self.config = config
        self.exchange: Optional[ccxtpro.Exchange] = None
        
        # Track subscribed symbols
        self.subscribed_futures: Set[str] = set()
        self.subscribed_options: Set[str] = set()
        
        # Store latest orderbook snapshots
        self.orderbooks: Dict[str, OrderbookSnapshot] = {}
        
        # Track running tasks
        self.tasks: List[asyncio.Task] = []
        self.is_running: bool = False
        
        # Market metadata cache
        self._futures_markets: Dict[str, Dict] = {}
        self._options_markets: Dict[str, Dict] = {}
        self._markets_loaded: bool = False
    
    async def start(self):
        """Initialize the exchange connection and load markets."""
        logger.info(f"Initializing {self.config.exchange_id} connection...")
        
        # Initialize exchange
        exchange_class = getattr(ccxtpro, self.config.exchange_id)
        
        exchange_config = {
            'enableRateLimit': self.config.rate_limit,
        }
        
        if self.config.api_key and self.config.api_secret:
            exchange_config['apiKey'] = self.config.api_key
            exchange_config['secret'] = self.config.api_secret
        
        if self.config.testnet:
            exchange_config['options'] = {'defaultType': 'test'}
        
        self.exchange = exchange_class(exchange_config)
        
        # Load markets
        await self._load_markets()
        
        self.is_running = True
        logger.info(f"Connected to {self.config.exchange_id}")
    
    async def stop(self):
        """Stop all streaming tasks and close exchange connection."""
        logger.info("Stopping data collector...")
        self.is_running = False
        
        # Cancel all running tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for all tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        # Close exchange connection
        if self.exchange:
            await self.exchange.close()
        
        logger.info("Data collector stopped")
    
    async def _load_markets(self):
        """Load and cache market information."""
        if not self.exchange:
            raise RuntimeError("Exchange not initialized. Call start() first.")
        
        logger.info("Loading markets...")
        markets = await self.exchange.load_markets()
        
        # Separate futures and options markets
        for symbol, market in markets.items():
            if market.get('type') == 'future' or market.get('future'):
                self._futures_markets[symbol] = market
            elif market.get('type') == 'option' or market.get('option'):
                self._options_markets[symbol] = market
        
        self._markets_loaded = True
        logger.info(
            f"Loaded {len(self._futures_markets)} futures "
            f"and {len(self._options_markets)} options markets"
        )
    
    def get_available_futures(self, base_currency: Optional[str] = None) -> List[str]:
        """
        Get list of available futures symbols.
        
        Args:
            base_currency: Filter by base currency (e.g., 'BTC', 'ETH')
            
        Returns:
            List of futures symbol strings
        """
        if not self._markets_loaded:
            raise RuntimeError("Markets not loaded. Call start() first.")
        
        symbols = list(self._futures_markets.keys())
        
        if base_currency:
            symbols = [s for s in symbols if s.startswith(base_currency)]
        
        return sorted(symbols)
    
    def get_available_options(
        self,
        base_currency: Optional[str] = None,
        option_type: Optional[str] = None,
        expiry: Optional[str] = None
    ) -> List[str]:
        """
        Get list of available options symbols.
        
        Args:
            base_currency: Filter by base currency (e.g., 'BTC', 'ETH')
            option_type: Filter by 'C' (call) or 'P' (put)
            expiry: Filter by expiry date string (e.g., '30DEC24')
            
        Returns:
            List of options symbol strings
        """
        if not self._markets_loaded:
            raise RuntimeError("Markets not loaded. Call start() first.")
        
        symbols = list(self._options_markets.keys())
        
        if base_currency:
            symbols = [s for s in symbols if s.startswith(base_currency)]
        
        if option_type:
            symbols = [s for s in symbols if f'-{option_type}' in s]
        
        if expiry:
            symbols = [s for s in symbols if expiry in s]
        
        return sorted(symbols)
    
    async def subscribe_futures(self, symbols: List[str]):
        """
        Subscribe to orderbook updates for futures symbols.
        
        Args:
            symbols: List of futures symbols to subscribe to
        """
        if not self.is_running:
            raise RuntimeError("Collector not running. Call start() first.")
        
        for symbol in symbols:
            if symbol not in self.subscribed_futures:
                self.subscribed_futures.add(symbol)
                # Create a task for each symbol
                task = asyncio.create_task(self._stream_orderbook(symbol, 'future'))
                self.tasks.append(task)
                logger.info(f"Subscribed to futures orderbook: {symbol}")
    
    async def subscribe_options(self, symbols: List[str]):
        """
        Subscribe to orderbook updates for options symbols.
        
        Args:
            symbols: List of options symbols to subscribe to
        """
        if not self.is_running:
            raise RuntimeError("Collector not running. Call start() first.")
        
        for symbol in symbols:
            if symbol not in self.subscribed_options:
                self.subscribed_options.add(symbol)
                # Create a task for each symbol
                task = asyncio.create_task(self._stream_orderbook(symbol, 'option'))
                self.tasks.append(task)
                logger.info(f"Subscribed to options orderbook: {symbol}")
    
    async def subscribe_all_futures(self, base_currency: Optional[str] = None):
        """
        Subscribe to all available futures.
        
        Args:
            base_currency: Optional filter by base currency
        """
        symbols = self.get_available_futures(base_currency)
        await self.subscribe_futures(symbols)
    
    async def subscribe_all_options(
        self,
        base_currency: Optional[str] = None,
        option_type: Optional[str] = None,
        expiry: Optional[str] = None
    ):
        """
        Subscribe to all available options matching filters.
        
        Args:
            base_currency: Optional filter by base currency
            option_type: Optional filter by 'C' (call) or 'P' (put)
            expiry: Optional filter by expiry date
        """
        symbols = self.get_available_options(base_currency, option_type, expiry)
        await self.subscribe_options(symbols)
    
    async def unsubscribe(self, symbol: str):
        """
        Unsubscribe from a symbol's orderbook updates.
        
        Args:
            symbol: Symbol to unsubscribe from
        """
        self.subscribed_futures.discard(symbol)
        self.subscribed_options.discard(symbol)
        logger.info(f"Unsubscribed from: {symbol}")
    
    async def _stream_orderbook(self, symbol: str, market_type: str):
        """
        Stream orderbook updates for a specific symbol.
        
        Args:
            symbol: Symbol to stream
            market_type: 'future' or 'option'
        """
        reconnect_attempts = 0
        
        while self.is_running and (
            symbol in self.subscribed_futures or symbol in self.subscribed_options
        ):
            try:
                # Watch orderbook updates
                orderbook = await self.exchange.watch_order_book(
                    symbol,
                    limit=self.config.orderbook_limit
                )
                
                # Reset reconnect counter on successful connection
                reconnect_attempts = 0
                
                # Create snapshot
                snapshot = OrderbookSnapshot(
                    symbol=symbol,
                    timestamp=datetime.fromtimestamp(orderbook['timestamp'] / 1000)
                    if orderbook.get('timestamp')
                    else datetime.now(),
                    bids=orderbook['bids'],
                    asks=orderbook['asks'],
                    exchange=self.config.exchange_id
                )
                
                # Store latest snapshot
                self.orderbooks[symbol] = snapshot
                
                # Call user callback if provided
                if self.config.on_orderbook_update:
                    try:
                        await self.config.on_orderbook_update(snapshot)
                    except Exception as e:
                        logger.error(f"Error in orderbook callback: {e}")
                
            except Exception as e:
                logger.error(f"Error streaming {symbol}: {e}")
                reconnect_attempts += 1
                
                if reconnect_attempts >= self.config.max_reconnect_attempts:
                    logger.error(
                        f"Max reconnect attempts reached for {symbol}. Giving up."
                    )
                    break
                
                # Call error callback if provided
                if self.config.on_error:
                    try:
                        await self.config.on_error(symbol, e)
                    except Exception as callback_error:
                        logger.error(f"Error in error callback: {callback_error}")
                
                # Wait before reconnecting
                await asyncio.sleep(self.config.reconnect_delay)
    
    def get_latest_orderbook(self, symbol: str) -> Optional[OrderbookSnapshot]:
        """
        Get the latest orderbook snapshot for a symbol.
        
        Args:
            symbol: Symbol to retrieve
            
        Returns:
            OrderbookSnapshot or None if not available
        """
        return self.orderbooks.get(symbol)
    
    def get_all_orderbooks(self) -> Dict[str, OrderbookSnapshot]:
        """
        Get all latest orderbook snapshots.
        
        Returns:
            Dictionary mapping symbols to their latest OrderbookSnapshot
        """
        return self.orderbooks.copy()
    
    def get_orderbooks_as_dataframe(self) -> pd.DataFrame:
        """
        Convert current orderbook snapshots to a pandas DataFrame.
        
        Returns:
            DataFrame with orderbook data for all subscribed symbols
        """
        if not self.orderbooks:
            return pd.DataFrame()
        
        data = [ob.to_dict() for ob in self.orderbooks.values()]
        return pd.DataFrame(data)
    
    def get_futures_orderbooks(self) -> Dict[str, OrderbookSnapshot]:
        """Get orderbooks for all subscribed futures."""
        return {
            symbol: ob
            for symbol, ob in self.orderbooks.items()
            if symbol in self.subscribed_futures
        }
    
    def get_options_orderbooks(self) -> Dict[str, OrderbookSnapshot]:
        """Get orderbooks for all subscribed options."""
        return {
            symbol: ob
            for symbol, ob in self.orderbooks.items()
            if symbol in self.subscribed_options
        }
    
    async def get_market_info(self, symbol: str) -> Optional[Dict]:
        """
        Get detailed market information for a symbol.
        
        Args:
            symbol: Symbol to get info for
            
        Returns:
            Market info dictionary or None
        """
        if not self._markets_loaded:
            await self._load_markets()
        
        return (
            self._futures_markets.get(symbol) or
            self._options_markets.get(symbol)
        )
    
    def get_futures_required_fields(self) -> List[str]:
        """
        Get list of required fields for futures ticker data based on exchange schema.
        
        Returns:
            List of required field names
        """
        if self.config.exchange_id == 'deribit' and deribit_futures_schema:
            return deribit_futures_schema.REQUIRED_FIELDS.copy()
        return []
    
    def get_futures_optional_fields(self) -> List[str]:
        """
        Get list of optional fields for futures ticker data based on exchange schema.
        
        Returns:
            List of optional field names
        """
        if self.config.exchange_id == 'deribit' and deribit_futures_schema:
            return deribit_futures_schema.OPTIONAL_FIELDS.copy()
        return []
    
    def get_options_required_fields(self) -> List[str]:
        """
        Get list of required fields for options ticker data based on exchange schema.
        
        Returns:
            List of required field names
        """
        if self.config.exchange_id == 'deribit' and deribit_options_schema:
            return deribit_options_schema.REQUIRED_FIELDS.copy()
        return []
    
    def get_options_optional_fields(self) -> List[str]:
        """
        Get list of optional fields for options ticker data based on exchange schema.
        
        Returns:
            List of optional field names
        """
        if self.config.exchange_id == 'deribit' and deribit_options_schema:
            return deribit_options_schema.OPTIONAL_FIELDS.copy()
        return []
    
    def validate_ticker_data(
        self, 
        data: Dict[str, Any], 
        instrument_type: str
    ) -> tuple[bool, List[str]]:
        """
        Validate ticker data against the appropriate schema.
        
        Args:
            data: Ticker data dictionary to validate
            instrument_type: 'future' or 'option'
            
        Returns:
            Tuple of (is_valid, missing_required_fields)
        """
        if self.config.exchange_id == 'deribit':
            if instrument_type == 'future' and deribit_futures_schema:
                required = deribit_futures_schema.REQUIRED_FIELDS
            elif instrument_type == 'option' and deribit_options_schema:
                required = deribit_options_schema.REQUIRED_FIELDS
            else:
                return True, []  # No schema available
            
            missing = [f for f in required if f not in data]
            return len(missing) == 0, missing
        
        return True, []  # Unknown exchange


class MultiExchangeCollector:
    """
    Manage multiple CCXT Pro collectors across different exchanges.
    
    Useful for collecting data from multiple exchanges simultaneously
    and comparing orderbooks, prices, and liquidity.
    """
    
    def __init__(self):
        """Initialize multi-exchange collector."""
        self.collectors: Dict[str, CCXTProCollector] = {}
    
    async def add_exchange(self, config: StreamConfig):
        """
        Add an exchange collector.
        
        Args:
            config: StreamConfig for the exchange
        """
        if config.exchange_id in self.collectors:
            logger.warning(f"Exchange {config.exchange_id} already added")
            return
        
        collector = CCXTProCollector(config)
        await collector.start()
        self.collectors[config.exchange_id] = collector
        logger.info(f"Added exchange: {config.exchange_id}")
    
    async def stop_all(self):
        """Stop all exchange collectors."""
        for collector in self.collectors.values():
            await collector.stop()
        self.collectors.clear()
    
    def get_collector(self, exchange_id: str) -> Optional[CCXTProCollector]:
        """Get collector for a specific exchange."""
        return self.collectors.get(exchange_id)
    
    def get_all_orderbooks(self) -> Dict[str, Dict[str, OrderbookSnapshot]]:
        """
        Get orderbooks from all exchanges.
        
        Returns:
            Dictionary mapping exchange_id -> {symbol -> OrderbookSnapshot}
        """
        return {
            exchange_id: collector.get_all_orderbooks()
            for exchange_id, collector in self.collectors.items()
        }
    
    def compare_orderbooks(self, symbol: str) -> pd.DataFrame:
        """
        Compare orderbooks for the same symbol across exchanges.
        
        Args:
            symbol: Symbol to compare
            
        Returns:
            DataFrame with comparison data
        """
        data = []
        for exchange_id, collector in self.collectors.items():
            ob = collector.get_latest_orderbook(symbol)
            if ob:
                row = ob.to_dict()
                row['exchange'] = exchange_id
                data.append(row)
        
        return pd.DataFrame(data) if data else pd.DataFrame()

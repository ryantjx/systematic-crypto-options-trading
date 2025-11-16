#!/usr/bin/env python3
"""
Stream BTC futures with expiries from Deribit using CCXT Pro.

This script streams real-time orderbook data for all Bitcoin futures contracts
with expiration dates (excludes perpetuals). Includes comprehensive logging,
monitoring, and data storage capabilities.

Features:
- Auto-discovers all BTC futures with expiry dates
- Real-time orderbook streaming via WebSocket
- Monitoring of price changes, spreads, and update rates
- Multi-format data storage (JSONL and Parquet)
- Comprehensive logging with colored console output
- Graceful error handling and reconnection

Usage:
    python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py [options]
    
Examples:
    # Stream all BTC futures for 60 seconds (no storage)
    python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py
    
    # Stream for 5 minutes with data storage
    python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --duration 300 --store
    
    # Stream specific expiry months
    python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --expiries DEC24 MAR25
    
    # Use JSONL format only
    python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --store --format jsonl
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.ccxt_collector.ccxt_collector import (
    CCXTProCollector,
    StreamConfig,
    OrderbookSnapshot
)
from src.data.ccxt_collector.storage import OrderbookDataStore, StreamingDataRecorder
from src.logging.logger import setup_logging, get_logger


# Setup logging - unique log file for this example
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"btc_futures_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

setup_logging(
    level="INFO",
    log_file=log_file,
    console=True,
    colored=True
)

logger = get_logger(__name__)


class BTCFuturesMonitor:
    """
    Monitor and display statistics for BTC futures streaming.
    
    Tracks price movements, spreads, update rates, and provides
    real-time insights into market activity across all expiries.
    """
    
    def __init__(self):
        self.update_count: Dict[str, int] = {}
        self.last_prices: Dict[str, float] = {}
        self.min_prices: Dict[str, float] = {}
        self.max_prices: Dict[str, float] = {}
        self.spread_stats: Dict[str, List[float]] = defaultdict(list)
        self.start_time = datetime.now()
        self.total_updates = 0
    
    async def on_orderbook_update(self, snapshot: OrderbookSnapshot):
        """
        Callback for orderbook updates with comprehensive logging.
        
        Args:
            snapshot: OrderbookSnapshot from the exchange
        """
        symbol = snapshot.symbol
        
        # Initialize tracking for new symbols
        if symbol not in self.update_count:
            self.update_count[symbol] = 0
            logger.info(f"🎯 Started streaming {symbol}")
        
        self.update_count[symbol] += 1
        self.total_updates += 1
        
        # Track and log price movements
        mid_price = snapshot.mid_price
        if mid_price:
            # Initialize min/max tracking
            if symbol not in self.min_prices:
                self.min_prices[symbol] = mid_price
                self.max_prices[symbol] = mid_price
                logger.info(
                    f"💰 {symbol}: Initial price ${mid_price:,.2f} | "
                    f"Spread: ${snapshot.spread:.2f}"
                )
            else:
                # Update min/max
                self.min_prices[symbol] = min(self.min_prices[symbol], mid_price)
                self.max_prices[symbol] = max(self.max_prices[symbol], mid_price)
                
                # Check for significant price changes
                price_change = mid_price - self.last_prices[symbol]
                pct_change = (price_change / self.last_prices[symbol]) * 100
                
                # Log significant moves (>= 0.1%)
                if abs(pct_change) >= 0.1:
                    direction = "📈" if price_change > 0 else "📉"
                    logger.info(
                        f"{direction} {symbol}: ${mid_price:,.2f} "
                        f"({pct_change:+.2f}%) | "
                        f"Spread: ${snapshot.spread:.2f}"
                    )
            
            self.last_prices[symbol] = mid_price
        
        # Track spread statistics
        if snapshot.spread:
            self.spread_stats[symbol].append(snapshot.spread)
        
        # Periodic summary stats (every 100 updates per symbol)
        count = self.update_count[symbol]
        if count % 100 == 0:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            rate = count / elapsed if elapsed > 0 else 0
            
            # Calculate spread stats
            spreads = self.spread_stats[symbol]
            avg_spread = sum(spreads) / len(spreads) if spreads else 0
            
            logger.info(
                f"📊 {symbol}: {count} updates "
                f"(~{rate:.1f}/sec) | "
                f"Avg spread: ${avg_spread:.2f}"
            )
    
    async def on_error(self, symbol: str, error: Exception):
        """
        Callback for streaming errors.
        
        Args:
            symbol: Symbol that encountered an error
            error: Exception that occurred
        """
        logger.error(f"❌ Error streaming {symbol}: {error}")
    
    def print_summary(self):
        """Print comprehensive summary statistics."""
        logger.info("=" * 70)
        logger.info("📈 BTC FUTURES STREAMING SESSION SUMMARY")
        logger.info("=" * 70)
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        logger.info(f"⏱️  Duration: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        logger.info(f"🎯 Contracts tracked: {len(self.update_count)}")
        logger.info(f"📡 Total updates: {self.total_updates:,}")
        logger.info(f"📊 Avg update rate: {self.total_updates/elapsed:.1f} updates/sec")
        logger.info("")
        logger.info("Per-Contract Statistics:")
        logger.info("-" * 70)
        
        # Sort by expiry (chronologically)
        sorted_symbols = sorted(self.update_count.keys())
        
        for symbol in sorted_symbols:
            count = self.update_count[symbol]
            rate = count / elapsed if elapsed > 0 else 0
            last_price = self.last_prices.get(symbol, 0)
            min_price = self.min_prices.get(symbol, 0)
            max_price = self.max_prices.get(symbol, 0)
            price_range = max_price - min_price if max_price and min_price else 0
            
            # Calculate average spread
            spreads = self.spread_stats[symbol]
            avg_spread = sum(spreads) / len(spreads) if spreads else 0
            
            logger.info(f"  {symbol}:")
            logger.info(f"    Updates: {count:,} (~{rate:.1f}/sec)")
            logger.info(f"    Last price: ${last_price:,.2f}")
            logger.info(f"    Price range: ${min_price:,.2f} - ${max_price:,.2f} (${price_range:.2f})")
            logger.info(f"    Avg spread: ${avg_spread:.2f}")
        
        logger.info("=" * 70)


async def get_btc_futures_with_expiry(
    collector: CCXTProCollector,
    expiry_filters: Optional[List[str]] = None
) -> List[str]:
    """
    Discover BTC futures with expiration dates (excludes perpetuals).
    
    Args:
        collector: Initialized CCXTProCollector instance
        expiry_filters: Optional list of expiry strings to filter (e.g., ['DEC24', 'MAR25'])
    
    Returns:
        List of BTC futures symbols with expiries
    """
    logger.info("🔍 Discovering BTC futures contracts...")
    
    # Get all BTC futures
    all_btc_futures = collector.get_available_futures(base_currency='BTC')
    
    # Filter out perpetuals (they contain 'PERPETUAL' in the symbol)
    futures_with_expiry = [
        symbol for symbol in all_btc_futures
        if 'PERPETUAL' not in symbol
    ]
    
    # Apply expiry filters if specified
    if expiry_filters:
        filtered = []
        for symbol in futures_with_expiry:
            for expiry in expiry_filters:
                if expiry.upper() in symbol.upper():
                    filtered.append(symbol)
                    break
        futures_with_expiry = filtered
    
    logger.info(f"✅ Found {len(futures_with_expiry)} BTC futures with expiries")
    for symbol in sorted(futures_with_expiry):
        logger.info(f"   - {symbol}")
    
    return futures_with_expiry


async def stream_btc_futures(
    duration: int = 60,
    store_data: bool = True,
    data_format: str = 'both',
    expiry_filters: Optional[List[str]] = None
):
    """
    Stream BTC futures with expiries from Deribit.
    
    Args:
        duration: How long to stream in seconds
        store_data: Whether to store data to disk
        data_format: Storage format ('jsonl', 'parquet', or 'both')
        expiry_filters: Optional list of expiry months to filter (e.g., ['DEC24', 'MAR25'])
    """
    logger.info("=" * 70)
    logger.info("🚀 BTC FUTURES STREAMING - DERIBIT")
    logger.info("=" * 70)
    logger.info(f"⏱️  Duration: {duration} seconds ({duration/60:.1f} minutes)")
    logger.info(f"💾 Data storage: {'Enabled' if store_data else 'Disabled'}")
    if store_data:
        logger.info(f"📁 Storage format: {data_format}")
    if expiry_filters:
        logger.info(f"🔍 Filtering expiries: {', '.join(expiry_filters)}")
    logger.info("-" * 70)
    
    # Create monitor
    monitor = BTCFuturesMonitor()
    
    # Setup data storage
    recorder = None
    if store_data:
        data_dir = Path(__file__).parent / "data"
        data_store = OrderbookDataStore(base_path=str(data_dir / "orderbooks"))
        session_name = datetime.now().strftime('%Y%m%d_%H%M%S')
        recorder = StreamingDataRecorder(
            data_store=data_store,
            format=data_format,
            include_csv_depth=False,  # Keep storage lightweight
            session_name=session_name
        )
        logger.info(f"📁 Data directory: {data_dir}")
        logger.info(f"📝 Session name: {session_name}")
    
    # Combined callback for monitoring and recording
    async def combined_callback(snapshot: OrderbookSnapshot):
        """Combined callback for monitoring and recording."""
        await monitor.on_orderbook_update(snapshot)
        if recorder:
            await recorder.record_snapshot(snapshot)
    
    # Configure collector
    config = StreamConfig(
        exchange_id='deribit',
        testnet=False,  # Production
        orderbook_limit=10,
        on_orderbook_update=combined_callback,
        on_error=monitor.on_error,
        store_snapshots=True,
        max_snapshots_per_symbol=1000
    )
    
    # Create and start collector
    collector = CCXTProCollector(config)
    
    try:
        # Initialize connection
        await collector.start()
        
        # Discover BTC futures with expiries
        futures_symbols = await get_btc_futures_with_expiry(
            collector,
            expiry_filters=expiry_filters
        )
        
        if not futures_symbols:
            logger.warning("⚠️  No BTC futures found matching criteria")
            return
        
        # Subscribe to futures
        logger.info(f"📡 Subscribing to {len(futures_symbols)} futures contracts...")
        await collector.subscribe_futures(futures_symbols)
        
        # Stream for specified duration
        logger.info(f"⏱️  Streaming started... (Press Ctrl+C to stop early)")
        logger.info("-" * 70)
        await asyncio.sleep(duration)
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Stream interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
    finally:
        # Stop collector
        logger.info("\n🛑 Stopping data stream...")
        await collector.stop()
        
        # Flush parquet data if recording
        if recorder:
            logger.info("💾 Flushing data to parquet...")
            recorder.flush_parquet()
        
        # Print summary
        monitor.print_summary()
        
        # Print storage stats
        if recorder:
            stats = recorder.get_stats()
            logger.info("\n📦 DATA STORAGE STATISTICS")
            logger.info(f"  Session: {stats['session_name']}")
            logger.info(f"  Total snapshots recorded: {stats['total_snapshots']:,}")
            logger.info(f"  JSONL files: {stats['jsonl_files']}")
            logger.info(f"  Parquet files: {stats['parquet_files']}")
            
            # List specific files created
            if data_format in ['jsonl', 'both']:
                jsonl_file = data_dir / 'orderbooks' / 'jsonl' / f"btc_futures_{stats['session_name']}.jsonl"
                logger.info(f"\n📄 JSONL: {jsonl_file}")
            if data_format in ['parquet', 'both']:
                parquet_file = data_dir / 'orderbooks' / 'parquet' / f"btc_futures_{stats['session_name']}.parquet"
                logger.info(f"📄 Parquet: {parquet_file}")
        
        logger.info(f"\n📝 Session log: {log_file}")
        logger.info("=" * 70)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Stream BTC futures with expiries from Deribit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Stream all BTC futures for 60 seconds (no storage)
  python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py
  
  # Stream for 5 minutes with data storage
  python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --duration 300 --store
  
  # Stream only December 2024 and March 2025 expiries
  python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --expiries DEC24 MAR25 --store
  
  # Use JSONL format only for 10 minutes
  python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --duration 600 --store --format jsonl
  
  # Stream for 1 hour with parquet storage
  python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --duration 3600 --store --format parquet
        """
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Duration to stream in seconds (default: 60)'
    )
    
    parser.add_argument(
        '--store',
        action='store_true',
        help='Enable data storage to disk (default: disabled)'
    )
    
    parser.add_argument(
        '--format',
        choices=['jsonl', 'parquet', 'both'],
        default='both',
        help='Data storage format (default: both)'
    )
    
    parser.add_argument(
        '--expiries',
        nargs='+',
        help='Filter by expiry months (e.g., DEC24 MAR25 JUN25)'
    )
    
    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()
    
    await stream_btc_futures(
        duration=args.duration,
        store_data=args.store,
        data_format=args.format,
        expiry_filters=args.expiries
    )


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)

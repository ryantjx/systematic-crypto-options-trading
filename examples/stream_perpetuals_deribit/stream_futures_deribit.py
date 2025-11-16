#!/usr/bin/env python3
"""
Stream BTC and ETH futures data from Deribit using CCXT Pro.

This script demonstrates real-time streaming of orderbook data for Bitcoin and
Ethereum futures on Deribit exchange. It logs all data updates and stores them
to disk in multiple formats (JSONL and CSV).

Usage:
    python examples/stream_futures_deribit/stream_futures_deribit.py [--duration SECONDS] [--symbols SYMBOL1 SYMBOL2 ...]
    
Examples:
    # Stream for 60 seconds (default, no data storage)
    python examples/stream_futures_deribit/stream_futures_deribit.py
    
    # Stream for 5 minutes with data storage
    python examples/stream_futures_deribit/stream_futures_deribit.py --duration 300 --store
    
    # Stream specific symbols
    python examples/stream_futures_deribit/stream_futures_deribit.py --symbols BTC-PERPETUAL ETH-PERPETUAL
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List

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
log_file = log_dir / f"stream_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

setup_logging(
    level="INFO",
    log_file=log_file,
    console=True,
    colored=True
)

logger = get_logger(__name__)


class FuturesStreamMonitor:
    """Monitor and display statistics for futures streaming."""
    
    def __init__(self):
        self.update_count = {}
        self.last_prices = {}
        self.start_time = datetime.now()
    
    async def on_orderbook_update(self, snapshot: OrderbookSnapshot):
        """Callback for orderbook updates with logging and monitoring."""
        symbol = snapshot.symbol
        
        # Update counters
        if symbol not in self.update_count:
            self.update_count[symbol] = 0
            logger.info(f"🎯 Started receiving data for {symbol}")
        
        self.update_count[symbol] += 1
        
        # Log price updates
        mid_price = snapshot.mid_price
        if mid_price:
            # Check for significant price changes
            if symbol in self.last_prices:
                price_change = mid_price - self.last_prices[symbol]
                pct_change = (price_change / self.last_prices[symbol]) * 100
                
                if abs(pct_change) >= 0.1:  # Log if change >= 0.1%
                    direction = "📈" if price_change > 0 else "📉"
                    logger.info(
                        f"{direction} {symbol}: ${mid_price:.2f} "
                        f"({pct_change:+.2f}%) | "
                        f"Spread: ${snapshot.spread:.2f}"
                    )
            else:
                logger.info(
                    f"💰 {symbol}: Initial price ${mid_price:.2f} | "
                    f"Spread: ${snapshot.spread:.2f}"
                )
            
            self.last_prices[symbol] = mid_price
        
        # Log periodic statistics
        count = self.update_count[symbol]
        if count % 50 == 0:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            rate = count / elapsed if elapsed > 0 else 0
            logger.info(
                f"📊 {symbol}: {count} updates received "
                f"(~{rate:.1f} updates/sec)"
            )
    
    async def on_error(self, symbol: str, error: Exception):
        """Callback for errors."""
        logger.error(f"❌ Error streaming {symbol}: {error}")
    
    def print_summary(self):
        """Print summary statistics."""
        logger.info("=" * 60)
        logger.info("📈 STREAMING SESSION SUMMARY")
        logger.info("=" * 60)
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        logger.info(f"Duration: {elapsed:.1f} seconds")
        logger.info(f"Symbols tracked: {len(self.update_count)}")
        
        for symbol, count in sorted(self.update_count.items()):
            rate = count / elapsed if elapsed > 0 else 0
            last_price = self.last_prices.get(symbol, 0)
            logger.info(
                f"  {symbol}: {count} updates (~{rate:.1f}/sec) | "
                f"Last price: ${last_price:.2f}"
            )
        
        logger.info("=" * 60)


async def stream_futures(
    symbols: List[str],
    duration: int = 60,
    store_data: bool = True,
    data_format: str = 'both'
):
    """
    Stream futures data from Deribit.
    
    Args:
        symbols: List of futures symbols to stream
        duration: How long to stream in seconds
        store_data: Whether to store data to disk
        data_format: Storage format ('jsonl', 'csv', or 'both')
    """
    logger.info("🚀 Starting Deribit Futures Data Stream")
    logger.info(f"Symbols: {', '.join(symbols)}")
    logger.info(f"Duration: {duration} seconds")
    logger.info(f"Data storage: {'Enabled' if store_data else 'Disabled'}")
    if store_data:
        logger.info(f"Storage format: {data_format}")
    logger.info("-" * 60)
    
    # Create monitor
    monitor = FuturesStreamMonitor()
    
    # Setup data storage
    recorder = None
    if store_data:
        data_dir = Path(__file__).parent / "data"
        data_store = OrderbookDataStore(base_path=str(data_dir / "orderbooks"))
        recorder = StreamingDataRecorder(
            data_store=data_store,
            format=data_format,
            include_csv_depth=True
        )
        logger.info(f"📁 Data will be stored in: {data_dir}")
    
    # Create combined callback
    async def combined_callback(snapshot: OrderbookSnapshot):
        """Combined callback for monitoring and recording."""
        await monitor.on_orderbook_update(snapshot)
        if recorder:
            await recorder.record_snapshot(snapshot)
    
    # Configure collector
    config = StreamConfig(
        exchange_id='deribit',
        testnet=False,  # Use production
        orderbook_limit=10,
        on_orderbook_update=combined_callback,
        on_error=monitor.on_error,
        store_snapshots=True,
        max_snapshots_per_symbol=1000
    )
    
    # Create collector
    collector = CCXTProCollector(config)
    
    try:
        # Start collector
        await collector.start()
        
        # Subscribe to futures
        logger.info(f"📡 Subscribing to {len(symbols)} futures symbols...")
        await collector.subscribe_futures(symbols)
        
        # Stream for specified duration
        logger.info(f"⏱️  Streaming for {duration} seconds... (Press Ctrl+C to stop early)")
        await asyncio.sleep(duration)
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Stream interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
    finally:
        # Stop collector
        logger.info("🛑 Stopping data stream...")
        await collector.stop()
        
        # Print summary
        monitor.print_summary()
        
        # Print storage stats
        if recorder:
            stats = recorder.get_stats()
            logger.info("\n📦 STORAGE STATISTICS")
            logger.info(f"  Total snapshots recorded: {stats['total_snapshots']}")
            logger.info(f"  JSONL files: {stats['jsonl_files']}")
            logger.info(f"  CSV files: {stats['csv_files']}")
        
        logger.info(f"\n📄 Session log saved to: {log_file}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Stream BTC and ETH futures data from Deribit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Stream default symbols (BTC and ETH perpetuals) for 60 seconds (no storage)
  python examples/stream_futures_deribit/stream_futures_deribit.py
  
  # Stream for 5 minutes with data storage
  python examples/stream_futures_deribit/stream_futures_deribit.py --duration 300 --store
  
  # Stream specific futures contracts
  python examples/stream_futures_deribit/stream_futures_deribit.py --symbols BTC-PERPETUAL ETH-PERPETUAL BTC-27DEC24
  
  # Enable data storage with specific format
  python examples/stream_futures_deribit/stream_futures_deribit.py --store --format csv
        """
    )
    
    parser.add_argument(
        '--symbols',
        nargs='+',
        default=['BTC-PERPETUAL', 'ETH-PERPETUAL'],
        help='Futures symbols to stream (default: BTC-PERPETUAL ETH-PERPETUAL)'
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
        choices=['jsonl', 'csv', 'both'],
        default='both',
        help='Data storage format (default: both)'
    )
    
    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()
    
    await stream_futures(
        symbols=args.symbols,
        duration=args.duration,
        store_data=args.store,
        data_format=args.format
    )


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Goodbye!")
        sys.exit(0)

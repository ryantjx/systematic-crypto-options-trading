#!/usr/bin/env python3
"""
Stream BTC futures with expiries from Deribit using CCXT Pro.

This script streams real-time orderbook data for all Bitcoin futures contracts
with expiration dates (excludes perpetuals). Includes comprehensive logging,
monitoring, and data storage capabilities.

Features:
- Auto-discovers all BTC futures with expiry dates
- Real-time orderbook streaming via WebSocket
- Monitoring of update rates and data flow
- Multi-format data storage (JSONL and Parquet)
- Comprehensive logging with colored console output
- Graceful error handling and reconnection

Usage:
    python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py [options]
    
Examples:
    # Stream all BTC futures for 60 seconds
    python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py
    
    # Stream specific expiry months
    python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --expiries DEC24 MAR25
"""

import asyncio
import argparse
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.data.ccxt_collector.ccxt_collector import (
    CCXTProCollector,
    StreamConfig,
    OrderbookSnapshot
)
from src.logging.logger import setup_logging, get_logger


# Define data directory
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Setup logging - fixed log file
log_file = DATA_DIR / "output.log"

setup_logging(
    level="INFO",
    log_file=log_file,
    console=True,
    colored=True
)

logger = get_logger(__name__)


class SimpleDataWriter:
    """
    Simple data writer for streaming data.
    Writes to output.jsonl and output.parquet without timestamps in filenames.
    """
    
    def __init__(self):
        self.jsonl_path = DATA_DIR / "output.jsonl"
        self.parquet_path = DATA_DIR / "output.parquet"
        self.buffer: List[Dict[str, Any]] = []
        self.buffer_size = 100  # Flush to parquet every 100 snapshots
        
        # Clear existing files
        if self.jsonl_path.exists():
            self.jsonl_path.unlink()
        if self.parquet_path.exists():
            self.parquet_path.unlink()
            
        logger.info(f"📝 Data will be written to {self.jsonl_path} and {self.parquet_path}")

    async def write(self, snapshot: OrderbookSnapshot):
        """Write snapshot to storage."""
        data = snapshot.to_dict()
        data['timestamp'] = snapshot.timestamp.isoformat()
        
        # Write to JSONL immediately
        with self.jsonl_path.open('a') as f:
            json.dump(data, f)
            f.write('\n')
            
        # Add to buffer for Parquet
        # For parquet, we need datetime objects for timestamp, not strings if we want proper types
        parquet_data = snapshot.to_dict()
        parquet_data['timestamp'] = snapshot.timestamp
        self.buffer.append(parquet_data)
        
        if len(self.buffer) >= self.buffer_size:
            self.flush_parquet()
            
    def flush_parquet(self):
        """Flush buffer to parquet file."""
        if not self.buffer:
            return
            
        df = pd.DataFrame(self.buffer)
        
        # Append to parquet if exists, otherwise create
        if self.parquet_path.exists():
            existing_df = pd.read_parquet(self.parquet_path)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.to_parquet(self.parquet_path, engine='pyarrow', compression='snappy', index=False)
        else:
            df.to_parquet(self.parquet_path, engine='pyarrow', compression='snappy', index=False)
            
        self.buffer.clear()


class BTCFuturesMonitor:
    """
    Monitor and display statistics for BTC futures streaming.
    
    Tracks update rates and provides real-time insights into 
    market activity across all expiries.
    """
    
    def __init__(self):
        self.update_count: Dict[str, int] = {}
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
        
        # Periodic summary stats (every 100 updates per symbol)
        count = self.update_count[symbol]
        if count % 100 == 0:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            rate = count / elapsed if elapsed > 0 else 0
            
            logger.info(
                f"📊 {symbol}: {count} updates "
                f"(~{rate:.1f}/sec)"
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
            
            logger.info(f"  {symbol}:")
            logger.info(f"    Updates: {count:,} (~{rate:.1f}/sec)")
        
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
    expiry_filters: Optional[List[str]] = None
):
    """
    Stream BTC futures with expiries from Deribit.
    
    Args:
        duration: How long to stream in seconds
        expiry_filters: Optional list of expiry months to filter (e.g., ['DEC24', 'MAR25'])
    """
    logger.info("=" * 70)
    logger.info("🚀 BTC FUTURES STREAMING - DERIBIT")
    logger.info("=" * 70)
    logger.info(f"⏱️  Duration: {duration} seconds ({duration/60:.1f} minutes)")
    if expiry_filters:
        logger.info(f"🔍 Filtering expiries: {', '.join(expiry_filters)}")
    logger.info("-" * 70)
    
    # Create monitor and writer
    monitor = BTCFuturesMonitor()
    writer = SimpleDataWriter()
    
    # Combined callback for monitoring and recording
    async def combined_callback(snapshot: OrderbookSnapshot):
        """Combined callback for monitoring and recording."""
        await monitor.on_orderbook_update(snapshot)
        await writer.write(snapshot)
    
    # Configure collector
    config = StreamConfig(
        exchange_id='deribit',
        testnet=False,  # Production
        orderbook_limit=10,
        on_orderbook_update=combined_callback,
        on_error=monitor.on_error
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
        
        # Flush remaining data
        writer.flush_parquet()
        
        # Print summary
        monitor.print_summary()
        
        logger.info(f"\n📝 Session log: {log_file}")
        logger.info("=" * 70)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Stream BTC futures with expiries from Deribit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Stream all BTC futures for 60 seconds
  python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py
  
  # Stream for 5 minutes
  python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --duration 300
  
  # Stream only December 2024 and March 2025 expiries
  python examples/stream_btc_futures_deribit/stream_btc_futures_deribit.py --expiries DEC24 MAR25
        """
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Duration to stream in seconds (default: 60)'
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
        expiry_filters=args.expiries
    )


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)

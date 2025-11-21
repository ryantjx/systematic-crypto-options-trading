#!/usr/bin/env python3
"""
Stream BTC and ETH futures data from Deribit using CCXT Pro.

This script demonstrates real-time streaming of orderbook data for Bitcoin and
Ethereum futures on Deribit exchange. It logs all data updates and stores them
to disk in multiple formats (JSONL and Parquet).

Usage:
    python examples/stream_futures_deribit/stream_futures_deribit.py [--duration SECONDS] [--symbols SYMBOL1 SYMBOL2 ...]
    
Examples:
    # Stream for 60 seconds
    python examples/stream_futures_deribit/stream_futures_deribit.py
    
    # Stream specific symbols
    python examples/stream_futures_deribit/stream_futures_deribit.py --symbols BTC-PERPETUAL ETH-PERPETUAL
"""

import asyncio
import argparse
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

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


class FuturesStreamMonitor:
    """Monitor and display statistics for futures streaming."""
    
    def __init__(self):
        self.update_count = {}
        self.start_time = datetime.now()
    
    async def on_orderbook_update(self, snapshot: OrderbookSnapshot):
        """Callback for orderbook updates with logging and monitoring."""
        symbol = snapshot.symbol
        
        # Update counters
        if symbol not in self.update_count:
            self.update_count[symbol] = 0
            logger.info(f"🎯 Started receiving data for {symbol}")
        
        self.update_count[symbol] += 1
        
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
            logger.info(
                f"  {symbol}: {count} updates (~{rate:.1f}/sec)"
            )
        
        logger.info("=" * 60)


async def stream_futures(
    symbols: List[str],
    duration: int = 60
):
    """
    Stream futures data from Deribit.
    
    Args:
        symbols: List of futures symbols to stream
        duration: How long to stream in seconds
    """
    logger.info("🚀 Starting Deribit Futures Data Stream")
    logger.info(f"Symbols: {', '.join(symbols)}")
    logger.info(f"Duration: {duration} seconds")
    logger.info("-" * 60)
    
    # Create monitor and writer
    monitor = FuturesStreamMonitor()
    writer = SimpleDataWriter()
    
    # Create combined callback
    async def combined_callback(snapshot: OrderbookSnapshot):
        """Combined callback for monitoring and recording."""
        await monitor.on_orderbook_update(snapshot)
        await writer.write(snapshot)
    
    # Configure collector
    config = StreamConfig(
        exchange_id='deribit',
        testnet=False,  # Use production
        orderbook_limit=10,
        on_orderbook_update=combined_callback,
        on_error=monitor.on_error
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
        
        # Flush remaining data
        writer.flush_parquet()
        
        # Print summary
        monitor.print_summary()
        
        logger.info(f"\n📄 Session log saved to: {log_file}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Stream BTC and ETH futures data from Deribit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Stream default symbols (BTC and ETH perpetuals) for 60 seconds
  python examples/stream_futures_deribit/stream_futures_deribit.py
  
  # Stream for 5 minutes
  python examples/stream_futures_deribit/stream_futures_deribit.py --duration 300
  
  # Stream specific futures contracts
  python examples/stream_futures_deribit/stream_futures_deribit.py --symbols BTC-PERPETUAL ETH-PERPETUAL BTC-27DEC24
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
        default=15,
        help='Duration to stream in seconds (default: 60)'
    )
    
    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()
    
    await stream_futures(
        symbols=args.symbols,
        duration=args.duration
    )


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Goodbye!")
        sys.exit(0)

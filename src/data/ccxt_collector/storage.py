"""
Data storage utilities for CCXT Pro collector.

Provides helpers for persisting orderbook data to various formats.
"""

import json
import csv
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import pandas as pd

from .ccxt_collector import OrderbookSnapshot


class OrderbookDataStore:
    """
    Store and manage orderbook snapshot data.
    
    Supports multiple storage formats:
    - JSONL (JSON Lines) - One JSON object per line
    - CSV - Flattened orderbook data
    - Parquet - Columnar format for analytics
    """
    
    def __init__(self, base_path: str = "data/raw/orderbooks"):
        """
        Initialize data store.
        
        Args:
            base_path: Base directory for storing orderbook data
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.jsonl_path = self.base_path / "jsonl"
        self.csv_path = self.base_path / "csv"
        self.parquet_path = self.base_path / "parquet"
        
        self.jsonl_path.mkdir(exist_ok=True)
        self.csv_path.mkdir(exist_ok=True)
        self.parquet_path.mkdir(exist_ok=True)
    
    def save_snapshot_jsonl(
        self,
        snapshot: OrderbookSnapshot,
        filename: Optional[str] = None
    ):
        """
        Save snapshot to JSONL format.
        
        Args:
            snapshot: OrderbookSnapshot to save
            filename: Optional custom filename (default: symbol_YYYYMMDD.jsonl)
        """
        if filename is None:
            # Create filename from symbol and date
            safe_symbol = snapshot.symbol.replace('/', '_').replace(':', '_')
            date_str = snapshot.timestamp.strftime('%Y%m%d')
            filename = f"{safe_symbol}_{date_str}.jsonl"
        
        filepath = self.jsonl_path / filename
        
        # Prepare data
        data = snapshot.to_dict()
        data['timestamp'] = snapshot.timestamp.isoformat()
        
        # Append to file
        with filepath.open('a') as f:
            json.dump(data, f)
            f.write('\n')
    
    def save_snapshot_csv(
        self,
        snapshot: OrderbookSnapshot,
        filename: Optional[str] = None,
        include_depth: bool = False
    ):
        """
        Save snapshot to CSV format.
        
        Args:
            snapshot: OrderbookSnapshot to save
            filename: Optional custom filename
            include_depth: Include full orderbook depth (default: False)
        """
        if filename is None:
            safe_symbol = snapshot.symbol.replace('/', '_').replace(':', '_')
            date_str = snapshot.timestamp.strftime('%Y%m%d')
            filename = f"{safe_symbol}_{date_str}.csv"
        
        filepath = self.csv_path / filename
        
        # Check if file exists to determine if we need headers
        file_exists = filepath.exists()
        
        # Prepare row data
        row = {
            'timestamp': snapshot.timestamp.isoformat(),
            'symbol': snapshot.symbol,
            'exchange': snapshot.exchange,
            'best_bid': snapshot.best_bid,
            'best_ask': snapshot.best_ask,
            'mid_price': snapshot.mid_price,
            'spread': snapshot.spread,
            'bid_depth': len(snapshot.bids),
            'ask_depth': len(snapshot.asks),
        }
        
        if include_depth:
            # Add full orderbook depth
            for i, bid_entry in enumerate(snapshot.bids[:10]):
                row[f'bid_price_{i}'] = bid_entry[0]
                row[f'bid_size_{i}'] = bid_entry[1]
            for i, ask_entry in enumerate(snapshot.asks[:10]):
                row[f'ask_price_{i}'] = ask_entry[0]
                row[f'ask_size_{i}'] = ask_entry[1]
        
        # Write to CSV
        with filepath.open('a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    
    def save_snapshots_parquet(
        self,
        snapshots: List[OrderbookSnapshot],
        filename: str
    ):
        """
        Save multiple snapshots to Parquet format.
        
        Args:
            snapshots: List of OrderbookSnapshot objects
            filename: Output filename (without extension)
        """
        if not snapshots:
            return
        
        # Convert to DataFrame
        data = [s.to_dict() for s in snapshots]
        df = pd.DataFrame(data)
        
        # Save to parquet
        filepath = self.parquet_path / f"{filename}.parquet"
        df.to_parquet(filepath, engine='pyarrow', compression='snappy')
    
    def load_snapshots_jsonl(
        self,
        filename: str,
        limit: Optional[int] = None
    ) -> List[dict]:
        """
        Load snapshots from JSONL file.
        
        Args:
            filename: JSONL filename to load
            limit: Optional limit on number of snapshots to load
            
        Returns:
            List of snapshot dictionaries
        """
        filepath = self.jsonl_path / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        snapshots = []
        with filepath.open('r') as f:
            for i, line in enumerate(f):
                if limit and i >= limit:
                    break
                snapshots.append(json.loads(line))
        
        return snapshots
    
    def load_snapshots_csv(
        self,
        filename: str,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Load snapshots from CSV file.
        
        Args:
            filename: CSV filename to load
            limit: Optional limit on number of rows
            
        Returns:
            DataFrame with snapshot data
        """
        filepath = self.csv_path / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        nrows = limit if limit else None
        return pd.read_csv(filepath, nrows=nrows)
    
    def load_snapshots_parquet(self, filename: str) -> pd.DataFrame:
        """
        Load snapshots from Parquet file.
        
        Args:
            filename: Parquet filename (without extension)
            
        Returns:
            DataFrame with snapshot data
        """
        filepath = self.parquet_path / f"{filename}.parquet"
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        return pd.read_parquet(filepath)
    
    def list_files(self, format: str = 'jsonl') -> List[str]:
        """
        List available data files.
        
        Args:
            format: File format ('jsonl', 'csv', or 'parquet')
            
        Returns:
            List of filenames
        """
        if format == 'jsonl':
            path = self.jsonl_path
            pattern = '*.jsonl'
        elif format == 'csv':
            path = self.csv_path
            pattern = '*.csv'
        elif format == 'parquet':
            path = self.parquet_path
            pattern = '*.parquet'
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return [f.name for f in path.glob(pattern)]
    
    def cleanup_old_files(self, days: int = 7):
        """
        Remove files older than specified days.
        
        Args:
            days: Remove files older than this many days
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        
        for path in [self.jsonl_path, self.csv_path, self.parquet_path]:
            for file in path.iterdir():
                if file.is_file() and datetime.fromtimestamp(file.stat().st_mtime) < cutoff:
                    file.unlink()
                    print(f"Removed old file: {file.name}")


class StreamingDataRecorder:
    """
    Helper class to automatically record streaming data.
    
    Can be used as a callback for CCXTProCollector.
    Stores all instruments in consolidated files.
    """
    
    def __init__(
        self,
        data_store: Optional[OrderbookDataStore] = None,
        format: str = 'jsonl',
        include_csv_depth: bool = False,
        session_name: Optional[str] = None
    ):
        """
        Initialize recorder.
        
        Args:
            data_store: OrderbookDataStore instance (creates new if None)
            format: Storage format ('jsonl', 'parquet', or 'both')
            include_csv_depth: Include full depth in CSV (legacy)
            session_name: Name for this session's files (default: timestamp)
        """
        self.data_store = data_store or OrderbookDataStore()
        self.format = format
        self.include_csv_depth = include_csv_depth
        self.snapshot_count = 0
        self.snapshots_buffer: List[OrderbookSnapshot] = []
        
        # Generate session name if not provided
        if session_name is None:
            session_name = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.session_name = session_name
    
    async def record_snapshot(self, snapshot: OrderbookSnapshot):
        """
        Record a snapshot to consolidated file (can be used as callback).
        
        Args:
            snapshot: OrderbookSnapshot to record
        """
        # Add to buffer for batch writing
        self.snapshots_buffer.append(snapshot)
        self.snapshot_count += 1
        
        # Write to JSONL immediately (append mode)
        if self.format in ['jsonl', 'both']:
            self._write_jsonl_snapshot(snapshot)
        
        # Periodic status update
        if self.snapshot_count % 100 == 0:
            print(f"Recorded {self.snapshot_count} snapshots")
    
    def _write_jsonl_snapshot(self, snapshot: OrderbookSnapshot):
        """Write a single snapshot to consolidated JSONL file."""
        filename = f"btc_futures_{self.session_name}.jsonl"
        filepath = self.data_store.jsonl_path / filename
        
        data = snapshot.to_dict()
        data['timestamp'] = snapshot.timestamp.isoformat()
        
        with filepath.open('a') as f:
            json.dump(data, f)
            f.write('\n')
    
    def flush_parquet(self):
        """Flush buffered snapshots to consolidated parquet file."""
        if not self.snapshots_buffer:
            return
        
        if self.format not in ['parquet', 'both']:
            return
        
        # Convert all snapshots to records
        records = []
        for snapshot in self.snapshots_buffer:
            record = {
                'timestamp': snapshot.timestamp,
                'symbol': snapshot.symbol,
                'exchange': snapshot.exchange,
                'best_bid': snapshot.best_bid,
                'best_ask': snapshot.best_ask,
                'mid_price': snapshot.mid_price,
                'spread': snapshot.spread,
                'bid_depth': len(snapshot.bids),
                'ask_depth': len(snapshot.asks),
            }
            records.append(record)
        
        # Create DataFrame
        df = pd.DataFrame(records)
        
        # Save to consolidated parquet file
        filename = f"btc_futures_{self.session_name}.parquet"
        filepath = self.data_store.parquet_path / filename
        
        df.to_parquet(filepath, engine='pyarrow', compression='snappy', index=False)
    
    def get_stats(self) -> dict:
        """Get recording statistics."""
        return {
            'total_snapshots': self.snapshot_count,
            'jsonl_files': len(self.data_store.list_files('jsonl')),
            'csv_files': len(self.data_store.list_files('csv')),
            'parquet_files': len(self.data_store.list_files('parquet')),
            'session_name': self.session_name,
        }


# Example usage
if __name__ == "__main__":
    import asyncio
    from .ccxt_collector import CCXTProCollector, StreamConfig
    
    async def main():
        # Create data store
        data_store = OrderbookDataStore("data/raw/orderbooks")
        
        # Create recorder
        recorder = StreamingDataRecorder(data_store, format='both')
        
        # Configure collector with recorder callback
        config = StreamConfig(
            exchange_id='deribit',
            on_orderbook_update=recorder.record_snapshot
        )
        
        collector = CCXTProCollector(config)
        
        try:
            await collector.start()
            await collector.subscribe_futures(['BTC/USD:BTC'])
            
            # Record for 60 seconds
            await asyncio.sleep(60)
            
            # Print stats
            stats = recorder.get_stats()
            print(f"\nRecording Stats:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            
        finally:
            await collector.stop()
    
    asyncio.run(main())

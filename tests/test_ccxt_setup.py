"""
Quick test script to verify CCXT Pro collector setup.

This script checks:
1. CCXT Pro installation
2. Connection to exchange
3. Market data availability
4. Basic streaming functionality
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    dependencies = {
        'ccxt': 'ccxt',
        'ccxt.pro': 'ccxt (pro version)',
        'pandas': 'pandas',
        'asyncio': 'asyncio (built-in)',
    }
    
    missing = []
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - MISSING")
            missing.append(module)
    
    if missing:
        print("\n❌ Missing dependencies detected!")
        print("\nTo install:")
        if 'ccxt.pro' in missing or 'ccxt' in missing:
            print("  pip install ccxt[pro]")
        if 'pandas' in missing:
            print("  pip install pandas")
        return False
    
    print("\n✓ All dependencies installed\n")
    return True


async def test_connection(exchange_id='deribit'):
    """Test connection to exchange."""
    print(f"Testing connection to {exchange_id}...")
    
    try:
        import ccxt.pro as ccxtpro
        
        exchange_class = getattr(ccxtpro, exchange_id)
        exchange = exchange_class({'enableRateLimit': True})
        
        # Load markets
        markets = await exchange.load_markets()
        print(f"  ✓ Connected to {exchange_id}")
        print(f"  ✓ Loaded {len(markets)} markets")
        
        await exchange.close()
        return True
        
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        return False


async def test_market_discovery():
    """Test market discovery functionality."""
    print("Testing market discovery...")
    
    try:
        from src.data.ccxt_collector import CCXTProCollector, StreamConfig
        
        config = StreamConfig(exchange_id='deribit')
        collector = CCXTProCollector(config)
        
        await collector.start()
        
        # Test futures discovery
        futures = collector.get_available_futures()
        print(f"  ✓ Found {len(futures)} futures markets")
        
        btc_futures = collector.get_available_futures(base_currency='BTC')
        print(f"  ✓ Found {len(btc_futures)} BTC futures")
        
        # Test options discovery
        options = collector.get_available_options()
        print(f"  ✓ Found {len(options)} options markets")
        
        btc_calls = collector.get_available_options(base_currency='BTC', option_type='C')
        print(f"  ✓ Found {len(btc_calls)} BTC call options")
        
        await collector.stop()
        return True
        
    except Exception as e:
        print(f"  ✗ Market discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_streaming():
    """Test basic streaming functionality."""
    print("Testing orderbook streaming...")
    
    try:
        from src.data.ccxt_collector import CCXTProCollector, StreamConfig
        
        received_updates = []
        
        async def on_update(orderbook):
            received_updates.append(orderbook)
            if len(received_updates) <= 3:
                print(f"  ✓ Received update #{len(received_updates)}: "
                      f"{orderbook.symbol} @ ${orderbook.mid_price:.2f}")
        
        config = StreamConfig(
            exchange_id='deribit',
            orderbook_limit=5,
            on_orderbook_update=on_update
        )
        
        collector = CCXTProCollector(config)
        await collector.start()
        
        # Subscribe to BTC perpetual
        await collector.subscribe_futures(['BTC/USD:BTC'])
        
        # Wait for a few updates
        print("  Waiting for orderbook updates (10 seconds)...")
        await asyncio.sleep(10)
        
        await collector.stop()
        
        if len(received_updates) > 0:
            print(f"  ✓ Streaming successful! Received {len(received_updates)} updates")
            return True
        else:
            print("  ✗ No updates received")
            return False
        
    except Exception as e:
        print(f"  ✗ Streaming test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("CCXT Pro Collector - Setup Verification")
    print("=" * 60)
    print()
    
    results = []
    
    # Check dependencies
    results.append(('Dependencies', check_dependencies()))
    print()
    
    if not results[0][1]:
        print("⚠️  Please install missing dependencies before continuing")
        return
    
    # Test connection
    results.append(('Connection', await test_connection()))
    print()
    
    # Test market discovery
    results.append(('Market Discovery', await test_market_discovery()))
    print()
    
    # Test streaming
    results.append(('Streaming', await test_streaming()))
    print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20s} {status}")
    
    print()
    
    if all(result[1] for result in results):
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("  1. Check examples/ccxt_streaming_examples.py for usage examples")
        print("  2. Read src/data/README_CCXT_COLLECTOR.md for documentation")
        print("  3. Start building your trading strategies!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")


def main():
    """Entry point."""
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

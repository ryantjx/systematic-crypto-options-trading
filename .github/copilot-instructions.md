# AI Agent Instructions - Systematic Crypto Options Trading

## Project Overview

Quantitative research framework for cryptocurrency derivatives trading. Focus on data infrastructure, volatility modeling, and systematic strategy development.

**Core Objectives:** Build data pipelines → Develop models → Backtest strategies → Manage risk

## Environment & Dependencies

### Package Management: `uv` (Not pip!)
- **Critical:** This project uses `uv` for fast package management
- Setup: Run `python setup.py` to create `.venv` and install dependencies
- Activate: `source .venv/bin/activate`
- Install packages: `uv pip install <package>` (NOT `pip install`)
- CCXT Pro required for WebSocket streaming: `uv pip install ccxt[pro]`

### Key Dependencies
- **Data:** `polars` (preferred), `pandas`, `numpy`, `asyncio`
- **Data Sources:** `ccxt[pro]`, `yfinance`, `ibkr`
- **Statistics:** `statsmodels`, `scipy`
- **Analysis:** `matplotlib`, `seaborn`, `jupyter`
- **ML/DL:** `scikit-learn`, `tensorflow`, `torch`
- **Code Quality:** `black` (line-length=100), `flake8`, `mypy`, `pytest`

## Architecture & Code Organization

### Module Structure (Import from `src/`)
```python
# Always add src/ to path in standalone scripts/notebooks
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # Adjust depth as needed

# Then import framework modules
from src.data.ccxt_collector import CCXTProCollector, StreamConfig
from src.logging import get_logger, setup_logging
from src.utils.plotting import plot_volatility_surface

# Prefer Polars for data manipulation (faster, better type safety)
import polars as pl
import pandas as pd  # Only when Polars doesn't support needed functionality
```

### Core Components
1. **`src/data/`** - Data collection and streaming infrastructure
2. **`src/logging/`** - Centralized logging with color support
3. **`references/`** - Reference implementations (models, strategies, risk)
4. **`examples/`** - Standalone runnable examples with isolated logs/data

### Data Storage Conventions
- **`data/raw/`** - Raw market data from exchanges (gitignored)
- **`data/processed/`** - Cleaned/transformed data (gitignored)
- **`data/results/`** - Backtest outputs, analysis results (gitignored)
- **Examples store locally:** `examples/*/data/` and `examples/*/logs/`
- **Storage formats:** Use `.parquet` for structured/tabular data (NEVER `.csv`), `.json` for unstructured data, `.log` for logs

## Critical Patterns & Workflows

### 1. Async/Await for Data Collection
```python
# Data streaming uses async patterns
async def stream_data():
    # ... async implementation
    pass

asyncio.run(stream_data())
```

### 2. Logging Setup (Required Pattern)
```python
# At top of every script/example
from src.logging import setup_logging, get_logger

setup_logging(
    level="INFO",
    log_file="logs/myfile.log",
    console=True,
    colored=True
)
logger = get_logger(__name__)
```

### 3. Configuration Pattern
- Centralized in `configs/config.py`
- Use dataclasses for type-safe configs
- Never hardcode credentials - use environment variables

## Testing & Validation

### Run Tests
```bash
pytest tests/                          # All tests
pytest tests/test_ccxt_setup.py       # Verify CCXT Pro setup
```

### Code Quality (Use Black formatting)
```bash
black . --line-length 100              # Format code
flake8 src/ tests/                     # Lint
mypy src/ --ignore-missing-imports     # Type check
```

## Development Commands

### Run Examples
```bash
# Must activate venv first
source .venv/bin/activate

# Run examples (check each example's README for usage)
python examples/stream_futures_deribit/stream_futures_deribit.py
```

### Jupyter Notebooks
```bash
jupyter notebook notebooks/00_getting_started.ipynb
# Notebooks auto-add src/ to path in first cell
```

## Data Quality & Processing

### Data Storage Formats
```python
# Prefer Polars for data transformations (faster, type-safe)
import polars as pl

# Good: Using Polars with Parquet for structured data
df = pl.read_parquet("data/orderbooks.parquet")
result = df.filter(pl.col("spread") < MAX_SPREAD).select(["symbol", "mid_price"])
result.write_parquet("data/processed/filtered.parquet")

# Use JSON for unstructured/nested data
import json
with open("data/config.json", "w") as f:
    json.dump(config_dict, f)

# Only use Pandas when necessary (e.g., specific library compatibility)
import pandas as pd
df_pandas = pd.read_parquet("data.parquet")  # Only if required by external library
```

## Project-Specific Guidelines

### File Creation
- **Only create files directly relevant to the task** - Do not create auxiliary files unless explicitly requested
- **Do NOT create new READMEs if one already exists in the directory** - Update existing READMEs instead
- **New collectors/data sources:** Add to `src/data/`
- **New strategies:** Inherit from `references/strategies/base.py` pattern
- **New models:** Follow `references/models/pricing.py` structure (static methods)
- **Standalone examples:** Create under `examples/new_example/` with own logs/data dirs

### Import Style
```python
# Preferred: Explicit imports from framework modules
from src.data.ccxt_collector import CCXTProCollector
from src.logging import get_logger

# Avoid: Star imports, importing entire modules
# ❌ from src.data import *
# ❌ import src
```

### Documentation
- Docstrings: Google style for functions/classes
- Type hints: Required for function signatures
- README per major component (see `src/data/ccxt_collector/README.md`)

## Common Pitfalls

1. **Using `pip` instead of `uv`** - Always use `uv pip` for this project
2. **Using Pandas instead of Polars** - Prefer `polars` for data manipulation (faster, better typed)
3. **Forgetting to activate venv** - Most scripts assume `.venv` is active
4. **Missing `sys.path.insert` in notebooks** - Scripts won't find `src/` modules
5. **Not calling `await collector.start()`** - Initialize async components properly
6. **Blocking the event loop** - Heavy processing in async callbacks breaks streaming

## Reference Files for Patterns

- **Async streaming:** `examples/stream_futures_deribit/stream_futures_deribit.py`
- **Data persistence:** `src/data/ccxt_collector/storage.py`
- **Logging setup:** `src/logging/logger.py`
- **Config structure:** `configs/config.py`
- **Testing pattern:** `tests/test_ccxt_setup.py`
- **Options pricing:** `references/models/pricing.py`
- **Strategy base:** `references/strategies/base.py`

## Quick Start for New Features

1. Activate environment: `source .venv/bin/activate`
2. Check existing patterns in `src/` and `examples/`
3. Add code to appropriate module in `src/`
4. Test with pytest or create example in `examples/`
5. Format with `black` before committing
6. Update relevant README if adding major functionality

## Current Development Status

- ✅ Data infrastructure (CCXT Pro WebSocket streaming)
- ✅ Centralized logging system
- ✅ Example futures streaming with storage
- 🚧 Volatility surface modeling (in progress)
- 🚧 Strategy backtesting framework (planned)
- 🚧 Risk management modules (planned)

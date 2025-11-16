"""
Volatility-based trading strategies.
"""

import pandas as pd
import numpy as np
from typing import List
from .base import BaseStrategy, Signal
from datetime import datetime


class VolatilityArbitrage(BaseStrategy):
    """
    Volatility arbitrage strategy.
    
    Trades options when realized volatility deviates from implied volatility.
    """
    
    def __init__(
        self,
        lookback_window: int = 30,
        entry_threshold: float = 0.2,
        exit_threshold: float = 0.05
    ):
        super().__init__("Volatility Arbitrage")
        self.lookback_window = lookback_window
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        
    def calculate_realized_vol(self, returns: pd.Series) -> float:
        """Calculate realized volatility from returns."""
        return returns.std() * np.sqrt(252)  # Annualized
    
    def generate_signals(self, market_data: pd.DataFrame) -> List[Signal]:
        """
        Generate signals based on IV vs RV spread.
        
        Buy options when IV < RV (vol underpriced)
        Sell options when IV > RV (vol overpriced)
        """
        signals = []
        
        # Calculate realized volatility
        returns = market_data['close'].pct_change()
        rv = self.calculate_realized_vol(returns.tail(self.lookback_window))
        
        # Compare with implied volatility for each option
        for _, row in market_data.iterrows():
            if pd.isna(row.get('implied_vol')):
                continue
                
            iv = row['implied_vol']
            spread = (iv - rv) / rv  # Normalized spread
            
            if spread < -self.entry_threshold:
                # IV is low relative to RV - buy volatility
                signals.append(Signal(
                    timestamp=datetime.now(),
                    action="buy",
                    symbol=row['symbol'],
                    option_type=row['option_type'],
                    strike=row['strike'],
                    expiry=row['expiry'],
                    quantity=1.0,
                    confidence=min(abs(spread), 1.0),
                    reason=f"IV ({iv:.2%}) < RV ({rv:.2%})"
                ))
            elif spread > self.entry_threshold:
                # IV is high relative to RV - sell volatility
                signals.append(Signal(
                    timestamp=datetime.now(),
                    action="sell",
                    symbol=row['symbol'],
                    option_type=row['option_type'],
                    strike=row['strike'],
                    expiry=row['expiry'],
                    quantity=1.0,
                    confidence=min(abs(spread), 1.0),
                    reason=f"IV ({iv:.2%}) > RV ({rv:.2%})"
                ))
        
        return signals
    
    def calculate_position_size(self, signal: Signal, portfolio_value: float) -> float:
        """Size positions based on confidence and portfolio value."""
        max_position_value = portfolio_value * 0.05  # 5% max per position
        base_size = signal.confidence * 10  # Scale by confidence
        return min(base_size, max_position_value / 100)  # Assuming $100 per contract


class StrangleStrategy(BaseStrategy):
    """
    Long/Short Strangle strategy.
    
    Profits from large moves (long) or range-bound markets (short).
    """
    
    def __init__(self, delta_target: float = 0.25, direction: str = "long"):
        super().__init__(f"{direction.title()} Strangle")
        self.delta_target = delta_target
        self.direction = direction
        
    def generate_signals(self, market_data: pd.DataFrame) -> List[Signal]:
        """
        Generate strangle signals.
        
        Construct strangle with puts and calls at target delta.
        """
        signals = []
        # TODO: Implement strangle construction logic
        return signals
    
    def calculate_position_size(self, signal: Signal, portfolio_value: float) -> float:
        """Calculate position size."""
        return portfolio_value * 0.1 / 100  # 10% of portfolio

"""
Position limits and risk checks.
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class RiskLimits:
    """Define risk limits for trading."""
    max_portfolio_delta: float = 1000.0
    max_portfolio_vega: float = 5000.0
    max_portfolio_gamma: float = 100.0
    max_position_size: float = 0.05  # 5% of portfolio
    max_single_option_notional: float = 50000.0
    max_leverage: float = 2.0
    min_liquidity_score: float = 0.3


class RiskChecker:
    """Check trades against risk limits."""
    
    def __init__(self, limits: RiskLimits):
        self.limits = limits
        
    def check_trade(
        self,
        current_portfolio: Dict,
        proposed_trade: Dict
    ) -> tuple[bool, Optional[str]]:
        """
        Check if proposed trade violates risk limits.
        
        Args:
            current_portfolio: Current portfolio state
            proposed_trade: Proposed trade details
            
        Returns:
            (approved, reason) - True if trade passes all checks
        """
        # Check delta limit
        new_delta = current_portfolio.get('delta', 0) + proposed_trade.get('delta', 0)
        if abs(new_delta) > self.limits.max_portfolio_delta:
            return False, f"Delta limit exceeded: {new_delta} > {self.limits.max_portfolio_delta}"
        
        # Check vega limit
        new_vega = current_portfolio.get('vega', 0) + proposed_trade.get('vega', 0)
        if abs(new_vega) > self.limits.max_portfolio_vega:
            return False, f"Vega limit exceeded: {new_vega} > {self.limits.max_portfolio_vega}"
        
        # Check position size
        position_value = proposed_trade.get('notional', 0)
        portfolio_value = current_portfolio.get('total_value', 1)
        
        if position_value / portfolio_value > self.limits.max_position_size:
            return False, "Position size too large relative to portfolio"
        
        # Check single option notional
        if position_value > self.limits.max_single_option_notional:
            return False, f"Single option notional too large: ${position_value}"
        
        # All checks passed
        return True, None
    
    def get_max_allowable_size(
        self,
        current_portfolio: Dict,
        trade_greeks: Dict
    ) -> float:
        """
        Calculate maximum allowable trade size given current portfolio.
        
        Returns:
            Maximum number of contracts
        """
        max_size = float('inf')
        
        # Delta constraint
        if trade_greeks.get('delta', 0) != 0:
            delta_room = self.limits.max_portfolio_delta - abs(current_portfolio.get('delta', 0))
            max_size = min(max_size, delta_room / abs(trade_greeks['delta']))
        
        # Vega constraint
        if trade_greeks.get('vega', 0) != 0:
            vega_room = self.limits.max_portfolio_vega - abs(current_portfolio.get('vega', 0))
            max_size = min(max_size, vega_room / abs(trade_greeks['vega']))
        
        return max(0, max_size)

"""
Risk metrics and calculations.
"""

import numpy as np
import pandas as pd
from typing import Dict, List


class RiskMetrics:
    """Calculate various risk metrics for portfolio analysis."""
    
    @staticmethod
    def value_at_risk(returns: pd.Series, confidence: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR).
        
        Args:
            returns: Series of portfolio returns
            confidence: Confidence level (e.g., 0.95 for 95% VaR)
            
        Returns:
            VaR value (positive number representing potential loss)
        """
        return -np.percentile(returns, (1 - confidence) * 100)
    
    @staticmethod
    def conditional_var(returns: pd.Series, confidence: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR / Expected Shortfall).
        
        Average loss beyond VaR threshold.
        """
        var = RiskMetrics.value_at_risk(returns, confidence)
        return -returns[returns <= -var].mean()
    
    @staticmethod
    def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Sharpe ratio
        """
        excess_returns = returns - risk_free_rate / 252  # Daily rf rate
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    
    @staticmethod
    def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sortino ratio (downside deviation).
        
        Like Sharpe but only penalizes downside volatility.
        """
        excess_returns = returns - risk_free_rate / 252
        downside_std = returns[returns < 0].std()
        
        if downside_std == 0:
            return np.inf
        
        return np.sqrt(252) * excess_returns.mean() / downside_std
    
    @staticmethod
    def max_drawdown(cumulative_returns: pd.Series) -> Dict[str, float]:
        """
        Calculate maximum drawdown.
        
        Returns:
            Dictionary with max_drawdown, peak, and trough dates
        """
        cummax = cumulative_returns.cummax()
        drawdown = (cumulative_returns - cummax) / cummax
        
        max_dd = drawdown.min()
        max_dd_idx = drawdown.idxmin()
        
        # Find peak before max drawdown
        peak_idx = cumulative_returns[:max_dd_idx].idxmax()
        
        return {
            'max_drawdown': max_dd,
            'peak_date': peak_idx,
            'trough_date': max_dd_idx
        }
    
    @staticmethod
    def calmar_ratio(returns: pd.Series, years: float = 1.0) -> float:
        """
        Calculate Calmar ratio (return / max drawdown).
        
        Args:
            returns: Series of returns
            years: Number of years in the period
        """
        cumulative = (1 + returns).cumprod()
        annual_return = (cumulative.iloc[-1] ** (1/years)) - 1
        max_dd = abs(RiskMetrics.max_drawdown(cumulative)['max_drawdown'])
        
        if max_dd == 0:
            return np.inf
        
        return annual_return / max_dd

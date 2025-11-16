"""
Options Greeks calculations.
"""

import numpy as np
from scipy.stats import norm
from typing import Dict


class GreeksCalculator:
    """Calculate option Greeks for risk management and hedging."""
    
    @staticmethod
    def delta(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> float:
        """
        Calculate Delta (∂V/∂S).
        
        Rate of change of option value with respect to underlying price.
        """
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        
        if option_type.lower() == "call":
            return norm.cdf(d1)
        else:  # put
            return norm.cdf(d1) - 1
    
    @staticmethod
    def gamma(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """
        Calculate Gamma (∂²V/∂S²).
        
        Rate of change of delta with respect to underlying price.
        """
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        return norm.pdf(d1) / (S * sigma * np.sqrt(T))
    
    @staticmethod
    def vega(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """
        Calculate Vega (∂V/∂σ).
        
        Sensitivity to volatility (returns vega per 1% change in vol).
        """
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        return S * norm.pdf(d1) * np.sqrt(T) / 100
    
    @staticmethod
    def theta(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> float:
        """
        Calculate Theta (∂V/∂t).
        
        Time decay - change in option value per day.
        """
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type.lower() == "call":
            theta = (
                -S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                - r * K * np.exp(-r * T) * norm.cdf(d2)
            )
        else:  # put
            theta = (
                -S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                + r * K * np.exp(-r * T) * norm.cdf(-d2)
            )
        
        return theta / 365  # Per day
    
    @staticmethod
    def rho(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> float:
        """
        Calculate Rho (∂V/∂r).
        
        Sensitivity to interest rate (per 1% change).
        """
        d2 = (np.log(S / K) + (r - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        
        if option_type.lower() == "call":
            return K * T * np.exp(-r * T) * norm.cdf(d2) / 100
        else:  # put
            return -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100
    
    @staticmethod
    def all_greeks(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> Dict[str, float]:
        """
        Calculate all Greeks at once.
        
        Returns:
            Dictionary with delta, gamma, vega, theta, rho
        """
        return {
            'delta': GreeksCalculator.delta(S, K, T, r, sigma, option_type),
            'gamma': GreeksCalculator.gamma(S, K, T, r, sigma),
            'vega': GreeksCalculator.vega(S, K, T, r, sigma),
            'theta': GreeksCalculator.theta(S, K, T, r, sigma, option_type),
            'rho': GreeksCalculator.rho(S, K, T, r, sigma, option_type)
        }

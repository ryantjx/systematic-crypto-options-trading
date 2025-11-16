"""
Options pricing models.
"""

import numpy as np
from scipy.stats import norm
from typing import Union


class BlackScholes:
    """
    Black-Scholes option pricing model.
    
    Adapted for cryptocurrency options with continuous trading.
    """
    
    @staticmethod
    def price(
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str = "call"
    ) -> float:
        """
        Calculate Black-Scholes option price.
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiry (years)
            r: Risk-free rate (or funding rate for crypto)
            sigma: Volatility (annualized)
            option_type: "call" or "put"
            
        Returns:
            Option price
        """
        if T <= 0:
            return max(S - K, 0) if option_type == "call" else max(K - S, 0)
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type.lower() == "call":
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        elif option_type.lower() == "put":
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        else:
            raise ValueError("option_type must be 'call' or 'put'")
        
        return price
    
    @staticmethod
    def implied_volatility(
        price: float,
        S: float,
        K: float,
        T: float,
        r: float,
        option_type: str = "call",
        max_iterations: int = 100,
        tolerance: float = 1e-6
    ) -> float:
        """
        Calculate implied volatility using Newton-Raphson method.
        
        Args:
            price: Observed option price
            S: Spot price
            K: Strike price
            T: Time to expiry (years)
            r: Risk-free rate
            option_type: "call" or "put"
            max_iterations: Maximum iterations for convergence
            tolerance: Convergence tolerance
            
        Returns:
            Implied volatility
        """
        # Initial guess using Brenner-Subrahmanyam approximation
        sigma = np.sqrt(2 * np.pi / T) * (price / S)
        
        for i in range(max_iterations):
            price_est = BlackScholes.price(S, K, T, r, sigma, option_type)
            vega = BlackScholes.vega(S, K, T, r, sigma)
            
            diff = price_est - price
            
            if abs(diff) < tolerance:
                return sigma
            
            if vega < 1e-10:
                break
            
            sigma = sigma - diff / vega
            
            # Ensure sigma stays positive
            sigma = max(sigma, 1e-6)
        
        return sigma
    
    @staticmethod
    def vega(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate vega (sensitivity to volatility)."""
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        return S * norm.pdf(d1) * np.sqrt(T)

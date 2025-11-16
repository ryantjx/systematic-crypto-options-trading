"""
Volatility surface modeling and construction.
"""

import numpy as np
import pandas as pd
from scipy.interpolate import griddata, RBFInterpolator
from typing import Tuple, Optional


class VolatilitySurface:
    """
    Construct and manage implied volatility surfaces.
    """
    
    def __init__(self):
        self.surface_data = None
        self.interpolator = None
        
    def fit(
        self,
        strikes: np.ndarray,
        expiries: np.ndarray,
        ivs: np.ndarray,
        method: str = "rbf"
    ) -> None:
        """
        Fit volatility surface to observed IVs.
        
        Args:
            strikes: Array of strike prices
            expiries: Array of time to expiries (years)
            ivs: Array of implied volatilities
            method: Interpolation method ("rbf", "linear", "cubic")
        """
        self.surface_data = pd.DataFrame({
            'strike': strikes,
            'expiry': expiries,
            'iv': ivs
        })
        
        points = np.column_stack([strikes, expiries])
        
        if method == "rbf":
            self.interpolator = RBFInterpolator(points, ivs, kernel='thin_plate_spline')
        else:
            self.interpolator = lambda x: griddata(
                points, ivs, x, method=method, fill_value=np.nan
            )
    
    def get_iv(self, strike: float, expiry: float) -> float:
        """
        Get implied volatility for a given strike and expiry.
        
        Args:
            strike: Strike price
            expiry: Time to expiry (years)
            
        Returns:
            Implied volatility
        """
        if self.interpolator is None:
            raise ValueError("Surface not fitted. Call fit() first.")
        
        point = np.array([[strike, expiry]])
        return float(self.interpolator(point))
    
    def get_atm_vol(self, spot: float, expiry: float) -> float:
        """Get at-the-money volatility for given expiry."""
        return self.get_iv(spot, expiry)
    
    def get_skew(self, spot: float, expiry: float, delta_k: float = 0.1) -> float:
        """
        Calculate volatility skew.
        
        Args:
            spot: Current spot price
            expiry: Time to expiry
            delta_k: Percentage distance from ATM for skew calculation
            
        Returns:
            Skew measure (put vol - call vol) / ATM vol
        """
        atm_vol = self.get_iv(spot, expiry)
        put_strike = spot * (1 - delta_k)
        call_strike = spot * (1 + delta_k)
        
        put_vol = self.get_iv(put_strike, expiry)
        call_vol = self.get_iv(call_strike, expiry)
        
        return (put_vol - call_vol) / atm_vol


class SVIModel:
    """
    Stochastic Volatility Inspired (SVI) parameterization.
    
    Models implied variance as a function of log-moneyness:
    w(k) = a + b * (ρ * (k - m) + sqrt((k - m)^2 + σ^2))
    """
    
    def __init__(self):
        self.params = None
        
    def fit(self, log_moneyness: np.ndarray, total_variance: np.ndarray):
        """
        Fit SVI parameters to market data.
        
        Args:
            log_moneyness: ln(K/S) array
            total_variance: σ^2 * T array
        """
        # TODO: Implement parameter calibration
        # This requires non-linear optimization with constraints
        raise NotImplementedError("SVI calibration pending")
    
    def predict(self, log_moneyness: np.ndarray) -> np.ndarray:
        """Predict total variance for given log-moneyness."""
        if self.params is None:
            raise ValueError("Model not fitted")
        
        a, b, rho, m, sigma = self.params
        k = log_moneyness
        
        return a + b * (rho * (k - m) + np.sqrt((k - m)**2 + sigma**2))

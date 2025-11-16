"""
Mathematical utility functions.
"""

import numpy as np
from typing import Union, List


def annualized_volatility(returns: np.ndarray, periods_per_year: int = 252) -> float:
    """
    Calculate annualized volatility from returns.
    
    Args:
        returns: Array of returns
        periods_per_year: Trading periods per year (252 for daily, 8760 for hourly)
    
    Returns:
        Annualized volatility
    """
    return np.std(returns) * np.sqrt(periods_per_year)


def log_returns(prices: np.ndarray) -> np.ndarray:
    """Calculate log returns from price series."""
    return np.diff(np.log(prices))


def simple_returns(prices: np.ndarray) -> np.ndarray:
    """Calculate simple returns from price series."""
    return np.diff(prices) / prices[:-1]


def rolling_window(data: np.ndarray, window: int) -> np.ndarray:
    """
    Create rolling windows from array.
    
    Args:
        data: Input array
        window: Window size
        
    Returns:
        2D array where each row is a window
    """
    shape = data.shape[:-1] + (data.shape[-1] - window + 1, window)
    strides = data.strides + (data.strides[-1],)
    return np.lib.stride_tricks.as_strided(data, shape=shape, strides=strides)


def normalize(data: Union[np.ndarray, List], method: str = 'zscore') -> np.ndarray:
    """
    Normalize data.
    
    Args:
        data: Input data
        method: 'zscore' or 'minmax'
        
    Returns:
        Normalized data
    """
    data = np.array(data)
    
    if method == 'zscore':
        return (data - np.mean(data)) / np.std(data)
    elif method == 'minmax':
        return (data - np.min(data)) / (np.max(data) - np.min(data))
    else:
        raise ValueError(f"Unknown normalization method: {method}")


def weighted_average(values: np.ndarray, weights: np.ndarray) -> float:
    """Calculate weighted average."""
    return np.average(values, weights=weights)

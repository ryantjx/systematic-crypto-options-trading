"""
Plotting and visualization utilities.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
from typing import Optional, Tuple


def plot_volatility_surface(
    strikes: np.ndarray,
    expiries: np.ndarray,
    ivs: np.ndarray,
    spot: Optional[float] = None,
    figsize: Tuple[int, int] = (12, 8)
) -> plt.Figure:
    """
    Plot 3D volatility surface.
    
    Args:
        strikes: Array of strike prices
        expiries: Array of times to expiry
        ivs: Array of implied volatilities
        spot: Current spot price (for reference)
        figsize: Figure size
        
    Returns:
        Matplotlib figure
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    
    # Create meshgrid if not already
    if strikes.ndim == 1:
        K, T = np.meshgrid(strikes, expiries)
        IV = ivs.reshape(len(expiries), len(strikes))
    else:
        K, T, IV = strikes, expiries, ivs
    
    surf = ax.plot_surface(K, T, IV, cmap='viridis', alpha=0.8)
    
    ax.set_xlabel('Strike')
    ax.set_ylabel('Time to Expiry (years)')
    ax.set_zlabel('Implied Volatility')
    ax.set_title('Implied Volatility Surface')
    
    if spot is not None:
        ax.plot([spot, spot], [T.min(), T.max()], [IV.min(), IV.max()],
                'r--', linewidth=2, label=f'Spot: ${spot:.0f}')
    
    fig.colorbar(surf, ax=ax, shrink=0.5)
    
    return fig


def plot_volatility_smile(
    strikes: np.ndarray,
    ivs: np.ndarray,
    spot: float,
    expiry: float,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Plot volatility smile for a single expiry.
    
    Args:
        strikes: Strike prices
        ivs: Implied volatilities
        spot: Current spot price
        expiry: Time to expiry (for title)
        figsize: Figure size
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot smile
    ax.plot(strikes, ivs, 'b-', linewidth=2)
    ax.scatter(strikes, ivs, c='blue', s=50, alpha=0.6)
    
    # Mark ATM
    ax.axvline(spot, color='red', linestyle='--', alpha=0.5, label='ATM')
    
    ax.set_xlabel('Strike Price')
    ax.set_ylabel('Implied Volatility')
    ax.set_title(f'Volatility Smile (T = {expiry:.2f} years)')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    return fig


def plot_pnl_distribution(
    pnl: pd.Series,
    bins: int = 50,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Plot P&L distribution.
    
    Args:
        pnl: Series of P&L values
        bins: Number of histogram bins
        figsize: Figure size
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Histogram
    ax1.hist(pnl, bins=bins, alpha=0.7, edgecolor='black')
    ax1.axvline(0, color='red', linestyle='--', linewidth=2)
    ax1.axvline(pnl.mean(), color='green', linestyle='--', linewidth=2, label='Mean')
    ax1.set_xlabel('P&L')
    ax1.set_ylabel('Frequency')
    ax1.set_title('P&L Distribution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Cumulative P&L
    cumulative_pnl = pnl.cumsum()
    ax2.plot(cumulative_pnl, linewidth=2)
    ax2.axhline(0, color='red', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Trade Number')
    ax2.set_ylabel('Cumulative P&L')
    ax2.set_title('Cumulative P&L')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_greeks_profile(
    spot_range: np.ndarray,
    greeks: dict,
    figsize: Tuple[int, int] = (14, 10)
) -> plt.Figure:
    """
    Plot Greeks profiles across spot price range.
    
    Args:
        spot_range: Array of spot prices
        greeks: Dictionary with 'delta', 'gamma', 'vega', 'theta'
        figsize: Figure size
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    greek_names = ['delta', 'gamma', 'vega', 'theta']
    
    for ax, name in zip(axes.flat, greek_names):
        if name in greeks:
            ax.plot(spot_range, greeks[name], linewidth=2)
            ax.axhline(0, color='red', linestyle='--', alpha=0.5)
            ax.set_xlabel('Spot Price')
            ax.set_ylabel(name.capitalize())
            ax.set_title(f'{name.capitalize()} Profile')
            ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

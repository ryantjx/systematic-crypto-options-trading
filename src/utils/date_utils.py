"""
Date and time utility functions for options trading.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List


def business_days_between(start: datetime, end: datetime) -> int:
    """
    Calculate business days between two dates.
    
    Note: Crypto markets trade 24/7, but this is useful for comparing
    to traditional markets.
    """
    return len(pd.bdate_range(start, end)) - 1


def calendar_days_between(start: datetime, end: datetime) -> int:
    """Calculate calendar days between dates."""
    return (end - start).days


def years_to_expiry(expiry: datetime, from_date: datetime = None) -> float:
    """
    Calculate time to expiry in years.
    
    Args:
        expiry: Expiration datetime
        from_date: Reference date (defaults to now)
        
    Returns:
        Years to expiry (365.25 day year)
    """
    if from_date is None:
        from_date = datetime.now()
    
    days = (expiry - from_date).total_seconds() / 86400
    return days / 365.25


def get_expiry_dates(
    start: datetime,
    end: datetime,
    frequency: str = 'monthly'
) -> List[datetime]:
    """
    Generate list of option expiry dates.
    
    Args:
        start: Start date
        end: End date
        frequency: 'weekly', 'monthly', or 'quarterly'
        
    Returns:
        List of expiry dates
    """
    if frequency == 'weekly':
        # Fridays (common for crypto options)
        dates = pd.date_range(start, end, freq='W-FRI')
    elif frequency == 'monthly':
        # Last Friday of month
        dates = pd.date_range(start, end, freq='W-FRI')
        dates = dates[dates.to_series().dt.is_month_end]
    elif frequency == 'quarterly':
        # Quarterly expirations
        dates = pd.date_range(start, end, freq='Q')
    else:
        raise ValueError(f"Unknown frequency: {frequency}")
    
    return [d.to_pydatetime() for d in dates]


def is_trading_hours() -> bool:
    """
    Check if current time is within trading hours.
    
    For crypto: Always True (24/7 markets)
    """
    return True


def next_expiry(from_date: datetime = None, days_ahead: int = 7) -> datetime:
    """Get next option expiry date."""
    if from_date is None:
        from_date = datetime.now()
    
    # Find next Friday (common expiry day)
    days_until_friday = (4 - from_date.weekday()) % 7
    if days_until_friday < days_ahead:
        days_until_friday += 7
    
    return from_date + timedelta(days=days_until_friday)

"""
Technical Indicators
----------------------
Pure, deterministic indicator calculations.
All functions accept and return pandas Series to keep them composable.
"""

import pandas as pd
import numpy as np


def ema(series: pd.Series, period: int) -> pd.Series:
    """
    Exponential Moving Average.

    Args:
        series: Price series (usually Close)
        period: EMA look-back period

    Returns:
        pd.Series of EMA values
    """
    return series.ewm(span=period, adjust=False).mean()


def atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int
) -> pd.Series:
    """
    Average True Range (Wilder / EMA-smoothed).

    True Range = max(high-low, |high-prev_close|, |low-prev_close|)
    ATR        = EMA(True Range, period)

    Args:
        high:   High price series
        low:    Low price series
        close:  Close price series
        period: ATR look-back period

    Returns:
        pd.Series of ATR values
    """
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low  - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    # Wilder smoothing ≈ EMA with span = period
    return tr.ewm(span=period, adjust=False).mean()


def highest(series: pd.Series, period: int) -> pd.Series:
    """Rolling highest value over `period` bars."""
    return series.rolling(period, min_periods=1).max()


def lowest(series: pd.Series, period: int) -> pd.Series:
    ""Rolling lowest value over `period` bars."""
    return series.rolling(period, min_periods=1).min()

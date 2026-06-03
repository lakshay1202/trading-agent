"""
EMA Crossover Strategy
------------------------
Signal logic:
  - BUY  (+1) when fast EMA crosses ABOVE slow EMA
  - SELL (-1) when fast EMA crosses BELOW slow EMA
  - HOLD  (0) otherwise

Long-only: sell signal closes any open long; no short entries.
"""

import pandas as pd
from strategies.indicators import ema


def generate_signals(
    df: pd.DataFrame,
    fast_period: int = 9,
    slow_period: int = 21,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Generate EMA Crossover entry / exit signals.

    Args:
        df:          OHLCV DataFrame (must contain 'Close' column)
        fast_period: Look-back for the fast EMA (e.g. 9)
        slow_period: Look-back for the slow EMA (e.g. 21)

    Returns:
        (signals, fast_ema, slow_ema)
        signals:  pd.Series[int] — 1=buy, -1=sell, 0=hold
        fast_ema: pd.Series[float]
        slow_ema: pd.Series[float]

    Raises:
        ValueError: If fast_period >= slow_period or df is too short.
    """
    if fast_period >= slow_period:
        raise ValueError(
            f"fast_period ({fast_period}) must be less than slow_period ({slow_period})."
        )
    if len(df) < slow_period:
        raise ValueError(
            f"DataFrame has only {len(df)} rows; need at least {slow_period} for slow EMA."
        )

    fast_ema = ema(df['Close'], fast_period)
    slow_ema = ema(df['Close'], slow_period)

    signals = pd.Series(0, index=df.index, name='signal', dtype=int)

    # Bullish crossover: fast crosses above slow
    cross_up   = (fast_ema > slow_ema) & (fast_ema.shift(1) <= slow_ema.shift(1))
    # Bearish crossover: fast crosses below slow
    cross_down = (fast_ema < slow_ema) & (fast_ema.shift(1) >= slow_ema.shift(1))

    signals[cross_up]   =  1
    signals[cross_down] = -1

    return signals, fast_ema, slow_ema

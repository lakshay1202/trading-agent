"""
Chandelier Exit Strategy
--------------------------
Signal logic (long-only):
  - BUY  (+1) when trend flips from bearish → bullish
  - SELL (-1) when trend flips from bullish → bearish
  - HOLD  (0) otherwise

Chandelier Exit Long = Highest High(period) − ATR(period) × multiplier

Direction rule:
  - If close > previous Chandelier Exit Long  → bullish  (+1)
  - If close < current  Chandelier Exit Long  → bearish  (-1)
  - Otherwise carry forward previous direction
"""

import numpy as np
import pandas as pd
from strategies.indicators import atr, highest


def generate_signals(
    df: pd.DataFrame,
    atr_period: int = 22,
    atr_multiplier: float = 3.0,
) -> tuple[pd.Series, pd.Series]:
    """
    Generate Chandelier Exit entry / exit signals.

    Args:
        df:             OHLCV DataFrame (must contain High, Low, Close)
        atr_period:     ATR look-back period (default 22)
        atr_multiplier: ATR multiplier for the stop distance (default 3.0)

    Returns:
        (signals, chandelier_long)
        signals:          pd.Series[int]   — 1=buy, -1=sell, 0=hold
        chandelier_long:  pd.Series[float] — the trailing stop line
    """
    if len(df) < atr_period:
        raise ValueError(
            f"DataFrame has only {len(df)} rows; "
            f"need at least {atr_period} for Chandelier Exit."
        )

    atr_vals       = atr(df['High'], df['Low'], df['Close'], atr_period)
    highest_high   = highest(df['High'], atr_period)
    chandelier_long = highest_high - atr_vals * atr_multiplier

    closes    = df['Close'].values
    ce_long   = chandelier_long.values
    n         = len(df)
    direction = np.ones(n, dtype=np.int8)   # start assuming bullish

    # Vectorised-friendly loop using numpy (fast enough for daily / hourly bars)
    for i in range(1, n):
        if closes[i] > ce_long[i - 1]:
            direction[i] = 1
        elif closes[i] < ce_long[i]:
            direction[i] = -1
        else:
            direction[i] = direction[i - 1]

    direction_s = pd.Series(direction, index=df.index)
    prev_dir    = direction_s.shift(1)

    signals = pd.Series(0, index=df.index, name='signal', dtype=int)
    signals[(direction_s == 1) & (prev_dir != 1)]  =  1   # flip to bullish → buy
    signals[(direction_s == -1) & (prev_dir != -1)] = -1  # flip to bearish → sell

    return signals, chandelier_long

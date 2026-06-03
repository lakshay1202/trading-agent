"""
yFinance OHLCV Data Loader
---------------------------
Fetches daily OHLCV data for Indian equities (NSE/BSE) via yfinance.
Only daily ('1d') timeframe is supported for Indian equities due to
data availability constraints.
"""

import yfinance as yf
import pandas as pd


INDIAN_SUFFIX = ['.NS', '.BO']  # NSE and BSE suffixes


def _ensure_suffix(symbol: str) -> str:
    """Auto-append .NS if no exchange suffix is present."""
    if not any(symbol.upper().endswith(s) for s in ['.NS', '.BO', '.L', '.AX']):
        return symbol + '.NS'
    return symbol


def fetch_yfinance_ohlcv(
    symbol: str,
    start_date: str,
    end_date: str,
    auto_suffix: bool = True
) -> pd.DataFrame:
    """
    Fetch daily OHLCV data from yfinance.

    Args:
        symbol:      Ticker symbol, e.g. 'RELIANCE.NS', 'TCS.NS', 'INFY.NS'
                     If no suffix is given and auto_suffix=True, '.NS' is appended.
        start_date:  Start date string 'YYYY-MM-DD'
        end_date:    End date string   'YYYY-MM-DD'
        auto_suffix: Auto-append '.NS' if no exchange suffix present.

    Returns:
        pd.DataFrame with DatetimeIndex and columns: Open, High, Low, Close, Volume

    Raises:
        ValueError:  If no data is returned for the symbol/date range.
        RuntimeError: On download errors.
    """
    if auto_suffix:
        symbol = _ensure_suffix(symbol)

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, interval='1d', auto_adjust=True)
    except Exception as e:
        raise RuntimeError(f"Error downloading data for '{symbol}' from yfinance: {e}")

    if df is None or df.empty:
        raise ValueError(
            f"No data returned for '{symbol}' between {start_date} and {end_date}. "
            "Verify the ticker symbol (e.g. 'RELIANCE.NS', 'TCS.NS') and date range."
        )

    # Keep only OHLCV columns
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()

    # Strip timezone info for consistency
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df.index.name = 'timestamp'

    df.sort_index(inplace=True)
    df.dropna(subset=['Open', 'High', 'Low', 'Close'], inplace=True)

    # Ensure numeric dtypes
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

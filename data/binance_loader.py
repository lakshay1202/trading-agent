"""
Binance OHLCV Data Loader
--------------------------
Fetches historical OHLCV data from Binance using the ccxt library.
Supports all timeframes: 1m, 5m, 15m, 1h, 4h, 1d.
"""

import ccxt
import pandas as pd
from datetime import datetime


VALID_TIMEFRAMES = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w']


def fetch_binance_ohlcv(
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str,
    limit_per_request: int = 1000
) -> pd.DataFrame:
    """
    Fetch OHLCV data from Binance via ccxt.

    Args:
        symbol:     Binance symbol, e.g. 'BTC/USDT' or 'BTCUSDT'
        timeframe:  Candle timeframe, e.g. '15m', '1h', '4h', '1d'
        start_date: Start date string 'YYYY-MM-DD'
        end_date:   End date string   'YYYY-MM-DD'

    Returns:
        pd.DataFrame with DatetimeIndex and columns: Open, High, Low, Close, Volume

    Raises:
        ValueError: If symbol or timeframe is invalid, or no data returned.
        RuntimeError: On network or API errors.
    """
    # Normalise symbol — accept both 'BTC/USDT' and 'BTCUSDT'
    if '/' not in symbol:
        # Try to insert the slash before common quote currencies
        for quote in ['USDT', 'BUSD', 'BTC', 'ETH', 'BNB', 'USD']:
            if symbol.endswith(quote):
                symbol = symbol[:-len(quote)] + '/' + quote
                break

    if timeframe not in VALID_TIMEFRAMES:
        raise ValueError(
            f"Invalid timeframe '{timeframe}'. "
            f"Supported: {VALID_TIMEFRAMES}"
        )

    exchange = ccxt.binance({'enableRateLimit': True})

    # Convert date strings to millisecond timestamps
    since_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
    end_ts   = int(datetime.strptime(end_date,   '%Y-%m-%d').timestamp() * 1000)

    all_ohlcv = []
    current_ts = since_ts

    while current_ts < end_ts:
        try:
            batch = exchange.fetch_ohlcv(
                symbol, timeframe, since=current_ts, limit=limit_per_request
            )
        except ccxt.BadSymbol:
            raise ValueError(f"Symbol '{symbol}' not found on Binance.")
        except ccxt.NetworkError as e:
            raise RuntimeError(f"Network error while fetching Binance data: {e}")
        except ccxt.ExchangeError as e:
            raise RuntimeError(f"Binance exchange error: {e}")

        if not batch:
            break

        all_ohlcv.extend(batch)
        last_ts = batch[-1][0]

        # Advance past the last returned candle
        current_ts = last_ts + 1

        # Stop if we've reached the end date
        if last_ts >= end_ts:
            break

        # Avoid infinite loop if exchange returns duplicate final candle
        if len(batch) < limit_per_request:
            break

    if not all_ohlcv:
        raise ValueError(
            f"No data returned for {symbol} [{timeframe}] "
            f"between {start_date} and {end_date}. "
            "Check symbol name and date range."
        )

    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True).dt.tz_localize(None)
    df.set_index('timestamp', inplace=True)

    # Filter to requested window
    df = df[df.index < pd.Timestamp(end_date)]
    df = df[~df.index.duplicated(keep='first')]
    df.sort_index(inplace=True)

    # Ensure numeric dtypes
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(subset=['Open', 'High', 'Low', 'Close'], inplace=True)

    return df

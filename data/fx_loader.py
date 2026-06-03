"""
Forex (FX) Data Loader — Placeholder
--------------------------------------
This module is a placeholder for future Forex data integration.

Planned integrations:
  - OANDA REST API (live + historical, requires API key)
  - Alpha Vantage (free tier, limited history)
  - ccxt (for crypto-pegged FX pairs)

To implement, install the provider SDK and replace the stub below.
"""


def fetch_fx_ohlcv(
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str,
) -> None:
    """
    Placeholder for Forex OHLCV data fetching.

    Args:
        symbol:     FX pair, e.g. 'EUR/USD', 'GBP/JPY'
        timeframe:  Candle timeframe, e.g. '1h', '4h', '1d'
        start_date: Start date string 'YYYY-MM-DD'
        end_date:   End date string   'YYYY-MM-DD'

    Raises:
        NotImplementedError: Always — this module is not yet implemented.
    """
    raise NotImplementedError(
        "Forex data loading is not yet implemented.\n"
        "Planned providers: OANDA API, Alpha Vantage.\n"
        "This module is a placeholder for Phase 2 development."
    )

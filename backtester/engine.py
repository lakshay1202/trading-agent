"""
Backtest Engine
----------------
A deterministic, event-driven backtester.

Execution model:
  - Signals are generated on bar close.
  - Orders execute at the NEXT bar's open price (realistic fill).
  - Commission is applied on trade value (both entry and exit).
  - Slippage is applied as a percentage of execution price.
  - Long-only: 100% of available capital per trade, no leverage.
  - Any open position is closed at the last bar's close.
"""

import pandas as pd
import numpy as np
from typing import Optional


def run_backtest(
    df: pd.DataFrame,
    signals: pd.Series,
    initial_capital: float = 100_000.0,
    commission: float = 0.001,   # 0.1 %
    slippage: float = 0.0005,    # 0.05 %
) -> dict:
    """
    Run a vectorised / event-driven backtest.

    Args:
        df:              OHLCV DataFrame indexed by datetime.
        signals:         Series aligned to df.index with values 1, -1, or 0.
        initial_capital: Starting capital in account currency.
        commission:      Commission rate, e.g. 0.001 = 0.1 %.
        slippage:        Slippage rate, e.g. 0.0005 = 0.05 %.

    Returns:
        dict with keys:
          'equity_curve'    : pd.DataFrame  (index=datetime, columns=['equity','position'])
          'trades'          : pd.DataFrame  (one row per completed round-trip)
          'initial_capital' : float
    """
    opens  = df['Open'].values
    closes = df['Close'].values
    dates  = df.index
    sigs   = signals.reindex(df.index).fillna(0).values

    capital      = initial_capital
    shares       = 0.0
    position     = 0          # 0 = flat, 1 = long
    entry_price  = 0.0
    entry_date   = None
    capital_at_entry = 0.0   # capital committed when entering

    equity_records = []
    trade_records  = []

    n = len(df)

    for i in range(n):
        # ---- Execute signal from PREVIOUS bar at THIS bar's open ----
        if i > 0:
            prev_sig = sigs[i - 1]
        else:
            prev_sig = 0

        exec_open = opens[i]

        if prev_sig == 1 and position == 0:
            # ----- ENTER LONG -----
            exec_price       = exec_open * (1.0 + slippage)
            commission_cost  = capital * commission
            available        = capital - commission_cost
            shares           = available / exec_price
            capital_at_entry = capital          # snapshot before trade
            capital          = 0.0              # fully invested
            entry_price      = exec_price
            entry_date       = dates[i]
            position         = 1

        elif prev_sig == -1 and position == 1:
            # ----- EXIT LONG -----
            exec_price      = exec_open * (1.0 - slippage)
            gross_value     = shares * exec_price
            commission_cost = gross_value * commission
            capital         = gross_value - commission_cost

            pnl = capital - capital_at_entry
            trade_records.append(_make_trade(
                entry_date, dates[i],
                entry_price, exec_price,
                shares, pnl, capital_at_entry
            ))

            shares   = 0.0
            position = 0

        # ---- Mark-to-market equity at this bar's close ----
        if position == 1:
            equity = shares * closes[i]
        else:
            equity = capital

        equity_records.append({'date': dates[i], 'equity': equity, 'position': position})

    # ---- Force-close any open position at last bar's close ----
    if position == 1:
        exec_price      = closes[-1] * (1.0 - slippage)
        gross_value     = shares * exec_price
        commission_cost = gross_value * commission
        final_capital   = gross_value - commission_cost

        pnl = final_capital - capital_at_entry
        trade_records.append(_make_trade(
            entry_date, dates[-1],
            entry_price, exec_price,
            shares, pnl, capital_at_entry
        ))

        # Update last equity record to reflect closed position
        equity_records[-1]['equity']   = final_capital
        equity_records[-1]['position'] = 0

    equity_df = pd.DataFrame(equity_records).set_index('date')
    trades_df = pd.DataFrame(trade_records) if trade_records else pd.DataFrame(
        columns=['entry_date', 'exit_date', 'entry_price', 'exit_price',
                 'shares', 'pnl', 'return_pct', 'capital_risked']
    )

    return {
        'equity_curve':    equity_df,
        'trades':          trades_df,
        'initial_capital': initial_capital,
    }


def _make_trade(
    entry_date, exit_date,
    entry_price: float, exit_price: float,
    shares: float, pnl: float, capital_risked: float
) -> dict:
    return_pct = (exit_price / entry_price - 1.0) * 100.0
    return {
        'entry_date':     entry_date,
        'exit_date':      exit_date,
        'entry_price':    entry_price,
        'exit_price':     exit_price,
        'shares':         shares,
        'pnl':            pnl,
        'return_pct':     return_pct,
        'capital_risked': capital_risked,
    }

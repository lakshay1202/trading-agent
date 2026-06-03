"""
Performance Metrics
--------------------
All calculations are deterministic given the equity curve and trade log.
No AI involvement — pure arithmetic.
"""

import numpy as np
import pandas as pd


def calculate_metrics(
    equity_curve: pd.DataFrame,
    trades: pd.DataFrame,
    initial_capital: float,
    bars_per_year: int = 252,
) -> dict:
    """
    Compute standard backtesting performance metrics.

    Args:
        equity_curve:   DataFrame with a DatetimeIndex and an 'equity' column.
        trades:         DataFrame with columns including 'pnl'.
        initial_capital: Starting capital.
        bars_per_year:  Trading bars per year for annualisation.
                        Daily=252, Hourly=252*6.5≈1638, etc.

    Returns:
        dict with all metric values (float / int).
    """
    equity = equity_curve['equity'].copy()

    # --- Core returns ---
    final_equity  = float(equity.iloc[-1])
    total_return  = (final_equity / initial_capital - 1.0) * 100.0

    # --- CAGR ---
    n_days  = max((equity.index[-1] - equity.index[0]).days, 1)
    n_years = n_days / 365.25
    cagr    = ((final_equity / initial_capital) ** (1.0 / n_years) - 1.0) * 100.0

    # --- Drawdown ---
    rolling_max = equity.cummax()
    dd          = (equity - rolling_max) / rolling_max * 100.0
    max_drawdown = float(dd.min())

    # --- Sharpe ratio (annualised, zero risk-free rate) ---
    pct_returns = equity.pct_change().dropna()
    if pct_returns.std() > 1e-10:
        sharpe = float((pct_returns.mean() / pct_returns.std()) * np.sqrt(bars_per_year))
    else:
        sharpe = 0.0

    # --- Trade-level metrics ---
    if trades.empty or 'pnl' not in trades.columns:
        return _build_result(
            total_return, cagr, max_drawdown, sharpe,
            win_rate=0.0, profit_factor=0.0,
            num_trades=0, final_equity=final_equity,
        )

    winners = trades[trades['pnl'] > 0]
    losers  = trades[trades['pnl'] <= 0]

    win_rate      = len(winners) / len(trades) * 100.0
    gross_profit  = float(winners['pnl'].sum()) if not winners.empty else 0.0
    gross_loss    = float(losers['pnl'].abs().sum()) if not losers.empty else 0.0
    profit_factor = gross_profit / gross_loss if gross_loss > 1e-10 else float('inf')

    avg_win  = float(winners['pnl'].mean()) if not winners.empty else 0.0
    avg_loss = float(losers['pnl'].mean())  if not losers.empty  else 0.0

    return _build_result(
        total_return, cagr, max_drawdown, sharpe,
        win_rate, profit_factor,
        num_trades=len(trades), final_equity=final_equity,
        avg_win=avg_win, avg_loss=avg_loss,
        gross_profit=gross_profit, gross_loss=gross_loss,
    )


def _build_result(
    total_return, cagr, max_drawdown, sharpe,
    win_rate, profit_factor, num_trades, final_equity,
    avg_win=0.0, avg_loss=0.0,
    gross_profit=0.0, gross_loss=0.0,
) -> dict:
    def r(v, d=2):
        return round(float(v), d) if np.isfinite(v) else v

    return {
        'total_return':  r(total_return),
        'cagr':          r(cagr),
        'max_drawdown':  r(max_drawdown),
        'sharpe_ratio':  r(sharpe),
        'win_rate':      r(win_rate),
        'profit_factor': r(profit_factor),
        'num_trades':    int(num_trades),
        'final_equity':  r(final_equity, 0),
        'avg_win':       r(avg_win, 0),
        'avg_loss':      r(avg_loss, 0),
        'gross_profit':  r(gross_profit, 0),
        'gross_loss':    r(gross_loss, 0),
    }

"""
Trade Log Formatter
--------------------
Transforms the raw trades DataFrame into a clean, display-ready table.
"""

import pandas as pd


def format_trade_log(trades: pd.DataFrame) -> pd.DataFrame:
    """
    Format the raw trades DataFrame for display in Streamlit.

    Args:
        trades: Raw trades DataFrame from the backtest engine.

    Returns:
        Clean, display-ready DataFrame.
        Returns empty DataFrame if no trades.
    """
    if trades is None or trades.empty:
        return pd.DataFrame(
            columns=['#', 'Entry Date', 'Exit Date', 'Entry Price',
                     'Exit Price', 'Shares', 'PnL ($)', 'Return (%)', 'Result']
        )

    log = trades.copy()

    # Format dates
    for col in ['entry_date', 'exit_date']:
        if col in log.columns:
            log[col] = pd.to_datetime(log[col]).dt.strftime('%Y-%m-%d %H:%M')

    # Round numerics
    log['entry_price'] = log['entry_price'].round(4)
    log['exit_price']  = log['exit_price'].round(4)
    log['shares']      = log['shares'].round(4)
    log['pnl']         = log['pnl'].round(2)
    log['return_pct']  = log['return_pct'].round(2)

    # Result label
    log['result'] = log['pnl'].apply(lambda x: '✅ Win' if x > 0 else '❌ Loss')

    # Add trade number
    log.insert(0, '#', range(1, len(log) + 1))

    # Rename columns for display
    log = log.rename(columns={
        'entry_date':  'Entry Date',
        'exit_date':   'Exit Date',
        'entry_price': 'Entry Price',
        'exit_price':  'Exit Price',
        'shares':      'Shares',
        'pnl':         'PnL ($)',
        'return_pct':  'Return (%)',
        'result':      'Result',
    })

    display_cols = ['#', 'Entry Date', 'Exit Date', 'Entry Price',
                    'Exit Price', 'Shares', 'PnL ($)', 'Return (%)', 'Result']
    return log[[c for c in display_cols if c in log.columns]]

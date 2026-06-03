"""
AI Backtesting Agent - Streamlit App
"""
import sys
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, os.path.dirname(__file__))

from data.binance_loader import fetch_binance_ohlcv
from data.yfinance_loader import fetch_yfinance_ohlcv
from strategies.ema_crossover import generate_signals as ema_signals
from strategies.chandelier_exit import generate_signals as ce_signals
from backtester.engine import run_backtest
from backtester.metrics import calculate_metrics
from backtester.trade_log import format_trade_log
from agent.strategy_parser import parse_strategy, list_strategies

st.set_page_config(page_title="AI Backtesting Agent", layout="wide")
st.title("AI Backtesting Agent")
st.caption("Backtest deterministic trading strategies on Crypto and Indian Equities.")

with st.sidebar:
    st.header("Configuration")
    asset_class = st.selectbox("Asset Class",
        ["Crypto (Binance)", "Indian Equity (NSE/BSE)", "Forex (Coming Soon)"])

    if asset_class == "Crypto (Binance)":
        symbol = st.text_input("Symbol", value="BTC/USDT",
                               help="e.g. BTC/USDT, ETH/USDT, SOL/USDT")
        timeframe = st.selectbox("Timeframe",
                                 ["1m", "5m", "15m", "1h", "4h", "1d"], index=2)
    elif asset_class == "Indian Equity (NSE/BSE)":
        symbol = st.text_input("Symbol", value="RELIANCE.NS",
                               help="NSE: RELIANCE.NS  BSE: RELIANCE.BO")
        timeframe = "1d"
        st.info("Indian equities support daily timeframe only.")
    else:
        symbol = st.text_input("Symbol", value="EUR/USD")
        timeframe = st.selectbox("Timeframe", ["1h", "4h", "1d"])
        st.warning("Forex module coming in Phase 2.")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("Start", value=pd.Timestamp("2023-01-01"))
    with col_d2:
        end_date = st.date_input("End", value=pd.Timestamp("2024-01-01"))

    if start_date >= end_date:
        st.error("Start date must be before end date.")

    st.markdown("---")
    strategy = st.selectbox("Strategy", list_strategies())

    params = {}
    if strategy == "EMA Crossover":
        params["fast_period"] = st.number_input(
            "Fast EMA Period", min_value=2, max_value=200, value=9, step=1)
        params["slow_period"] = st.number_input(
            "Slow EMA Period", min_value=3, max_value=500, value=21, step=1)
    elif strategy == "Chandelier Exit":
        params["atr_period"] = st.number_input(
            "ATR Period", min_value=5, max_value=100, value=22, step=1)
        params["atr_multiplier"] = st.number_input(
            "ATR Multiplier", min_value=0.5, max_value=10.0,
            value=3.0, step=0.1, format="%.1f")

    st.markdown("---")
    initial_capital = st.number_input(
        "Initial Capital ($)", min_value=1_000, max_value=10_000_000,
        value=100_000, step=1_000)
    commission = st.number_input(
        "Commission (%)", min_value=0.0, max_value=2.0,
        value=0.1, step=0.01, format="%.2f") / 100.0
    slippage = st.number_input(
        "Slippage (%)", min_value=0.0, max_value=2.0,
        value=0.05, step=0.01, format="%.2f") / 100.0

    st.markdown("---")
    run_btn = st.button("Run Backtest", type="primary", use_container_width=True)

if not run_btn:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**Crypto**\nAny Binance pair | Any timeframe\nBTC/USDT, ETH/USDT...")
    with c2:
        st.info("**Indian Equity**\nNSE/BSE daily via yfinance\nRELIANCE.NS | TCS.NS...")
    with c3:
        st.info("**Strategies**\nEMA Crossover\nChandelier Exit\n(Forex coming Phase 2)")
    st.markdown("---")
    st.markdown("""
#### How it works
1. Pick your **asset class**, **symbol**, and **timeframe** in the sidebar.
2. Choose a **strategy** and tune its parameters.
3. Set **capital**, **commission**, and **slippage**.
4. Click **Run Backtest** - results appear instantly.
""")
    st.stop()

if asset_class == "Forex (Coming Soon)":
    st.error("Forex not yet implemented. Select Crypto or Indian Equity.")
    st.stop()

try:
    config = parse_strategy(strategy, params)
except ValueError as e:
    st.error(f"Parameter error: {e}")
    st.stop()

with st.spinner(f"Fetching {symbol} [{timeframe}] data..."):
    try:
        if asset_class == "Crypto (Binance)":
            df = fetch_binance_ohlcv(symbol, timeframe, str(start_date), str(end_date))
        else:
            df = fetch_yfinance_ohlcv(symbol, str(start_date), str(end_date))
    except (ValueError, RuntimeError) as e:
        st.error(f"Data error: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        st.stop()

st.success(f"Loaded {len(df):,} candles for {symbol} "
           f"({df.index[0].date()} to {df.index[-1].date()})")

with st.spinner("Generating signals..."):
    try:
        if strategy == "EMA Crossover":
            signals, fast_ema, slow_ema = ema_signals(df, **config["params"])
            ind = {"fast_ema": fast_ema, "slow_ema": slow_ema}
        elif strategy == "Chandelier Exit":
            signals, chandelier = ce_signals(df, **config["params"])
            ind = {"chandelier": chandelier}
    except ValueError as e:
        st.error(f"Signal error: {e}")
        st.stop()

with st.spinner("Running backtest..."):
    result = run_backtest(df, signals, initial_capital, commission, slippage)
    equity_curve = result["equity_curve"]
    trades = result["trades"]
    metrics = calculate_metrics(equity_curve, trades, initial_capital)

st.markdown("---")
st.subheader("Performance Summary")

r1c1, r1c2, r1c3, r1c4 = st.columns(4)
r1c1.metric("Total Return", f"{metrics['total_return']}%",
            delta=f"{metrics['total_return']}%")
r1c2.metric("CAGR", f"{metrics['cagr']}%")
r1c3.metric("Max Drawdown", f"{metrics['max_drawdown']}%")
r1c4.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']}")

r2c1, r2c2, r2c3, r2c4 = st.columns(4)
r2c1.metric("Win Rate", f"{metrics['win_rate']}%")
r2c2.metric("Profit Factor", f"{metrics['profit_factor']}")
r2c3.metric("No. of Trades", metrics["num_trades"])
r2c4.metric("Final Equity", f"${metrics['final_equity']:,.0f}")

st.markdown("---")
st.subheader("Price Chart & Equity Curve")

fig = make_subplots(
    rows=2, cols=1, shared_xaxes=True,
    row_heights=[0.65, 0.35], vertical_spacing=0.03,
    subplot_titles=("Price with Signals", "Equity Curve"),
)

fig.add_trace(go.Candlestick(
    x=df.index, open=df["Open"], high=df["High"],
    low=df["Low"], close=df["Close"], name="Price",
    increasing_line_color="#26a69a", decreasing_line_color="#ef5350",
), row=1, col=1)

if strategy == "EMA Crossover":
    fig.add_trace(go.Scatter(
        x=df.index, y=ind["fast_ema"],
        name=f"Fast EMA ({config['params']['fast_period']})",
        line=dict(color="#2196f3", width=1.2),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=ind["slow_ema"],
        name=f"Slow EMA ({config['params']['slow_period']})",
        line=dict(color="#ff9800", width=1.2),
    ), row=1, col=1)
elif strategy == "Chandelier Exit":
    fig.add_trace(go.Scatter(
        x=df.index, y=ind["chandelier"],
        name=f"Chandelier Exit (ATR {config['params']['atr_period']})",
        line=dict(color="#e91e63", width=1.2, dash="dot"),
    ), row=1, col=1)

if not trades.empty:
    fig.add_trace(go.Scatter(
        x=trades["entry_date"], y=trades["entry_price"],
        mode="markers", name="Buy",
        marker=dict(symbol="triangle-up", size=10, color="#00e676"),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=trades["exit_date"], y=trades["exit_price"],
        mode="markers", name="Sell",
        marker=dict(symbol="triangle-down", size=10, color="#ff1744"),
    ), row=1, col=1)

eq_color = "#00c853" if metrics["total_return"] >= 0 else "#ff1744"
fig.add_trace(go.Scatter(
    x=equity_curve.index, y=equity_curve["equity"],
    name="Equity", fill="tozeroy",
    line=dict(color=eq_color, width=1.5),
), row=2, col=1)
fig.add_hline(y=initial_capital, line_dash="dash",
              line_color="gray", line_width=1, row=2, col=1)

fig.update_layout(
    height=720, template="plotly_dark",
    xaxis_rangeslider_visible=False,
    margin=dict(l=0, r=0, t=40, b=0),
)
fig.update_yaxes(title_text="Price", row=1, col=1)
fig.update_yaxes(title_text="Equity ($)", row=2, col=1)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Trade Log")

if trades.empty:
    st.info("No trades executed. Try a longer date range or different parameters.")
else:
    trade_log = format_trade_log(trades)
    st.dataframe(trade_log, use_container_width=True, hide_index=True)
    csv = trade_log.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Trade Log (CSV)", csv,
        f"trade_log_{symbol.replace('/', '')}_{strategy.replace(' ', '_')}.csv",
        "text/csv",
    )

st.markdown("---")
st.caption("For educational purposes only. Not financial advice. "
           "Past performance does not guarantee future results.")

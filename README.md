# 📈 AI Backtesting Agent — MVP

A modular Python + Streamlit backtesting platform for:
- **Crypto** — any Binance pair, any timeframe (1m → 1d)
- **Indian Equities** — NSE / BSE via yfinance (daily only)
- **Forex** — placeholder, coming in Phase 2

> ⚙️ The AI does **not** compute backtest results. It only parses and validates
> user inputs, then calls fully deterministic Python functions.

---

## 🚀 Quick Start (local)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**.

---

## 🧪 Test Cases

### Test 1 — BTCUSDT 15m Chandelier Exit

In the sidebar, set:

| Field | Value |
|---|---|
| Asset Class | Crypto (Binance) |
| Symbol | BTC/USDT |
| Timeframe | 15m |
| Start Date | 2023-01-01 |
| End Date | 2024-01-01 |
| Strategy | Chandelier Exit |
| ATR Period | 22 |
| ATR Multiplier | 3.0 |
| Initial Capital | 100,000 |
| Commission | 0.10% |
| Slippage | 0.05% |

Click **🚀 Run Backtest**.

---

### Test 2 — RELIANCE.NS Daily EMA Crossover

| Field | Value |
|---|---|
| Asset Class | Indian Equity (NSE/BSE) |
| Symbol | RELIANCE.NS |
| Timeframe | 1d (auto-locked) |
| Start Date | 2020-01-01 |
| End Date | 2024-01-01 |
| Strategy | EMA Crossover |
| Fast EMA | 9 |
| Slow EMA | 21 |

---

## 📁 Project Structure

```
trading-agent/
│
├── data/
│   ├── binance_loader.py      # Binance OHLCV via ccxt
│   ├── yfinance_loader.py     # Indian equities daily via yfinance
│   └── fx_loader.py           # Forex placeholder
│
├── strategies/
│   ├── indicators.py          # EMA, ATR, Highest, Lowest
│   ├── ema_crossover.py       # Fast/slow EMA crossover signals
│   └── chandelier_exit.py     # ATR-based trend following signals
│
├── backtester/
│   ├── engine.py              # Event-driven backtest engine
│   ├── metrics.py             # Return, CAGR, Drawdown, Sharpe, Win rate …
│   └── trade_log.py           # Trade log formatter
│
├── agent/
│   └── strategy_parser.py     # Input validation (AI boundary)
│
├── app.py                     # Streamlit frontend
├── requirements.txt
└── README.md
```

---

## 📊 Output Metrics

| Metric | Description |
|---|---|
| Total Return | % gain/loss vs. initial capital |
| CAGR | Compound annual growth rate |
| Max Drawdown | Worst peak-to-trough equity decline |
| Sharpe Ratio | Annualised risk-adjusted return (Rf = 0) |
| Win Rate | % of trades that were profitable |
| Profit Factor | Gross profit ÷ gross loss |
| No. of Trades | Total completed round-trips |
| Final Equity | Ending portfolio value |

---

## ☁️ Deployment (Streamlit Community Cloud — Free)

> ⚠️ **Note:** Streamlit apps cannot run on Vercel (which is for serverless/static sites).
> Use **Streamlit Community Cloud** — it's free and purpose-built for this.

1. Push this folder to a **public GitHub repo**.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select your repo, branch, and set **Main file path** to `app.py`.
4. Click **Deploy**. Your app gets a public URL in ~2 minutes.

No environment variables needed for the MVP (Binance public API + yfinance are unauthenticated).

---

## 🔮 What to Add Next

### Phase 2 — AI Natural Language Parsing
- Wire `agent/strategy_parser.py → parse_from_text()` to Claude or OpenAI API
- Users type: *"Backtest ETH/USDT 1h with 12/26 EMA from Jan 2023"*
- The LLM extracts params → passes to `parse_strategy()` → backtest runs

```python
# agent/strategy_parser.py
import anthropic

def parse_from_text(text: str) -> dict:
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=256,
        messages=[{"role": "user", "content": f"Extract backtest params as JSON: {text}"}]
    )
    raw = json.loads(message.content[0].text)
    return parse_strategy(raw['strategy'], raw['params'])
```

### Phase 3 — Additional Features
- **Forex module** via OANDA REST API
- **Multi-position sizing** (fixed %, Kelly criterion, volatility-adjusted)
- **Walk-forward optimisation** (avoid overfitting)
- **Parameter heatmaps** (visualise sensitivity)
- **Short selling** support
- **Portfolio mode** (multiple assets simultaneously)
- **Alert system** (email/Telegram when live signal fires)

---

## ⚠️ Limitations of This MVP

| Limitation | Impact |
|---|---|
| Long-only, 100% position size | Cannot short; no money management |
| No look-ahead bias check | Strategies must be carefully designed |
| Binance 15m data limited to ~2 years | Smaller sample for intraday strategies |
| yfinance may have data gaps | Indian equities around holidays |
| No transaction taxes | Indian equities have STT + stamp duty |
| Sharpe ratio uses calendar days | May differ slightly from standard calculations |
| No walk-forward / out-of-sample testing | Risk of overfitting parameters |

---

## ⚖️ Disclaimer

For educational purposes only. Not financial advice.
Past backtested performance does not guarantee future results.

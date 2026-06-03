"""
Strategy Parser Agent
----------------------
Maps user-selected strategy names + raw parameter inputs to validated
configuration dictionaries that the backtester can consume directly.

This module is DETERMINISTIC — the AI does not compute backtest results.
Its only job is input validation and parameter normalisation.

Future extension: replace or augment parse_from_text() with an
OpenAI / Claude API call to support natural-language strategy descriptions,
e.g. "Use a 9/21 EMA crossover on 4h BTC data starting from Jan 2023".
"""

from __future__ import annotations

STRATEGY_REGISTRY: dict[str, dict] = {
    'EMA Crossover': {
        'module':      'strategies.ema_crossover',
        'description': 'Buy when fast EMA crosses above slow EMA; sell on cross below.',
        'params': {
            'fast_period': {'type': int,   'default': 9,   'min': 2,   'max': 200},
            'slow_period': {'type': int,   'default': 21,  'min': 3,   'max': 500},
        },
    },
    'Chandelier Exit': {
        'module':      'strategies.chandelier_exit',
        'description': 'ATR-based trailing stop that flips bullish/bearish.',
        'params': {
            'atr_period':     {'type': int,   'default': 22,  'min': 5,   'max': 100},
            'atr_multiplier': {'type': float, 'default': 3.0, 'min': 0.5, 'max': 10.0},
        },
    },
}


def parse_strategy(strategy_name: str, params: dict) -> dict:
    """
    Validate and normalise strategy parameters.

    Args:
        strategy_name: Key from STRATEGY_REGISTRY.
        params:        Raw parameter dict from the UI (may be unclamped / wrong type).

    Returns:
        {'strategy': str, 'params': dict_of_validated_values}

    Raises:
        ValueError: If strategy_name is unknown or params fail validation.
    """
    if strategy_name not in STRATEGY_REGISTRY:
        raise ValueError(
            f"Unknown strategy '{strategy_name}'. "
            f"Available: {list(STRATEGY_REGISTRY.keys())}"
        )

    spec      = STRATEGY_REGISTRY[strategy_name]
    validated = {}

    for name, meta in spec['params'].items():
        raw   = params.get(name, meta['default'])
        value = meta['type'](raw)
        value = max(meta['min'], min(meta['max'], value))
        validated[name] = value

    # Extra cross-parameter validation
    if strategy_name == 'EMA Crossover':
        if validated['fast_period'] >= validated['slow_period']:
            raise ValueError(
                f"fast_period ({validated['fast_period']}) must be "
                f"less than slow_period ({validated['slow_period']})."
            )

    return {'strategy': strategy_name, 'params': validated}


def list_strategies() -> list[str]:
    """Return all registered strategy names."""
    return list(STRATEGY_REGISTRY.keys())


def parse_from_text(text: str) -> dict | None:
    """
    Placeholder for natural-language strategy parsing.

    Future: call OpenAI / Claude API to extract strategy name and parameters
    from free-form text, then pass result to parse_strategy().

    Args:
        text: Natural language description, e.g.
              "Backtest BTC/USDT 15m with 9/21 EMA crossover from Jan 2023"

    Returns:
        Validated strategy config dict, or None if parsing fails.
    """
    # TODO: Implement NLP parsing via LLM API
    raise NotImplementedError(
        "Natural-language parsing is not yet implemented. "
        "Use the Streamlit UI controls to configure your strategy."
    )

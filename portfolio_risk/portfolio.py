"""Portfolio definitions and return calculation."""

from __future__ import annotations

import pandas as pd

PORTFOLIOS: dict[str, dict[str, float]] = {
    "100% Stocks": {"Stocks": 1.0},
    "100% Bonds": {"Bonds": 1.0},
    "100% Gold": {"Gold": 1.0},
    "60/40": {"Stocks": 0.6, "Bonds": 0.4},
    "50/30/20": {"Stocks": 0.5, "Bonds": 0.3, "Gold": 0.2},
}


def portfolio_returns(returns: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    """Monthly returns of a portfolio rebalanced to its weights every month."""
    if abs(sum(weights.values()) - 1) > 1e-9:
        raise ValueError("Portfolio weights must add up to 100%")
    return sum(returns[asset] * weight for asset, weight in weights.items())


def all_portfolios(returns: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {name: portfolio_returns(returns, weights) for name, weights in PORTFOLIOS.items()}
    )

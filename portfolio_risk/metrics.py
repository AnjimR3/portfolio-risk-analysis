"""Performance and risk measures for a series of monthly returns."""

from __future__ import annotations

import numpy as np
import pandas as pd

MONTHS = 12


def growth(returns: pd.Series, start: float = 1.0) -> pd.Series:
    return start * (1 + returns).cumprod()


def annual_return(returns: pd.Series) -> float:
    return float((1 + returns).prod() ** (MONTHS / len(returns)) - 1)


def annual_volatility(returns: pd.Series) -> float:
    return float(returns.std(ddof=1) * np.sqrt(MONTHS))


def drawdown(returns: pd.Series) -> pd.Series:
    """Fall from the previous peak, including the starting value."""
    value = growth(returns)
    peak = value.cummax().clip(lower=1.0)
    return value / peak - 1


def longest_recovery_months(returns: pd.Series) -> int:
    """Longest stretch spent below a previous peak."""
    longest = current = 0
    for underwater in drawdown(returns) < 0:
        current = current + 1 if underwater else 0
        longest = max(longest, current)
    return longest


def worst_year(returns: pd.Series) -> float:
    """Worst return over any rolling 12 months."""
    return float(((1 + returns).rolling(MONTHS).apply(np.prod, raw=True) - 1).min())


def summarise(returns: pd.Series) -> dict[str, float]:
    yearly, volatility = annual_return(returns), annual_volatility(returns)
    return {
        "Annual return": yearly,
        "Volatility": volatility,
        "Return / risk": yearly / volatility if volatility else 0.0,
        "Max drawdown": float(drawdown(returns).min()),
        "Worst 12 months": worst_year(returns),
        "Longest recovery (months)": longest_recovery_months(returns),
    }

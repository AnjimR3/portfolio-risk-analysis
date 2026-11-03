"""Turn public price and yield data into monthly total returns."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

START = "1973-01"  # Gold traded freely from the early 1970s.
BOND_MATURITY_YEARS = 10


def _month_index(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.index = pd.PeriodIndex(pd.to_datetime(frame["Date"]), freq="M")
    return frame


def stock_returns(sp500: pd.DataFrame) -> pd.Series:
    """S&P 500 price return plus dividend yield.

    The source stops reporting dividends in 2023-06, so the last known yield is
    held constant after that date.
    """
    frame = _month_index(sp500)
    dividends = frame["Dividend"].where(frame["Dividend"] > 0)
    annual_yield = (dividends / frame["SP500"]).ffill()
    return (frame["SP500"].pct_change() + annual_yield.shift(1) / 12).rename("Stocks")


def bond_returns(yields: pd.DataFrame) -> pd.Series:
    """Approximate return of holding a 10-year US Treasury for one month.

    Each month buys a new par bond at the prior yield and reprices it at the
    current yield, using semi-annual compounding.
    """
    rate = _month_index(yields)["Rate"] / 100
    prior = rate.shift(1)
    periods = BOND_MATURITY_YEARS * 2
    discount = (1 + rate / 2) ** -periods
    price = prior / rate * (1 - discount) + discount
    return (price - 1 + prior / 12).rename("Bonds")


def gold_returns(gold: pd.DataFrame) -> pd.Series:
    """Gold price return. Gold pays no income."""
    return _month_index(gold)["Price"].pct_change().rename("Gold")


def load_returns(folder: str | Path) -> pd.DataFrame:
    """Load aligned monthly returns for every asset, dropping incomplete months."""
    folder = Path(folder)
    returns = pd.concat(
        [
            stock_returns(pd.read_csv(folder / "sp500.csv")),
            bond_returns(pd.read_csv(folder / "us_10y_yield.csv")),
            gold_returns(pd.read_csv(folder / "gold.csv")),
        ],
        axis=1,
    )
    return returns.loc[START:].dropna()

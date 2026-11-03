import pandas as pd
import pytest

from portfolio_risk.data import bond_returns, gold_returns, load_returns, stock_returns
from portfolio_risk.metrics import (
    annual_return, annual_volatility, drawdown, longest_recovery_months, summarise, worst_year,
)
from portfolio_risk.portfolio import PORTFOLIOS, all_portfolios, portfolio_returns


def test_annual_return_compounds():
    assert annual_return(pd.Series([0.01] * 24)) == pytest.approx(1.01**12 - 1)


def test_volatility_of_constant_returns_is_zero():
    assert annual_volatility(pd.Series([0.01] * 12)) == pytest.approx(0, abs=1e-12)


def test_drawdown_measures_fall_from_peak():
    result = drawdown(pd.Series([0.10, -0.50, 0.20]))
    assert result.tolist() == pytest.approx([0, -0.5, -0.4])


def test_drawdown_counts_a_loss_in_the_first_month():
    assert drawdown(pd.Series([-0.10])).iloc[0] == pytest.approx(-0.10)


def test_longest_recovery():
    assert longest_recovery_months(pd.Series([0.1, -0.2, 0.01, 0.5, -0.1])) == 2


def test_worst_year_uses_rolling_twelve_months():
    returns = pd.Series([0.0] * 11 + [-0.2] + [0.1] * 12)
    assert worst_year(returns) == pytest.approx(-0.2)


def test_summary_handles_zero_volatility():
    assert summarise(pd.Series([0.0] * 12))["Return / risk"] == 0


def test_weights_must_sum_to_one():
    with pytest.raises(ValueError):
        portfolio_returns(pd.DataFrame({"Stocks": [0.1]}), {"Stocks": 0.5})


def test_portfolio_is_weighted_average_each_month():
    returns = pd.DataFrame({"Stocks": [0.10], "Bonds": [0.00]})
    assert portfolio_returns(returns, {"Stocks": 0.6, "Bonds": 0.4}).iloc[0] == pytest.approx(0.06)


def test_stock_return_includes_dividend_yield():
    frame = pd.DataFrame(
        {"Date": ["2020-01-01", "2020-02-01"], "SP500": [100.0, 110.0], "Dividend": [12.0, 12.0]}
    )
    assert stock_returns(frame).iloc[1] == pytest.approx(0.10 + 0.01)


def test_stock_yield_is_held_after_dividends_stop():
    frame = pd.DataFrame(
        {"Date": ["2020-01-01", "2020-02-01", "2020-03-01"], "SP500": [100.0, 100.0, 100.0], "Dividend": [12.0, 0.0, 0.0]}
    )
    assert stock_returns(frame).iloc[2] == pytest.approx(0.01)


def test_bond_with_unchanged_yield_earns_its_coupon():
    frame = pd.DataFrame({"Date": ["2020-01-01", "2020-02-01"], "Rate": [6.0, 6.0]})
    assert bond_returns(frame).iloc[1] == pytest.approx(0.005)


def test_bond_loses_value_when_yields_rise():
    frame = pd.DataFrame({"Date": ["2020-01-01", "2020-02-01"], "Rate": [3.0, 4.0]})
    assert bond_returns(frame).iloc[1] < 0


def test_gold_return():
    frame = pd.DataFrame({"Date": ["2020-01", "2020-02"], "Price": [100.0, 105.0]})
    assert gold_returns(frame).iloc[1] == pytest.approx(0.05)


def test_real_data_is_complete_and_starts_in_1973():
    returns = load_returns("data")
    assert str(returns.index[0]) == "1973-01"
    assert not returns.isna().any().any()
    assert returns.index.is_monotonic_increasing and returns.index.is_unique
    assert len(returns) == (returns.index[-1] - returns.index[0]).n + 1
    assert returns.abs().max().max() < 0.5


def test_every_portfolio_is_calculated():
    assert list(all_portfolios(load_returns("data")).columns) == list(PORTFOLIOS)

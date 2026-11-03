"""Command line entry point: python -m portfolio_risk"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .charts import save_charts
from .data import load_returns
from .metrics import summarise
from .portfolio import all_portfolios


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyse long-run multi-asset portfolios.")
    parser.add_argument("--data", default="data")
    parser.add_argument("--output", default="output")
    args = parser.parse_args()

    returns = all_portfolios(load_returns(args.data))
    table = pd.DataFrame({name: summarise(returns[name]) for name in returns}).T
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    table.to_csv(output / "metrics.csv", float_format="%.6f", index_label="Portfolio")
    save_charts(returns, table, output)

    print(f"Period: {returns.index[0]} to {returns.index[-1]} ({len(returns)} months)")
    print(table.to_string(float_format=lambda value: f"{value:.4f}"))


if __name__ == "__main__":
    main()

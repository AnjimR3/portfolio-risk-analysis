"""Save the charts used in the README."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, PercentFormatter

from .metrics import drawdown, growth

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e6e5e0"
COLORS = {"100% Stocks": "#2a78d6", "60/40": "#eb6834", "50/30/20": "#1baf7a"}
LABEL_OFFSET = {"50/30/20": 7, "60/40": -7}
ALL_COLORS = {**COLORS, "100% Bonds": "#6250d6", "100% Gold": "#eda100"}


def _axes(title: str):
    figure, axes = plt.subplots(figsize=(10, 5.2), facecolor=SURFACE)
    axes.set_facecolor(SURFACE)
    axes.set_title(title, loc="left", fontsize=14, fontweight="bold", color=TEXT, pad=14)
    for side in ("top", "right", "left"):
        axes.spines[side].set_visible(False)
    axes.spines["bottom"].set_color(GRID)
    axes.grid(axis="y", color=GRID, linewidth=0.8)
    axes.set_axisbelow(True)
    axes.tick_params(colors=MUTED, length=0)
    return figure, axes


def _save(figure, path: Path) -> None:
    figure.tight_layout()
    figure.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(figure)


def save_charts(returns: pd.DataFrame, table: pd.DataFrame, folder: Path) -> None:
    index = returns.index.to_timestamp()

    figure, axes = _axes("Growth of $100, log scale")
    for name, color in COLORS.items():
        value = growth(returns[name], 100)
        axes.plot(index, value, color=color, linewidth=2, label=name)
        axes.annotate(
            f"{name}: ${value.iloc[-1]:,.0f}", (index[-1], value.iloc[-1]), xytext=(8, LABEL_OFFSET.get(name, 0)),
            textcoords="offset points", va="center", color=TEXT, fontsize=10,
        )
    axes.set_yscale("log")
    axes.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value:,.0f}"))
    axes.yaxis.set_minor_formatter(FuncFormatter(lambda *_: ""))
    axes.set_xlim(index[0], index[-1] + pd.DateOffset(years=9))
    axes.set_xticks(pd.to_datetime([f"{year}-01-01" for year in range(1980, 2030, 10)]))
    axes.set_xticklabels([str(year) for year in range(1980, 2030, 10)])
    axes.legend(frameon=False, loc="upper left", labelcolor=MUTED)
    _save(figure, folder / "growth.png")

    figure, axes = _axes("Fall from previous peak")
    for name, color in COLORS.items():
        axes.plot(index, drawdown(returns[name]), color=color, linewidth=1.6, label=name)
    axes.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    axes.legend(frameon=False, loc="lower left", ncol=3, labelcolor=MUTED)
    _save(figure, folder / "drawdown.png")

    figure, axes = _axes("Return and risk, annualised")
    axes.grid(axis="x", color=GRID, linewidth=0.8)
    for name, color in ALL_COLORS.items():
        x, y = table.loc[name, "Volatility"], table.loc[name, "Annual return"]
        axes.scatter(x, y, s=90, color=color, edgecolor=SURFACE, linewidth=1.5, zorder=3)
        axes.annotate(name, (x, y), xytext=(9, 5), textcoords="offset points", color=TEXT, fontsize=10)
    axes.set_xlabel("Volatility", color=MUTED)
    axes.set_ylabel("Annual return", color=MUTED)
    axes.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    axes.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    axes.set_xlim(left=0)
    _save(figure, folder / "risk_return.png")

# The standard backtest chart, three times over: daily US market returns
# against the previous evening's 99% VaR forecast through 2007-2009, for plain
# historical simulation, the RiskMetrics normal model, and filtered historical
# simulation. The dots are the days the loss went through the forecast.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "var_backtest"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from var_common import GREY, INK, MUTED, RUST, TEAL, Z99, ewma_vol, fhs_var, hs_var, load_market, load_or_exit, year_fraction

OUT = Path(__file__).with_suffix("")


def main() -> None:
    dates, r = load_or_exit(OUT, load_market)
    vol = ewma_vol(r)
    methods = [
        ("Historical simulation, trailing 250 days", hs_var(r, 250, 0.99)),
        ("Normal distribution, EWMA volatility (RiskMetrics, decay 0.94)", Z99 * vol),
        ("Filtered historical simulation (EWMA volatility, 1000 days of residuals)", fhs_var(r, vol, 1000, 0.99)),
    ]
    m = (dates >= 20070101) & (dates <= 20091231)
    x = year_fraction(dates[m])

    fig, axes = plt.subplots(3, 1, figsize=(7.8, 7.4), sharex=True)
    for ax, (name, var) in zip(axes, methods, strict=True):
        hits = r[m] < -var[m]
        ax.vlines(x, 0, r[m] * 100, color=GREY, lw=0.7, alpha=0.8)
        ax.plot(x, -var[m] * 100, color=TEAL, lw=1.5)
        ax.scatter(x[hits], r[m][hits] * 100, s=16, color=RUST, zorder=5, edgecolor="white", linewidth=0.4)
        ax.set_title(name, fontsize=9.5, color=INK, loc="left", pad=4)
        ax.text(
            0.005,
            0.9,
            f"{hits.sum()} exceedances in {m.sum()} days   (a correct 99% VaR expects {0.01 * m.sum():.1f})",
            transform=ax.transAxes,
            ha="left",
            fontsize=8.8,
            color=RUST,
        )
        ax.set_ylim(-14.5, 13.5)
        ax.set_yticks([-10, -5, 0, 5, 10])
        ax.set_ylabel("%", fontsize=9, color=MUTED, rotation=0, labelpad=8)
        ax.tick_params(labelsize=8.5, colors=MUTED)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GREY)
    axes[-1].set_xticks([2007, 2008, 2009, 2010])
    axes[-1].set_xticklabels(["Jan 2007", "Jan 2008", "Jan 2009", "Jan 2010"])
    axes[-1].set_xlim(2007, 2010)
    fig.text(
        0.5,
        -0.04,
        "Bars: daily return of the US equity market. Line: minus the 99% one-day VaR forecast made the evening before.\n"
        "Dots: days the loss exceeded the forecast. Data from the Kenneth R. French data library.",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )
    fig.tight_layout()
    for ext in ("pdf", "svg"):
        fig.savefig(f"{OUT}.{ext}", transparent=True, bbox_inches="tight")


main()

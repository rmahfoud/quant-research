# Where the risk is, against where the money is: each position's share of the
# account and its share of the portfolio's 95% one-day VaR (component VaR), for
# the worked five-fund account.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "var_components"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from var_common import GREY, INK, LABELS, MUTED, POSITIONS, RUST, load_industries, load_or_exit, risk_report

OUT = Path(__file__).with_suffix("")


def main() -> None:
    names, dates, rows = load_or_exit(OUT, load_industries)
    pos = np.array(list(POSITIONS.values()))
    rep = risk_report(rows[:, [names.index(k) for k in POSITIONS]], pos)
    weight = pos / pos.sum() * 100
    risk = rep["component"] / rep["normal95"] * 100
    y = np.arange(len(pos))[::-1]

    fig, ax = plt.subplots(figsize=(7.8, 3.9))
    ax.barh(y + 0.19, weight, height=0.34, color=GREY, alpha=0.7, label="share of the account's dollars")
    ax.barh(y - 0.19, risk, height=0.34, color=RUST, alpha=0.9, label="share of the account's 95% VaR")
    for yi, w, k, c in zip(y, weight, risk, rep["component"], strict=True):
        ax.text(w + 0.8, yi + 0.19, f"{w:.0f}%", va="center", fontsize=8.8, color=MUTED)
        ax.text(k + 0.8, yi - 0.19, f"{k:.0f}%   (\\${c:,.0f})", va="center", fontsize=8.8, color=RUST)
    ax.set_yticks(y)
    ax.set_yticklabels([LABELS[k] for k in POSITIONS], fontsize=9.5, color=INK)
    ax.set_xlim(0, 70)
    ax.set_xlabel("percent of total", fontsize=9.5, color=MUTED)
    ax.set_title(
        f"A \\$100,000 account in five sector funds: total one-day 95% VaR \\${rep['normal95']:,.0f}",
        fontsize=10,
        color=INK,
        pad=10,
    )
    ax.tick_params(labelsize=8.5, colors=MUTED)
    ax.tick_params(axis="y", length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GREY)
    ax.legend(fontsize=8.8, frameon=False, loc="lower right")
    fig.text(
        0.5,
        -0.05,
        f"Component VaR from an EWMA (0.94) covariance matrix as of the end of {dates[-1] // 10000}. "
        "Value-weighted US industry portfolios\nfrom the Kenneth R. French data library stand in for sector funds.",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )
    fig.tight_layout()
    for ext in ("pdf", "svg"):
        fig.savefig(f"{OUT}.{ext}", transparent=True, bbox_inches="tight")


main()

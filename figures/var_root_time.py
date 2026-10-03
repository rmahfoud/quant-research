# What the square-root-of-time rule costs. Take today's one-day 99% VaR from the
# RiskMetrics model, multiply by the square root of ten, and count how often the
# next ten days lose more than that — separately for calm and turbulent starting
# points. A correct ten-day 99% VaR would be breached 1% of the time in each.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "var_root_time"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from var_common import GREY, INK, MUTED, RUST, TEAL, Z99, ewma_vol, load_market, load_or_exit

OUT = Path(__file__).with_suffix("")
H = 10


def main() -> None:
    dates, r = load_or_exit(OUT, load_market)
    vol = ewma_vol(r)
    idx = np.arange(1000, len(r) - H)
    c = np.concatenate([[0.0], np.cumsum(np.log1p(r))])
    scaled = np.expm1(c[idx + H] - c[idx]) / (vol[idx] * np.sqrt(H))
    bucket = np.searchsorted(np.quantile(vol[idx], [0.2, 0.4, 0.6, 0.8]), vol[idx])
    rates = [np.mean(scaled[bucket == b] < -Z99) * 100 for b in range(5)]
    vols = [vol[idx][bucket == b].mean() * 100 for b in range(5)]

    fig, ax = plt.subplots(figsize=(7.8, 4.0))
    bars = ax.bar(range(5), rates, width=0.62, color=[RUST, RUST, RUST, RUST, TEAL], alpha=0.88)
    for b, rate in zip(bars, rates, strict=True):
        ax.text(b.get_x() + b.get_width() / 2, rate + 0.12, f"{rate:.1f}%", ha="center", fontsize=9.5, color=INK)
    ax.axhline(1.0, color=INK, lw=1.1, ls="--")
    ax.text(4.42, 6.2, "dashed line: the 1% a correct ten-day 99% VaR delivers", fontsize=8.8, color=INK, ha="right")
    ax.set_xticks(range(5))
    ax.set_xticklabels(
        [
            f"{label}\n(daily vol {v:.2f}%)"
            for label, v in zip(("calmest fifth", "2nd", "3rd", "4th", "most turbulent fifth"), vols, strict=True)
        ]
    )
    ax.set_ylim(0, 6.8)
    ax.set_ylabel("ten-day breach rate, %", fontsize=9.5, color=MUTED)
    ax.set_xlabel("today's volatility", fontsize=9.5, color=MUTED)
    ax.set_title(
        "How often the next ten days lose more than  √10 × today's one-day 99% VaR",
        fontsize=10,
        color=INK,
        pad=10,
    )
    ax.tick_params(labelsize=8.5, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)
    fig.text(
        0.5,
        -0.05,
        f"US equity market, overlapping ten-day windows, {dates[1000] // 10000}–{dates[-1] // 10000}; "
        "one-day VaR is 2.33 × EWMA (0.94) volatility.\nData from the Kenneth R. French data library.",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )
    fig.tight_layout()
    for ext in ("pdf", "svg"):
        fig.savefig(f"{OUT}.{ext}", transparent=True, bbox_inches="tight")


main()

# The picture everyone draws of value at risk: the last 500 daily P&Ls of
# $100,000 in the US equity market, with the 95% and 99% VaR cut-offs, the
# 97.5% expected shortfall, and the normal curve that the parametric method
# puts in the histogram's place.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "var_anatomy"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from var_common import GREY, INK, MUTED, RUST, TEAL, load_market, load_or_exit

OUT = Path(__file__).with_suffix("")
NOTIONAL = 100_000.0


def main() -> None:
    dates, r = load_or_exit(OUT, load_market)
    pnl = r[-500:] * NOTIONAL
    var95, var99 = -np.quantile(pnl, 0.05), -np.quantile(pnl, 0.01)
    es = -pnl[pnl <= np.quantile(pnl, 0.025)].mean()
    sd = pnl.std(ddof=1)

    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    bins = np.arange(-6250, 10251, 250)
    counts, edges = np.histogram(pnl, bins=bins)
    centres = (edges[:-1] + edges[1:]) / 2
    tail = centres < -var95
    ax.bar(centres[~tail], counts[~tail], width=230, color=GREY, alpha=0.55, lw=0)
    ax.bar(centres[tail], counts[tail], width=230, color=RUST, alpha=0.85, lw=0)

    x = np.linspace(-6500, 6500, 600)
    ax.plot(x, 500 * 250 * np.exp(-((x - pnl.mean()) ** 2) / (2 * sd**2)) / (sd * np.sqrt(2 * np.pi)), color=INK, lw=1.3)
    ax.text(1500, 44, "normal curve with\nthe same standard deviation", fontsize=8.5, color=INK, va="center")

    top = counts.max() * 1.18
    for value, label, colour, height in (
        (var95, f"95% VaR  \\${var95:,.0f}\n25 of the 500 days were worse", TEAL, 0.95),
        (var99, f"99% VaR  \\${var99:,.0f}\n5 days were worse", TEAL, 0.72),
        (es, f"97.5% ES  \\${es:,.0f}\naverage of the worst 13 days", RUST, 0.49),
    ):
        ax.plot([-value, -value], [0, top * height], color=colour, lw=1.4, ls="--" if colour == RUST else "-")
        ax.plot([-3650, -value], [top * height, top * height], color=colour, lw=0.8)
        ax.text(-6450, top * height, label, fontsize=8.8, color=colour, ha="left", va="center")
    ax.annotate(
        f"worst day  -\\${-pnl.min():,.0f}",
        xy=(pnl.min(), 1.2),
        xytext=(pnl.min() + 250, 12),
        fontsize=8.5,
        color=RUST,
        ha="center",
        arrowprops={"arrowstyle": "-", "color": RUST, "lw": 0.8},
    )

    ax.set_xlim(-6600, 6600)
    ax.set_ylim(0, top)
    ax.set_xlabel("one-day profit or loss on \\$100,000, dollars", fontsize=9.5, color=MUTED)
    ax.set_ylabel("days", fontsize=9.5, color=MUTED)
    ax.set_title(
        f"500 trading days of the US equity market, ending {dates[-1] // 10000}",
        fontsize=10,
        color=INK,
        pad=10,
    )
    ax.tick_params(labelsize=8.5, colors=MUTED)
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)
    fig.text(
        0.5,
        -0.03,
        "VaR marks where the tail begins. It is silent about how far the tail goes. "
        "Daily data from the Kenneth R. French data library.",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )
    fig.tight_layout()
    for ext in ("pdf", "svg"):
        fig.savefig(f"{OUT}.{ext}", transparent=True, bbox_inches="tight")


main()

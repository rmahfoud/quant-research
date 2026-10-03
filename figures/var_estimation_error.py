# How precisely a tail-risk number can be estimated at all. IID Student t(4)
# returns, so every model assumption holds and the only problem is sample size:
# the bars are the central 90% of estimates across 20,000 simulated histories,
# as a ratio to the true value.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "var_estimation_error"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from var_common import GREY, INK, MUTED, RUST, TEAL, estimation_error

OUT = Path(__file__).with_suffix("")


def main() -> None:
    results = estimation_error()
    windows = list(results)
    series = [
        ("VaR 95% (HS)", "95% VaR, historical simulation", GREY),
        ("VaR 99% (HS)", "99% VaR, historical simulation", TEAL),
        ("ES 97.5% (HS)", "97.5% ES, historical simulation", RUST),
        ("VaR 99% (normal)", "99% VaR, normal formula", INK),
    ]
    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    ax.axhline(1.0, color=GREY, lw=1.0, ls=":")
    for j, (key, label, colour) in enumerate(series):
        for i, n in enumerate(windows):
            lo, mid, hi = np.quantile(results[n][key], [0.05, 0.5, 0.95])
            xpos = i + (j - 1.5) * 0.19
            ax.plot([xpos, xpos], [lo, hi], color=colour, lw=5, alpha=0.75, solid_capstyle="butt")
            ax.scatter(
                [xpos],
                [mid],
                s=22,
                color="white",
                edgecolor=colour,
                linewidth=1.3,
                zorder=5,
                label=label if i == 0 else None,
            )
    ax.set_xticks(range(len(windows)))
    ax.set_xticklabels([f"{n} days\n({n / 250:g} yr)" for n in windows])
    ax.set_ylim(0.6, 1.4)
    ax.set_yticks([0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
    ax.set_ylabel("estimate ÷ truth", fontsize=9.5, color=MUTED)
    ax.set_xlabel("history used", fontsize=9.5, color=MUTED)
    ax.set_title(
        "Sampling error of a one-day tail estimate  (bar: central 90% of estimates, dot: median)",
        fontsize=10,
        color=INK,
        pad=10,
    )
    ax.tick_params(labelsize=8.5, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)
    ax.legend(fontsize=8.5, frameon=False, loc="upper right", ncol=2)
    fig.text(
        0.5,
        -0.04,
        "Simulated IID Student t(4) returns: fat-tailed, but with nothing changing over time. "
        "The normal formula is tighter and reliably wrong.",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )
    fig.tight_layout()
    for ext in ("pdf", "svg"):
        fig.savefig(f"{OUT}.{ext}", transparent=True, bbox_inches="tight")


main()

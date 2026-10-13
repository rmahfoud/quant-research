# Eight definitions of a "bad" market regime, drawn as strips under the US
# market index from 1995 to 2025, for regime_classification.md. The labels and
# the data are built in rc_common.py, which also prints the statistics the
# chapter quotes.
#
# Run standalone:  uv run --no-project --with matplotlib python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "rc-labels"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from rc_common import GOLD, GREY, INK, MUTED, RUST, TEAL, labels, load_or_exit, market, runs, to_datetime64

START, STOP = 19950101, 20251231
STRIPS = [
    ("Bear, ±20% rule, ex post", RUST),
    ("Bear, ±20% rule, as confirmed", RUST),
    ("10% below the high, now", RUST),
    ("Next-month volatility, top fifth", TEAL),
    ("10% drawdown in next quarter", TEAL),
    ("Negative next-quarter return", TEAL),
    ("Jump model, high-risk state", GOLD),
    ("NBER recession", GOLD),
]


def main() -> None:
    load_or_exit(Path(__file__))
    m, labs = market(), labels()
    dates = m["dates"]
    i0, i1 = np.searchsorted(dates, START), np.searchsorted(dates, STOP, side="right")
    t = to_datetime64(dates[i0:i1])
    wealth = m["P"][i0:i1] / m["P"][i0]

    fig, axes = plt.subplots(
        2, 1, figsize=(7.0, 5.9), sharex=True, gridspec_kw={"height_ratios": [1.0, 1.55], "hspace": 0.08}
    )
    ax = axes[0]
    bear = np.nan_to_num(labs["Bear, ±20% rule, ex post"][i0:i1]).astype(int)
    for a, b in runs(bear):
        ax.axvspan(t[a], t[min(b + 1, len(t) - 1)], color=RUST, alpha=0.16, linewidth=0)
    ax.plot(t, wealth, color=INK, linewidth=0.9)
    ax.set_yscale("log")
    ax.set_ylabel("growth of one dollar\n(log scale)", fontsize=9.5, color=MUTED)
    ax.set_yticks([1, 2, 4, 8, 16])
    ax.set_yticklabels(["1", "2", "4", "8", "16"])
    ax.set_title(
        "US stock market, 1995-2025, with ex-post ±20% bear markets shaded",
        fontsize=10.0,
        color=INK,
        loc="left",
        pad=8,
    )

    ax = axes[1]
    n = len(STRIPS)
    for row, (name, color) in enumerate(STRIPS):
        y = labs[name][i0:i1]
        level = n - 1 - row
        on = np.nan_to_num(y).astype(int)
        for a, b in runs(on):
            ax.axvspan(
                t[a],
                t[min(b + 1, len(t) - 1)],
                ymin=(level + 0.18) / n,
                ymax=(level + 0.82) / n,
                color=color,
                linewidth=0,
            )
        undefined = np.flatnonzero(~np.isfinite(y))
        if len(undefined):
            ax.axvspan(
                t[undefined[0]],
                t[-1],
                ymin=(level + 0.18) / n,
                ymax=(level + 0.82) / n,
                color=GREY,
                alpha=0.25,
                linewidth=0,
            )
    ax.set_ylim(0, n)
    ax.set_yticks([n - 1 - k + 0.5 for k in range(n)])
    ax.set_yticklabels([name for name, _ in STRIPS], fontsize=9.0, color=INK)
    ax.tick_params(axis="y", length=0)
    for k in range(1, n):
        ax.axhline(k, color=GREY, linewidth=0.4, alpha=0.5)
    ax.text(
        0.0,
        -0.17,
        "Rust: price-path rules.  Teal: next-month or next-quarter outcomes.  Gold: fitted model, NBER.",
        transform=ax.transAxes,
        fontsize=8.8,
        color=MUTED,
    )
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    for ax in axes:
        ax.tick_params(labelsize=9.0, colors=MUTED, length=3)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GREY)
    axes[1].spines["left"].set_visible(False)

    out = Path(__file__).with_suffix(".svg")
    fig.savefig(out, transparent=True, bbox_inches="tight", metadata={"Date": None})
    print(f"wrote {out.name}")


if __name__ == "__main__":
    main()

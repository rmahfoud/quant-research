# The yield decomposition, drawn. Every bond's yield is the same sum of
# components with different terms switched on. Representative magnitudes for a
# mid-cycle environment, not a quote from any date: the point is the structure,
# not the levels.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "bd_yield_stack"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"

# component -> colour.  Ordered as they stack, bottom to top.
COMPONENTS = [
    ("expected real short rate", "#1F3A6E"),
    ("expected inflation", "#4E7CB8"),
    ("term premium", "#0B6E75"),
    ("expected credit loss", "#C98A2E"),
    ("credit risk premium", "#A8452B"),
    ("liquidity premium", "#7A5E86"),
    ("option cost", "#5A6E4A"),
]

# instrument -> the seven components, in percent.
BONDS = {
    "3-month\nT-bill":            [1.50, 2.30, 0.00, 0.00, 0.00, 0.00, 0.00],
    "10-year\nTIPS":              [1.50, 0.00, 0.50, 0.00, 0.00, 0.00, 0.00],
    "10-year\nTreasury":          [1.50, 2.30, 0.50, 0.00, 0.00, 0.00, 0.00],
    "Current-coupon\nagency MBS": [1.50, 2.30, 0.60, 0.00, 0.00, 0.05, 0.60],
    "10-year\nA-rated corp":      [1.50, 2.30, 0.50, 0.10, 0.60, 0.25, 0.00],
    "8-year\nB-rated corp":       [1.50, 2.30, 0.45, 2.20, 1.40, 0.60, 0.15],
    "10-year EM\nsovereign, USD": [1.50, 2.30, 0.50, 0.80, 1.10, 0.40, 0.00],
}


def main() -> None:
    names = list(BONDS)
    data = np.array([BONDS[n] for n in names])
    totals = data.sum(axis=1)
    y = np.arange(len(names))[::-1]

    fig, ax = plt.subplots(figsize=(10.4, 4.6))
    left = np.zeros(len(names))
    for i, (label, colour) in enumerate(COMPONENTS):
        ax.barh(y, data[:, i], left=left, color=colour, height=0.62,
                label=label, edgecolor="white", lw=0.7)
        left += data[:, i]

    for yi, tot in zip(y, totals):
        ax.text(tot + 0.12, yi, f"{tot:.2f}%", va="center", fontsize=9,
                color=INK, fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=8.5)
    ax.set_xlabel("yield (%)", fontsize=9)
    ax.set_xlim(0, 10.2)
    ax.tick_params(labelsize=8.5, colors=MUTED)
    ax.tick_params(axis="y", colors=INK)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#DCE4E6")
    ax.legend(fontsize=8.0, frameon=False, ncol=4, loc="upper center",
              bbox_to_anchor=(0.5, -0.145))
    ax.set_title("One decomposition, seven markets", fontsize=10.5, color=INK, loc="left")

    ax.text(
        0.5, -0.36,
        "Representative mid-cycle magnitudes, not a quote from any date. The TIPS bar is short because "
        "inflation is stripped out of it,\nnot because it is cheap. Read a yield by asking which blocks are "
        "in it and which risk each one pays you to carry.",
        transform=ax.transAxes, ha="center", va="top", fontsize=8.5, color=MUTED,
    )
    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print(f"{'instrument':>30} {'yield':>7} {'spread to 10y UST':>19}")
    ust = BONDS["10-year\nTreasury"]
    ust_total = sum(ust)
    for n in names:
        t = sum(BONDS[n])
        print(f"{n.replace(chr(10), ' '):>30} {t:6.2f}% {(t - ust_total) * 100:15.0f}bp")
    print()
    hy = BONDS["8-year\nB-rated corp"]
    hy_spread = sum(hy[3:])
    print(f"B-rated spread {hy_spread * 100:.0f}bp = expected loss {hy[3] * 100:.0f}bp "
          f"+ risk premium {hy[4] * 100:.0f}bp + liquidity {hy[5] * 100:.0f}bp + option {hy[6] * 100:.0f}bp")
    print(f"  expected loss is {hy[3] / hy_spread:.0%} of the spread")
    ig = BONDS["10-year\nA-rated corp"]
    ig_spread = sum(ig[3:])
    print(f"A-rated spread {ig_spread * 100:.0f}bp; expected loss is {ig[3] / ig_spread:.0%} of it")


main()

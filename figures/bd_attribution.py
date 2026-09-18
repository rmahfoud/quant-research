# Where a year of bond return comes from. The same 10-year bond, held one year,
# under a large sell-off and a large rally, with the return split into the four
# terms of the return identity. Carry and roll are known in advance; the other
# two are the bet.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "bd_attribution"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
NAVY = "#1F3A6E"
FAINT = "#DCE4E6"

COUPON = 0.04
Y10 = 0.04
Y9 = 0.0392  # the curve is 8bp steeper between 9 and 10 years
FREQ = 2


def price(y: float, maturity: float, coupon: float = COUPON) -> float:
    n = int(round(maturity * FREQ))
    t = np.arange(1, n + 1)
    cf = np.full(n, 100.0 * coupon / FREQ)
    cf[-1] += 100.0
    return float((cf * (1.0 + y / FREQ) ** (-t)).sum())


def risk(y: float, maturity: float) -> tuple[float, float]:
    h = 1e-5
    p0, pu, pd = price(y, maturity), price(y + h, maturity), price(y - h, maturity)
    return -(pu - pd) / (2 * h) / p0, (pu - 2 * p0 + pd) / h**2 / p0


def attribute(dy: float) -> dict[str, float]:
    p0 = price(Y10, 10.0)
    p_roll = price(Y9, 9.0)                    # one year later, curve unchanged
    p1 = price(Y9 + dy, 9.0)                   # one year later, curve shifted
    d, c = risk(Y9, 9.0)

    carry = 100.0 * COUPON / p0
    roll = (p_roll - p0) / p0
    duration = -d * dy
    convexity = 0.5 * c * dy**2
    total = (p1 - p0 + 100.0 * COUPON) / p0
    return {
        "coupon\n(carry)": carry * 100,
        "roll-down": roll * 100,
        "duration\n$-D \\Delta y$": duration * 100,
        "convexity\n$+\\frac{1}{2} C (\\Delta y)^2$": convexity * 100,
        "cross terms": (total - carry - roll - duration - convexity) * 100,
        "_total": total * 100,
    }


def waterfall(ax, parts: dict[str, float], title: str) -> None:
    labels = [k for k in parts if k != "_total"]
    vals = [parts[k] for k in labels]
    running = np.concatenate([[0.0], np.cumsum(vals)])
    for i, (lab, v) in enumerate(zip(labels, vals)):
        colour = TEAL if v >= 0 else RUST
        ax.bar(i, v, bottom=running[i], color=colour, width=0.62, edgecolor="white", lw=0.8)
        off = 0.9 if v >= 0 else -0.9
        ax.text(i, running[i] + v + off, f"{v:+.1f}", ha="center", va="center",
                fontsize=8.5, color=INK, fontweight="bold")
        if i < len(labels) - 1:
            ax.plot([i + 0.31, i + 0.69], [running[i + 1]] * 2, color=FAINT, lw=1.0, zorder=0)
    n = len(labels)
    ax.bar(n, parts["_total"], color=NAVY, width=0.62, edgecolor="white", lw=0.8)
    ax.text(n, parts["_total"] + (0.9 if parts["_total"] >= 0 else -0.9),
            f"{parts['_total']:+.1f}", ha="center", va="center",
            fontsize=9.5, color=NAVY, fontweight="bold")
    ax.set_xticks(range(n + 1))
    ax.set_xticklabels(labels + ["total\nreturn"], fontsize=8.0)
    ax.axhline(0, color=INK, lw=0.9)
    ax.set_ylabel("contribution to one-year return (%)", fontsize=9)
    ax.set_title(title, fontsize=10.5, color=INK, loc="left")
    ax.set_ylim(-24, 22)
    ax.tick_params(labelsize=8.5, colors=MUTED)
    ax.tick_params(axis="x", colors=INK)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(FAINT)


def main() -> None:
    cases = [(0.025, "Yields rise 250bp"), (-0.015, "Yields fall 150bp")]
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.5), sharey=True)
    for ax, (dy, title) in zip(axes, cases):
        waterfall(ax, attribute(dy), title)

    fig.text(
        0.5, -0.06,
        "A 10-year 4% bond bought at par, held one year, on a curve 8bp steeper between 9 and 10 years. "
        "The first two bars are\nknown the day you buy; the third is the entire bet; the fourth is the "
        "consolation prize that makes the loss smaller than the gain.",
        ha="center", fontsize=8.5, color=MUTED,
    )
    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    d, c = risk(Y9, 9.0)
    print(f"9-year bond at {Y9 * 100:.2f}%: modified duration {d:.2f}, convexity {c:.1f}")
    for dy, title in cases:
        parts = attribute(dy)
        print(f"\n{title} (dy = {dy * 1e4:+.0f}bp)")
        for k, v in parts.items():
            print(f"  {k.replace(chr(10), ' '):>34}  {v:+7.2f}%")
    p0 = price(Y10, 10.0)
    cushion = (100 * COUPON / p0 + (price(Y9, 9.0) - p0) / p0)
    print(f"\ncarry + roll = {cushion * 100:.2f}%; breakeven yield rise = {cushion / d * 1e4:.0f}bp")
    for label, mat in (("2-year", 2.0), ("5-year", 5.0), ("10-year", 10.0), ("30-year", 30.0)):
        dd, _ = risk(Y10, mat)
        print(f"  {label:>8}: duration {dd:5.2f}, one-year breakeven on 4% carry alone = "
              f"{0.04 / dd * 1e4:5.0f}bp")


main()

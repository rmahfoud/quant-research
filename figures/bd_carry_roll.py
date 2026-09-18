# Carry, roll-down, and the cushion. Left: a bond ages down an upward-sloping
# curve, so even with the curve pinned its yield falls and its price rises.
# Right: the one-year return of four maturities against a parallel shift. Where
# each line crosses zero is how much of a sell-off that bond's yield can absorb
# before the holder loses money.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "bd_carry_roll"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
NAVY = "#1F3A6E"
GOLD = "#C98A2E"
FAINT = "#DCE4E6"

FREQ = 2


def curve(t: np.ndarray | float) -> np.ndarray:
    """A plain upward-sloping curve: 3.0% at the front, flattening towards 4.6%."""
    return 0.030 + 0.016 * (1.0 - np.exp(-np.asarray(t, dtype=float) / 6.0))


def price(y: float, maturity: float, coupon: float) -> float:
    n = int(round(maturity * FREQ))
    t = np.arange(1, n + 1)
    cf = np.full(n, 100.0 * coupon / FREQ)
    cf[-1] += 100.0
    return float((cf * (1.0 + y / FREQ) ** (-t)).sum())


def one_year_return(maturity: float, dy: float) -> float:
    """Buy at the curve, hold a year, curve shifts by dy in parallel."""
    coupon = float(curve(maturity))            # issued at par
    p0 = price(coupon, maturity, coupon)
    y1 = float(curve(maturity - 1.0)) + dy
    p1 = price(y1, maturity - 1.0, coupon)
    return (p1 - p0 + 100.0 * coupon) / p0


def breakeven(maturity: float) -> float:
    lo, hi = -0.02, 0.06
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if one_year_return(maturity, mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def main() -> None:
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.0, 4.3))

    ts = np.linspace(0.25, 12, 300)
    ax.plot(ts, curve(ts) * 100, color=NAVY, lw=2.0, label="the curve (unchanged)")
    y5, y4 = float(curve(5.0)), float(curve(4.0))
    ax.plot([5.0], [y5 * 100], "o", color=RUST, ms=8, zorder=5)
    ax.plot([4.0], [y4 * 100], "o", color=TEAL, ms=8, zorder=5)
    ax.annotate(
        "", xy=(4.05, y4 * 100), xytext=(4.95, y5 * 100),
        arrowprops=dict(arrowstyle="->", color=RUST, lw=1.6),
    )
    ax.text(4.5, y5 * 100 + 0.10, "one year passes", ha="center", fontsize=8.5, color=RUST)
    ax.text(5.25, y5 * 100 - 0.06, f"buy a 5-year at {y5 * 100:.2f}%", fontsize=8.5,
            color=RUST, va="center")
    ax.annotate(
        f"it is now a 4-year, worth {y4 * 100:.2f}%\non the same curve — the price rises",
        xy=(4.0, y4 * 100 - 0.03), xytext=(6.8, 3.32),
        fontsize=8.5, color=TEAL, ha="center", va="center",
        arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.0),
    )
    ax.set_xlabel("maturity (years)", fontsize=9)
    ax.set_ylabel("yield (%)", fontsize=9)
    ax.set_title("Roll-down: the bond moves, the curve does not", fontsize=10.5, color=INK, loc="left")
    ax.set_ylim(2.75, 4.8)
    ax.legend(fontsize=8.5, frameon=False, loc="lower right")

    shifts = np.linspace(-0.015, 0.03, 300)
    mats = [(2.0, "2-year", NAVY), (5.0, "5-year", TEAL),
            (10.0, "10-year", GOLD), (30.0, "30-year", RUST)]
    for mat, label, c in mats:
        r = np.array([one_year_return(mat, dy) for dy in shifts]) * 100
        bx.plot(shifts * 1e4, r, color=c, lw=1.9, label=label)
        be = breakeven(mat)
        bx.plot([be * 1e4], [0.0], "o", color=c, ms=5, zorder=5)
    bx.axhline(0, color=INK, lw=0.9)
    bx.axvline(0, color=FAINT, lw=1.0, zorder=0)
    bx.set_xlabel("parallel yield shift over the year (basis points)", fontsize=9)
    bx.set_ylabel("one-year total return (%)", fontsize=9)
    bx.set_title("The cushion, and how fast it runs out", fontsize=10.5, color=INK, loc="left")
    bx.set_ylim(-28, 22)
    bx.legend(fontsize=8.5, frameon=False, loc="upper right")
    bx.text(0.02, 0.06, "dots: the sell-off each bond can absorb\nbefore the year's return turns negative",
            transform=bx.transAxes, fontsize=8.0, color=MUTED, va="bottom")

    for a in (ax, bx):
        a.tick_params(labelsize=8.5, colors=MUTED)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            a.spines[s].set_color(FAINT)

    fig.text(
        0.5, -0.05,
        "Carry and roll-down are the return you get for doing nothing, and they are known the day you buy. "
        "Duration converts\na yield move into a price move. A long bond has more yield and far less "
        "protection: its cushion is measured in weeks of patience.",
        ha="center", fontsize=8.5, color=MUTED,
    )
    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print(f"curve: {'  '.join(f'{t:g}y {float(curve(t)) * 100:.2f}%' for t in (1, 2, 5, 10, 30))}")
    print(f"\n{'bond':>8} {'yield':>7} {'carry':>7} {'roll':>7} {'carry+roll':>11} {'breakeven':>10}")
    for mat, label, _ in mats:
        cpn = float(curve(mat))
        p0 = price(cpn, mat, cpn)
        roll = (price(float(curve(mat - 1.0)), mat - 1.0, cpn) - p0) / p0
        be = breakeven(mat)
        print(f"{label:>8} {cpn * 100:6.2f}% {cpn * 100:6.2f}% {roll * 100:6.2f}% "
              f"{(cpn + roll) * 100:10.2f}% {be * 1e4:8.0f}bp")
    print()
    for mat, label, _ in mats:
        print(f"{label:>8}: +100bp year {one_year_return(mat, 0.01) * 100:+6.2f}%   "
              f"-100bp year {one_year_return(mat, -0.01) * 100:+6.2f}%")


main()

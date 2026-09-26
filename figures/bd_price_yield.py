# The price-yield curve, the duration tangent, and the convexity gap. Three
# bonds priced at par at 4%: 2-year, 10-year, 30-year. The straight line is what
# duration alone predicts for the 30-year; the gap between it and the true curve
# is convexity, and it is always in the holder's favour for an option-free bond.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "bd_price_yield"
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

Y0 = 0.04
FREQ = 2


def price(y: float | np.ndarray, maturity: float, coupon: float) -> np.ndarray:
    """Semi-annual coupon bond, 100 face, flat yield y."""
    n = int(maturity * FREQ)
    t = np.arange(1, n + 1)
    cf = np.full(n, 100.0 * coupon / FREQ)
    cf[-1] += 100.0
    d = (1.0 + np.asarray(y)[..., None] / FREQ) ** (-t)
    return (cf * d).sum(axis=-1)


def risk(maturity: float, coupon: float, y: float = Y0) -> tuple[float, float, float]:
    """Price, modified duration and convexity by central difference."""
    h = 1e-5
    p0 = float(price(np.array(y), maturity, coupon))
    pu = float(price(np.array(y + h), maturity, coupon))
    pd = float(price(np.array(y - h), maturity, coupon))
    dur = -(pu - pd) / (2 * h) / p0
    cvx = (pu - 2 * p0 + pd) / (h**2) / p0
    return p0, dur, cvx


def main() -> None:
    bonds = [(2.0, "2-year"), (10.0, "10-year"), (30.0, "30-year")]
    colours = [NAVY, TEAL, RUST]
    ys = np.linspace(0.0, 0.10, 400)

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.0, 4.3))

    for (mat, label), c in zip(bonds, colours, strict=True):
        ax.plot(ys * 100, price(ys, mat, Y0), color=c, lw=1.9, label=label)
    p30, d30, c30 = risk(30.0, Y0)
    tangent = p30 * (1 - d30 * (ys - Y0))
    ax.plot(ys * 100, tangent, color=MUTED, lw=1.3, ls="--", label="duration line (30-year)")
    ax.fill_between(ys * 100, tangent, price(ys, 30.0, Y0), color=RUST, alpha=0.11, lw=0)

    ax.axhline(100, color=FAINT, lw=1.0, zorder=0)
    ax.axvline(Y0 * 100, color=FAINT, lw=1.0, zorder=0)
    ax.annotate(
        "convexity:\nthe curve sits above\nits own tangent",
        xy=(7.6, float(price(np.array(0.076), 30.0, Y0))),
        xytext=(6.4, 118),
        fontsize=8.5,
        color=RUST,
        ha="center",
        arrowprops=dict(arrowstyle="->", color=RUST, lw=1.0),
    )
    ax.set_xlabel("yield to maturity (%)", fontsize=9)
    ax.set_ylabel("price (per 100 face)", fontsize=9)
    ax.set_title("Price against yield, 4% coupon bonds", fontsize=10.5, color=INK, loc="left")
    ax.set_ylim(20, 190)
    ax.legend(fontsize=8.5, frameon=False)

    shifts = np.linspace(-0.03, 0.03, 200)
    true = price(Y0 + shifts, 30.0, Y0) / p30 - 1
    lin = -d30 * shifts
    quad = -d30 * shifts + 0.5 * c30 * shifts**2
    bx.plot(shifts * 1e4, true * 100, color=RUST, lw=2.0, label="actual")
    bx.plot(shifts * 1e4, lin * 100, color=MUTED, lw=1.3, ls="--", label="duration only")
    bx.plot(shifts * 1e4, quad * 100, color=TEAL, lw=1.3, ls=":", label="duration + convexity")
    bx.axhline(0, color=FAINT, lw=1.0)
    bx.axvline(0, color=FAINT, lw=1.0)
    bx.set_xlabel("parallel yield shift (basis points)", fontsize=9)
    bx.set_ylabel("price change (%)", fontsize=9)
    bx.set_title("30-year bond: what each approximation predicts", fontsize=10.5, color=INK, loc="left")
    bx.legend(fontsize=8.5, frameon=False)

    for a in (ax, bx):
        a.tick_params(labelsize=8.5, colors=MUTED)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            a.spines[s].set_color(FAINT)

    fig.text(
        0.5,
        -0.05,
        "Duration is the slope at today's yield; it is exact only for an infinitesimal move. Convexity is the "
        "curvature,\nand for an option-free bond it always helps: gains from a rally exceed losses from an "
        "equal-sized sell-off.",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )
    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print("4% coupon bonds priced at par, y = 4.00%")
    print(f"{'bond':>10} {'price':>8} {'mod dur':>9} {'convexity':>10}")
    for mat, label in bonds:
        p, d, c = risk(mat, Y0)
        print(f"{label:>10} {p:8.2f} {d:9.2f} {c:10.1f}")
    print()
    for mat, label in bonds:
        p, d, c = risk(mat, Y0)
        for bp in (-100, 100, -300, 300):
            dy = bp / 1e4
            actual = float(price(np.array(Y0 + dy), mat, Y0)) / p - 1
            lin_ = -d * dy
            quad_ = -d * dy + 0.5 * c * dy**2
            print(
                f"{label:>10} {bp:+5d}bp  actual {actual * 100:+7.2f}%   "
                f"duration {lin_ * 100:+7.2f}%  (err {(lin_ - actual) * 100:+5.2f})   "
                f"+convexity {quad_ * 100:+7.2f}%  (err {(quad_ - actual) * 100:+5.2f})"
            )
    print()
    p, d, c = risk(30.0, Y0)
    up = float(price(np.array(Y0 + 0.01), 30.0, Y0)) / p - 1
    dn = float(price(np.array(Y0 - 0.01), 30.0, Y0)) / p - 1
    print(f"30-year, +/-100bp: gain {dn * 100:+.2f}% vs loss {up * 100:+.2f}%; asymmetry {(dn + up) * 100:+.2f}pp")


main()

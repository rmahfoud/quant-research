# Six stylised term structures and the carry term that shapes each one. These
# are shapes, not quotes: each curve is drawn from the cost-of-carry relation
# F = S exp(c * tau) with the net carry c chosen to match the market's usual
# driver, plus a seasonal term for natural gas and a mean-reverting expectation
# for the VIX, which has no cost of carry at all.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "fm_term_shapes"
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

OUT = Path(__file__).with_suffix("")


def main() -> None:
    fig, axes = plt.subplots(2, 3, figsize=(11.0, 6.4))
    months = np.arange(1, 13)
    tau = months / 12.0

    panels = []
    panels.append(
        (
            "Equity index",
            "financing minus dividends:\nc = r - q, a gentle contango",
            100 * np.exp((0.0375 - 0.012) * tau),
            NAVY,
            months,
        )
    )
    panels.append(
        (
            "Gold",
            "near full carry: financing plus a\ntiny storage cost, no convenience",
            100 * np.exp((0.0375 + 0.002) * tau),
            GOLD,
            months,
        )
    )
    panels.append(
        (
            "Crude oil, tight market",
            "low inventories: convenience yield\nexceeds financing, so backwardation",
            100 * (0.90 + 0.10 * np.exp(-tau / 0.45)),
            TEAL,
            months,
        )
    )
    glut = 100 * np.exp((0.0375 + 0.04) * tau) + 30 * np.exp(-((months - 1) ** 2) / 1.6) * (-1)
    panels.append(
        (
            "Crude oil, storage full",
            "storage itself is scarce: the front\ncollapses below the deferred months",
            glut,
            RUST,
            months,
        )
    )
    season = 3.4 * np.exp(0.0375 * tau) * (1 + 0.16 * np.cos(2 * np.pi * (months - 3) / 12))
    panels.append(
        (
            "Natural gas (first month November)",
            "seasonal storage and demand:\nwinter months rich, summer cheap",
            season / season[0] * 100,
            NAVY,
            months,
        )
    )
    vmonths = np.arange(1, 9)
    vix = 16.0 + 3.5 * (1 - np.exp(-(vmonths - 1) / 2.5))
    panels.append(
        (
            "VIX futures, calm market",
            "no carry relation: expectation plus\na volatility risk premium",
            vix / 15.0 * 100,
            RUST,
            vmonths,
        )
    )

    for ax, (title, sub, curve, colour, xs) in zip(axes.flat, panels):
        ax.plot(xs, curve, "o-", color=colour, lw=1.8, ms=3.8)
        ax.axhline(100, color=FAINT, lw=1.0, zorder=0)
        ax.set_title(title, fontsize=10.2, color=INK, loc="left")
        ax.text(0.03, 0.04, sub, transform=ax.transAxes, fontsize=8.2, color=MUTED, va="bottom")
        lo, hi = curve.min(), curve.max()
        pad = max(1.2, 0.35 * (hi - lo))
        ax.set_ylim(min(lo, 100) - pad * 1.9, max(hi, 100) + pad * 0.6)
        ax.set_xticks(xs if len(xs) <= 8 else xs[::2])
        ax.tick_params(labelsize=8.2, colors=MUTED)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(FAINT)
    for ax in axes[1]:
        ax.set_xlabel("contract month", fontsize=8.8)
    for ax in axes[:, 0]:
        ax.set_ylabel("price (spot = 100)", fontsize=8.8)

    fig.text(
        0.5,
        -0.03,
        "Stylised shapes, not market quotes. In every storable market the slope is the net cost of carry: "
        "financing and storage push the curve up,\nincome and convenience pull it down. The VIX has no such link, "
        "and its slope is mostly a premium paid to whoever is short.",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )
    fig.tight_layout()
    for ext in ("pdf", "svg"):
        fig.savefig(f"{OUT}.{ext}", transparent=True, bbox_inches="tight")


if __name__ == "__main__":
    main()

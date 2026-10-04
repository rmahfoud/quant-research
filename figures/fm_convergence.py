# Where carry is earned. Left: with the spot price pinned, a futures contract
# converges to it day by day, so a long in contango loses and a long in
# backwardation gains, with nothing happening at expiry or at a roll. Right: the
# same fact on the term structure: the contract slides down an unchanged curve as
# its maturity shrinks.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "fm_convergence"
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

OUT = Path(__file__).with_suffix("")
SPOT = 100.0
CARRY = 0.08  # 8% a year of net cost of carry, either sign


def main() -> None:
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.0, 4.3))

    days = np.linspace(90, 0, 300)
    tau = days / 365.0
    contango = SPOT * np.exp(CARRY * tau)
    backward = SPOT * np.exp(-CARRY * tau)
    ax.plot(days, np.full_like(days, SPOT), color=INK, lw=1.4, label="spot price (held constant)")
    ax.plot(days, contango, color=RUST, lw=2.0, label="futures in contango")
    ax.plot(days, backward, color=TEAL, lw=2.0, label="futures in backwardation")
    ax.invert_xaxis()
    ax.annotate(
        f"a long loses {contango[0] - SPOT:.2f}\nas the price falls to spot",
        xy=(45, SPOT * np.exp(CARRY * 45 / 365)),
        xytext=(62, 102.35),
        fontsize=8.5,
        color=RUST,
        ha="center",
        arrowprops=dict(arrowstyle="->", color=RUST, lw=1.0),
    )
    ax.annotate(
        f"a long gains {SPOT - backward[0]:.2f}\nas the price rises to spot",
        xy=(45, SPOT * np.exp(-CARRY * 45 / 365)),
        xytext=(62, 97.65),
        fontsize=8.5,
        color=TEAL,
        ha="center",
        arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.0),
    )
    ax.annotate(
        "at expiry the futures\nprice is the spot price",
        xy=(0.4, SPOT),
        xytext=(14, 98.35),
        fontsize=8.0,
        color=MUTED,
        ha="center",
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=0.9),
    )
    ax.set_xlabel("days to expiry", fontsize=9)
    ax.set_ylabel("price", fontsize=9)
    ax.set_title("Convergence: carry is paid daily, not at the roll", fontsize=10.5, color=INK, loc="left")
    ax.set_ylim(97.2, 102.8)
    ax.legend(fontsize=8.3, frameon=False, loc="upper right", bbox_to_anchor=(1.0, 0.93))

    mats = np.linspace(0, 12, 300)
    curve = SPOT * np.exp(CARRY * mats / 12.0)
    bx.plot(mats, curve, color=NAVY, lw=2.0, label="term structure today and next month (unchanged)")
    p3, p2 = SPOT * np.exp(CARRY * 3 / 12), SPOT * np.exp(CARRY * 2 / 12)
    bx.plot([3.0], [p3], "o", color=RUST, ms=8, zorder=5)
    bx.plot([2.0], [p2], "o", color=TEAL, ms=8, zorder=5)
    bx.annotate("", xy=(2.08, p2), xytext=(2.92, p3), arrowprops=dict(arrowstyle="->", color=RUST, lw=1.6))
    bx.text(3.25, p3 - 0.05, f"buy the 3-month contract at {p3:.2f}", fontsize=8.5, color=RUST, va="center")
    bx.annotate(
        f"a month later it is a 2-month contract;\non the same curve it is worth {p2:.2f}",
        xy=(2.0, p2 - 0.05),
        xytext=(5.6, 100.55),
        fontsize=8.5,
        color=TEAL,
        ha="center",
        va="center",
        arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.0),
    )
    bx.set_xlabel("months to expiry", fontsize=9)
    bx.set_ylabel("futures price", fontsize=9)
    bx.set_title("Roll-down: the contract moves, the curve does not", fontsize=10.5, color=INK, loc="left")
    bx.set_ylim(99.6, 108.8)
    bx.legend(fontsize=8.3, frameon=False, loc="upper left")

    for a in (ax, bx):
        a.tick_params(labelsize=8.5, colors=MUTED)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            a.spines[s].set_color(FAINT)

    fig.text(
        0.5,
        -0.05,
        "Both panels show the same 8%-a-year carry. With spot unchanged, a futures position earns or pays it "
        "continuously as the contract\nages toward expiry. Rolling into the next contract resets where on the "
        "curve you sit; it does not itself make or lose money.",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )
    fig.tight_layout()
    for ext in ("pdf", "svg"):
        fig.savefig(f"{OUT}.{ext}", transparent=True, bbox_inches="tight")


if __name__ == "__main__":
    main()

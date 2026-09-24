# The cost wall: the information coefficient a directional signal needs just to
# cover its round-trip cost, as a function of how long each position is held.
#
# A sign strategy on a signal whose correlation with the next-window return is
# rho earns, per trade, rho * sigma_h * sqrt(2/pi) when signal and return are
# jointly normal. It breaks even when that equals the round-trip cost c:
#
#     rho*(h) = (c / sigma_D) * sqrt(H / h) * sqrt(pi / 2)
#
# sigma_D is daily volatility, H = 390 trading minutes, and variance is spread
# evenly over trading time (overnight folded into sigma_D), which is accurate to
# a factor of about 1.5 at any single time of day.
#
#   Lines   — break-even IC for three cost-to-volatility ratios c / sigma_D.
#   Points  — published intraday effects at h = 30 minutes, IC = sqrt(R^2):
#             Baltussen et al. (2021), pooled equity index futures, rest of day
#             -> last half hour, R^2 = 2.45%; Gao et al. (2018), SPY, first
#             half hour -> last half hour, R^2 = 1.6%.
#   Band    — the monthly cross-sectional IC range the momentum deep dive calls
#             "genuinely useful" (0.02-0.05), at h = one month.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "im_cost_wall"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GOLD = "#9A6B00"
GREY = "#8A979D"

H = 390.0  # trading minutes per session
MONTH = 21 * H

CASES = (
    (0.005, TEAL, "c/σ = 0.005  (index futures: ~0.5 bp on ~1.1% a day)"),
    (0.02, GOLD, "c/σ = 0.02  (large-cap stock: ~3–4 bp on ~1.8%)"),
    (0.06, RUST, "c/σ = 0.06  (small-cap stock: ~15–20 bp on ~3%)"),
)

PUBLISHED = (
    ("A", "equity index futures, rest of day → last 30 min", np.sqrt(0.0245)),
    ("B", "SPY, first 30 min → last 30 min", np.sqrt(0.016)),
)


def breakeven(ratio: float, h: np.ndarray) -> np.ndarray:
    return ratio * np.sqrt(H / h) * np.sqrt(np.pi / 2)


def style(ax) -> None:
    ax.tick_params(labelsize=9, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)


def main() -> None:
    h = np.geomspace(1.0, MONTH, 400)
    fig, ax = plt.subplots(figsize=(8.2, 4.4))

    for ratio, color, label in CASES:
        ax.plot(h, breakeven(ratio, h), color=color, lw=2.0, label=label)

    ax.fill_between([MONTH / 1.35, MONTH * 1.0], 0.02, 0.05, color=GREY, alpha=0.25, linewidth=0)
    ax.text(MONTH, 0.068, "monthly momentum IC 0.02–0.05", fontsize=8.5, color=MUTED, ha="right", va="center")

    key = []
    for tag, label, ic in PUBLISHED:
        ax.scatter([30.0], [ic], s=34, color=INK, zorder=5, edgecolor="white", linewidth=0.6)
        ax.text(26.0, ic, tag, fontsize=9, color=INK, ha="right", va="center", fontweight="bold")
        key.append(f"{tag}  {label}  (IC {ic:.2f})")
    ax.text(
        330.0,
        0.62,
        "published intraday effects at 30 minutes:\n" + "\n".join(key),
        fontsize=8.5,
        color=INK,
        va="center",
        linespacing=1.5,
    )

    ticks = [1, 5, 30, H, 5 * H, MONTH]
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(ticks, labels=["1 min", "5 min", "30 min", "1 day", "1 week", "1 month"])
    ax.set_yticks(
        [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0],
        labels=["0.005", "0.01", "0.02", "0.05", "0.1", "0.2", "0.5", "1"],
    )
    ax.minorticks_off()
    ax.set_xlim(1.0, MONTH * 1.05)
    ax.set_ylim(0.004, 1.2)
    ax.set_xlabel("holding period per trade (trading time)", fontsize=10, color=MUTED)
    ax.set_ylabel("IC needed to cover round-trip cost", fontsize=10, color=MUTED)
    ax.set_title("The cost wall: break-even IC rises as 1/√(holding period)", fontsize=11, color=INK, loc="left", pad=8)
    ax.legend(frameon=False, fontsize=8.5, loc="lower left")
    style(ax)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    rows = (("1 min", 1.0), ("5 min", 5.0), ("30 min", 30.0), ("1 day", H), ("1 week", 5 * H), ("1 month", MONTH))
    print(f"{'horizon':>8}" + "".join(f"{f'c/sigma={r}':>14}" for r, _, _ in CASES))
    for name, minutes in rows:
        print(f"{name:>8}" + "".join(f"{breakeven(r, np.array(minutes)):>14.3f}" for r, _, _ in CASES))
    print(f"ratio of break-even IC, 30 min vs 1 month: {np.sqrt(MONTH / 30):.1f}")
    for tag, label, ic in PUBLISHED:
        print(f"published IC {ic:.3f}: {label}")


if __name__ == "__main__":
    main()

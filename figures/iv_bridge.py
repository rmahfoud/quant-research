# Where an option's implied variance "looks": the dollar-gamma weights.
#
# The hedged-P&L identity makes implied variance a weighted average of the
# variance priced in along the paths, with weight proportional to the option's
# dollar gamma at each (time, price) times the probability of being there. With
# Black–Scholes dynamics the product is exactly a Brownian bridge: a lens of
# probability that starts at today's price and ends at the strike on expiry.
#
#   Left  — the weight map for a 30-day at-the-money option (strike 100).
#   Right — the same for a 90-strike option: the lens tilts from spot to strike,
#           so the variance that matters is variance between 100 and 90.
#
# Each time slice is normalised to its own maximum so the shape is visible;
# the script also checks numerically that the product of density and dollar
# gamma equals the bridge density, and that the total weight per unit time is
# constant across the option's life.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import math
import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "iv_bridge"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

S0, VOL, DAYS = 100.0, 0.20, 30
T = DAYS / 365


def npdf(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)


def weights(strike: float, t: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Density of log-price at (t, x) times the dollar gamma of the strike there."""
    tt, xx = np.meshgrid(t, x, indexing="ij")
    mean = math.log(S0) - 0.5 * VOL**2 * tt
    density = npdf((xx - mean) / (VOL * np.sqrt(tt))) / (VOL * np.sqrt(tt))
    tau = T - tt
    d2 = (xx - math.log(strike) - 0.5 * VOL**2 * tau) / (VOL * np.sqrt(tau))
    dollar_gamma = strike * npdf(d2) / (VOL * np.sqrt(tau))
    return density * dollar_gamma


def bridge(strike: float, t: np.ndarray, x: np.ndarray) -> np.ndarray:
    tt, xx = np.meshgrid(t, x, indexing="ij")
    mean = math.log(S0) + (math.log(strike) - math.log(S0)) * tt / T
    sd = VOL * np.sqrt(tt * (T - tt) / T)
    return npdf((xx - mean) / sd) / sd


def style(ax) -> None:
    ax.tick_params(labelsize=9, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)


def main() -> None:
    cmap = LinearSegmentedColormap.from_list("teal_alpha", [(0.043, 0.431, 0.459, 0.0), (0.043, 0.431, 0.459, 0.95)])
    t = np.linspace(T / 400, T * (1 - 1 / 400), 300)
    x = np.linspace(math.log(80.0), math.log(115.0), 400)
    days = t * 365

    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.9), sharey=True)
    for ax, strike, title in (
        (axes[0], 100.0, "At the money: variance near 100 counts"),
        (axes[1], 90.0, "Strike 90: variance between 100 and 90"),
    ):
        w = weights(strike, t, x)
        b = bridge(strike, t, x)
        per_time = np.trapezoid(w, x, axis=1)
        norm = w / w.max(axis=1, keepdims=True)
        ax.pcolormesh(days, np.exp(x), norm.T, cmap=cmap, shading="auto", rasterized=True)
        line = np.exp(math.log(S0) + (math.log(strike) - math.log(S0)) * t / T)
        sd = VOL * np.sqrt(t * (T - t) / T)
        ax.plot(days, line, color=INK, lw=1.2)
        ax.plot(days, line * np.exp(sd), color=INK, lw=0.8, ls="--")
        ax.plot(days, line * np.exp(-sd), color=INK, lw=0.8, ls="--")
        ax.plot([0], [S0], "o", color=INK, ms=5, clip_on=False, zorder=5)
        ax.plot([DAYS], [strike], "o", color=RUST, ms=5, clip_on=False, zorder=5)
        ax.annotate("today's price", xy=(0, S0), xytext=(1.0, S0 + 4.2), fontsize=9, color=INK)
        ax.annotate("strike", xy=(DAYS, strike), xytext=(DAYS - 4.5, strike + 3.6), fontsize=9, color=RUST)
        ax.set_xlim(0, DAYS)
        ax.set_ylim(85, 109)
        ax.set_xlabel("days from today", fontsize=10, color=MUTED)
        ax.set_title(title, fontsize=11, color=INK, loc="left", pad=8)
        style(ax)

        bn = b / b.max(axis=1, keepdims=True)
        print(
            f"strike {strike}: max |weight/max - bridge/max| = {np.abs(norm - bn).max():.2e}; "
            f"weight per unit time min {per_time.min():.6f} max {per_time.max():.6f}"
        )
        # Share of total weight falling in each third of the option's life.
        thirds = [
            np.trapezoid(per_time[(t >= a) & (t < c)], t[(t >= a) & (t < c)])
            for a, c in ((0, T / 3), (T / 3, 2 * T / 3), (2 * T / 3, T))
        ]
        print(f"  weight by thirds of life: {[round(float(v / sum(thirds)), 3) for v in thirds]}")
        mid = int(np.argmin(np.abs(t - T / 2)))
        print(
            f"  at day 15 the one-sd band of the weights is {line[mid] * math.exp(-sd[mid]):.2f} to {line[mid] * math.exp(sd[mid]):.2f}"
        )

    axes[0].set_ylabel("underlying price", fontsize=10, color=MUTED)
    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight", dpi=200)


main()

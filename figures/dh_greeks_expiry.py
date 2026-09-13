# What happens to gamma as expiry approaches.
#
#   Left  — gamma against the underlying price for one strike at four times to
#           expiry. The curve narrows and its peak grows like 1/sqrt(time left):
#           the same open interest carries far more hedging need near expiry,
#           concentrated in a narrower band around the strike.
#   Right — gamma against days to expiry for an at-the-money option and for
#           options 2% and 5% out of the money. At the money, gamma grows without
#           bound; away from the money it peaks and then collapses to zero.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import math
import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "dh_greeks_expiry"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"
GOLD = "#B7791F"

K, VOL = 100.0, 0.20


def gamma(s: np.ndarray, tau: np.ndarray) -> np.ndarray:
    d1 = (np.log(s / K) + 0.5 * VOL**2 * tau) / (VOL * np.sqrt(tau))
    return np.exp(-0.5 * d1**2) / math.sqrt(2 * math.pi) / (s * VOL * np.sqrt(tau))


def style(ax) -> None:
    ax.tick_params(labelsize=9, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)


def main() -> None:
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.6, 3.9))

    s = np.linspace(90, 110, 600)
    for days, color, label in (
        (30, GREY, "30 days"),
        (7, TEAL, "7 days"),
        (2, GOLD, "2 days"),
        (0.5, RUST, "half a day"),
    ):
        axL.plot(s, gamma(s, days / 365), color=color, lw=2.0, label=label)
    axL.set_xlabel("underlying price (strike 100)", fontsize=10, color=MUTED)
    axL.set_ylabel("gamma (delta change per $1)", fontsize=10, color=MUTED)
    axL.set_title("Gamma narrows and spikes into expiry", fontsize=11, color=INK, loc="left", pad=8)
    axL.legend(frameon=False, fontsize=9.5, loc="upper right")
    axL.set_xlim(90, 110)
    style(axL)

    days = np.linspace(30, 0.05, 800)
    for spot, color, label in (
        (100.0, RUST, "at the money"),
        (102.0, GOLD, "2% from strike"),
        (105.0, TEAL, "5% from strike"),
    ):
        axR.plot(days, gamma(np.full_like(days, spot), days / 365), color=color, lw=2.0, label=label)
    axR.set_xlim(30, 0)
    axR.set_ylim(0, 0.45)
    axR.set_xlabel("days to expiry", fontsize=10, color=MUTED)
    axR.set_title("At the money it explodes; away, it dies", fontsize=11, color=INK, loc="left", pad=8)
    axR.legend(frameon=False, fontsize=9.5, loc="upper left")
    style(axR)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print("ATM gamma by days to expiry:")
    for d in (30, 7, 2, 1, 0.5, 0.25):
        print(f"  {d:>5} days: {float(gamma(np.array(100.0), d / 365)):.4f}")
    for spot in (102.0, 105.0):
        g = gamma(np.full_like(days, spot), days / 365)
        i = int(np.argmax(g))
        print(
            f"{spot}: peak gamma {g[i]:.4f} at {days[i]:.2f} days; at 30d {float(gamma(np.array(spot), 30 / 365)):.4f}; "
            f"at 0.25d {float(gamma(np.array(spot), 0.25 / 365)):.6f}"
        )


main()

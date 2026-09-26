# Pinning and its mirror image, on the last trading day before expiry.
#
# A stock starts the day near a strike of 100 that carries large open interest.
# Dealers hold that open interest either long (they bought the options) or short
# (they sold them), and re-hedge to delta-neutral every minute. Their trades move
# the price linearly, and no single minute's hedge trade can exceed a fixed share
# of the market's volume. Everything else is a random walk.
#
# Long dealers sell into rallies above the strike and buy dips below it, and the
# closer expiry gets the harder they do so: the closing price is pulled onto the
# strike. Short dealers do the opposite and the close is pushed away from it.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import math
import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "dh_pinning"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

K = 100.0
VOL = 0.25
MINUTES = 390
PATHS = 6000
DAY_YEARS = 1 / 252
POSITION = 400_000  # option-equivalent shares held by dealers at the strike
IMPACT = 1.0e-6  # $ of price move per share traded
MAX_TRADE = 60_000  # most shares the hedger can trade in one minute


def erf(x: np.ndarray) -> np.ndarray:
    # Abramowitz and Stegun 7.1.26, accurate to 1.5e-7.
    sign = np.sign(x)
    x = np.abs(x)
    t = 1.0 / (1.0 + 0.3275911 * x)
    poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))))
    return sign * (1.0 - poly * np.exp(-x * x))


def call_delta(s: np.ndarray, tau: float) -> np.ndarray:
    if tau <= 0:
        return (s > K).astype(float)
    d1 = (np.log(s / K) + 0.5 * VOL**2 * tau) / (VOL * math.sqrt(tau))
    return 0.5 * (1.0 + erf(d1 / math.sqrt(2)))


def simulate(rng: np.random.Generator, sign: int) -> np.ndarray:
    s = K + rng.normal(0.0, 0.8, PATHS)
    dt = DAY_YEARS / MINUTES
    held = -sign * POSITION * call_delta(s, DAY_YEARS)
    for m in range(1, MINUTES + 1):
        tau = DAY_YEARS * (1 - m / MINUTES)
        z = rng.standard_normal(PATHS)
        s = s * np.exp(-0.5 * VOL**2 * dt + VOL * math.sqrt(dt) * z)
        if sign == 0:
            continue
        target = -sign * POSITION * call_delta(s, max(tau, dt / 10))
        trade = np.clip(target - held, -MAX_TRADE, MAX_TRADE)
        held += trade
        s = s + IMPACT * trade
    return s


def main() -> None:
    rng = np.random.default_rng(20260914)
    closes = {name: simulate(rng, sign) - K for name, sign in (("none", 0), ("long", +1), ("short", -1))}

    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    bins = np.linspace(-4, 4, 81)
    ax.hist(closes["none"], bins=bins, color=GREY, alpha=0.55, label="no hedging dealers")
    ax.hist(closes["long"], bins=bins, histtype="step", color=TEAL, lw=2.0, label="dealers long gamma: pinned")
    ax.hist(closes["short"], bins=bins, histtype="step", color=RUST, lw=2.0, label="dealers short gamma: repelled")
    ax.axvline(0, color=INK, lw=1.0, ls=":")
    ax.set_xlim(-4, 4)
    ax.set_xlabel("closing price minus strike on expiry day ($)", fontsize=10, color=MUTED)
    ax.set_ylabel("number of simulated days", fontsize=10, color=MUTED)
    ax.set_title("Where the price closes on expiry day, strike 100", fontsize=11, color=INK, loc="left", pad=8)
    ax.legend(frameon=False, fontsize=9.5, loc="upper left")
    ax.tick_params(labelsize=9, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    for name, x in closes.items():
        print(
            f"{name:>5}: P(|close-K| < 0.10) = {np.mean(np.abs(x) < 0.10):.3f}, "
            f"P(< 0.25) = {np.mean(np.abs(x) < 0.25):.3f}, sd = {x.std():.3f}"
        )
    np.array([K])
    gamma_open = POSITION * math.exp(0) / (K * VOL * math.sqrt(DAY_YEARS)) / math.sqrt(2 * math.pi)
    print(
        f"dealer gamma at the strike at the open: {gamma_open:,.0f} shares per $1; "
        f"impact x gamma = {IMPACT * gamma_open:.3f}; one-minute cap {MAX_TRADE:,} shares"
    )


main()

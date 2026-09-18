# A smile is a probability distribution written in lognormal units.
#
#   Left  — three 30-day smiles with the same 20% at-the-money volatility:
#           flat, a skew of the kind equity indices show, and a symmetric smile.
#   Right — the risk-neutral density of the price at expiry implied by each,
#           recovered by Breeden–Litzenberger (the second strike-derivative of
#           call prices). The flat smile is exactly lognormal; the skew moves
#           mass into the left tail and pushes the peak to the right; the
#           symmetric smile fattens both tails and sharpens the peak.
#
# Smiles are raw SVI slices in total variance. Prints the moments of each
# density, probabilities read correctly and naively off the smile, and a check
# that the variance-swap strike from the 1/K^2 option strip matches the
# normal-weighted average of implied variance across the smile.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import math
import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "iv_smile_density"
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

F = 100.0
T = 30 / 365
SMILES = {
    "flat": None,
    "skew": (0.00134, 0.030, -0.55, 0.02, 0.05),
    "smile": (0.002118, 0.0234, 0.0, 0.0, 0.05),
}

_erf = np.vectorize(math.erf)


def ncdf(x: np.ndarray | float) -> np.ndarray:
    return 0.5 * (1 + _erf(np.asarray(x, dtype=float) / math.sqrt(2)))


def npdf(x: np.ndarray | float) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    return np.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)


def total_variance(name: str, k: np.ndarray) -> np.ndarray:
    params = SMILES[name]
    if params is None:
        return np.full_like(np.asarray(k, dtype=float), 0.20**2 * T)
    a, b, rho, m, s = params
    return a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + s**2))


def vol(name: str, strike: np.ndarray) -> np.ndarray:
    return np.sqrt(total_variance(name, np.log(np.asarray(strike, dtype=float) / F)) / T)


def call(strike: np.ndarray, sigma: np.ndarray) -> np.ndarray:
    s = sigma * math.sqrt(T)
    d1 = (np.log(F / strike) + 0.5 * s**2) / s
    return F * ncdf(d1) - strike * ncdf(d1 - s)


def style(ax) -> None:
    ax.tick_params(labelsize=9, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)


def main() -> None:
    dk = 0.01
    strikes = np.arange(30.0, 250.0 + dk / 2, dk)
    colors = {"flat": GREY, "skew": RUST, "smile": TEAL}
    labels = {"flat": "flat (lognormal)", "skew": "equity-index skew", "smile": "symmetric smile"}

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.6, 3.9))
    shown = (strikes >= 75) & (strikes <= 120)
    for name in ("flat", "skew", "smile"):
        sigma = vol(name, strikes)
        axL.plot(strikes[shown], 100 * sigma[shown], color=colors[name], lw=2.0, label=labels[name])
        c = call(strikes, sigma)
        density = np.gradient(np.gradient(c, dk), dk)
        axR.plot(strikes[shown], density[shown], color=colors[name], lw=2.0, label=labels[name])

        inner = (strikes > 35) & (strikes < 245)
        q, x = density[inner], strikes[inner]
        mass = np.trapezoid(q, x)
        mean = np.trapezoid(q * x, x) / mass
        r = np.log(x / F)
        mu = np.trapezoid(q * r, x) / mass
        sd = math.sqrt(np.trapezoid(q * (r - mu) ** 2, x) / mass)
        skew = np.trapezoid(q * (r - mu) ** 3, x) / mass / sd**3
        kurt = np.trapezoid(q * (r - mu) ** 4, x) / mass / sd**4 - 3
        # Probabilities are digitals: the first strike-derivative of the price
        # curve, which is far better conditioned than integrating the density.
        slope = np.gradient(c, dk)
        below90 = 1 + float(np.interp(90.0, strikes, slope))
        above105 = -float(np.interp(105.0, strikes, slope))
        s90, s105 = float(vol(name, np.array(90.0))), float(vol(name, np.array(105.0)))
        d2_90 = (math.log(F / 90) - 0.5 * s90**2 * T) / (s90 * math.sqrt(T))
        d2_105 = (math.log(F / 105) - 0.5 * s105**2 * T) / (s105 * math.sqrt(T))
        mode = x[np.argmax(q)]
        print(
            f"{name:6s}: mass {mass:.4f} mean {mean:.3f} mode {mode:.2f} | log-return sd {100 * sd:.3f}% "
            f"skew {skew:+.3f} excess kurt {kurt:+.3f} | P(S<90) {100 * below90:.2f}% vs naive N(-d2) {100 * float(ncdf(-d2_90)):.2f}% "
            f"| P(S>105) {100 * above105:.2f}% vs naive N(d2) {100 * float(ncdf(d2_105)):.2f}% | vol(90) {100 * s90:.2f} vol(105) {100 * s105:.2f}"
        )

        # Variance swap: the 1/K^2 strip of out-of-the-money options, and the
        # normal-weighted average of implied variance over z = -d2.
        otm = np.where(strikes < F, c - (F - strikes), c)
        kvar = 2 / T * np.trapezoid(otm / strikes**2, strikes)
        k = np.log(strikes / F)
        w = total_variance(name, k)
        z = k / np.sqrt(w) + 0.5 * np.sqrt(w)
        order = np.argsort(z)
        gatheral = np.trapezoid((w / T)[order] * npdf(z[order]), z[order])
        print(
            f"        ATM vol {100 * float(vol(name, np.array(F))):.3f}%  variance-swap vol from strip {100 * math.sqrt(kvar):.3f}%  "
            f"from normal-weighted smile {100 * math.sqrt(gatheral):.3f}%"
        )

    for strike in (80, 90, 95, 105, 110, 120):
        print(
            f"skew smile vol at {strike}: {100 * float(vol('skew', np.array(float(strike)))):.2f}%   symmetric: {100 * float(vol('smile', np.array(float(strike)))):.2f}%"
        )
    ks = np.array([99.0, 101.0])
    slope = np.diff(100 * vol("skew", ks))[0] / 2
    print(f"skew smile ATM slope: {slope:.3f} vol points per 1 strike point")

    axL.set_xlim(75, 120)
    axL.set_ylim(10, 45)
    axL.set_xlabel("strike (forward 100)", fontsize=10, color=MUTED)
    axL.set_ylabel("30-day implied volatility (%)", fontsize=10, color=MUTED)
    axL.set_title("Three smiles, same at-the-money level", fontsize=11, color=INK, loc="left", pad=8)
    axL.legend(frameon=False, fontsize=9.5, loc="upper right")
    style(axL)

    axR.set_xlim(75, 120)
    axR.set_ylim(0, None)
    axR.set_xlabel("price at expiry", fontsize=10, color=MUTED)
    axR.set_ylabel("risk-neutral density (per $1)", fontsize=10, color=MUTED)
    axR.set_title("The distributions they encode", fontsize=11, color=INK, loc="left", pad=8)
    axR.annotate(
        "skew: fatter left tail,\npeak pushed right",
        xy=(84, 0.0065),
        xytext=(76, 0.045),
        fontsize=9,
        color=RUST,
        arrowprops=dict(arrowstyle="->", color=RUST, lw=0.9),
    )
    style(axR)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")


main()

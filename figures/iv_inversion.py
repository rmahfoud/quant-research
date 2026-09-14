# Implied volatility as a change of units, and where that change is ill-conditioned.
#
#   Left  — Black–Scholes call price against volatility for three strikes on a
#           30-day option. Each curve rises monotonically, so every price in the
#           no-arbitrage range corresponds to exactly one volatility: implied
#           volatility is the price read backwards through the curve.
#   Right — how many volatility points a $0.05 error in the option price
#           becomes, by strike, at three maturities (flat 20% volatility). The
#           error is price error divided by vega, so it explodes in the wings
#           and at short maturities, where vega is small.
#
# Also prints the numbers quoted in the text: Newton iterations from the
# at-the-money approximation, the call–put volatility gap created by a wrong
# forward, and the effect of the clock used for an intraday option.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import math
import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "iv_inversion"
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
TAU = 30 / 365

_erf = np.vectorize(math.erf)


def ncdf(x: np.ndarray | float) -> np.ndarray:
    return 0.5 * (1 + _erf(np.asarray(x, dtype=float) / math.sqrt(2)))


def npdf(x: np.ndarray | float) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    return np.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)


def call(f: float, k: np.ndarray | float, tau: float, vol: np.ndarray | float) -> np.ndarray:
    s = np.asarray(vol, dtype=float) * math.sqrt(tau)
    d1 = (np.log(f / np.asarray(k, dtype=float)) + 0.5 * s**2) / s
    return f * ncdf(d1) - np.asarray(k, dtype=float) * ncdf(d1 - s)


def put(f: float, k: np.ndarray | float, tau: float, vol: np.ndarray | float) -> np.ndarray:
    return call(f, k, tau, vol) - (f - np.asarray(k, dtype=float))


def vega(f: float, k: np.ndarray | float, tau: float, vol: np.ndarray | float) -> np.ndarray:
    s = np.asarray(vol, dtype=float) * math.sqrt(tau)
    d1 = (np.log(f / np.asarray(k, dtype=float)) + 0.5 * s**2) / s
    return f * npdf(d1) * math.sqrt(tau)


def implied_newton(price: float, f: float, k: float, tau: float, guess: float, steps: int = 6) -> list[float]:
    path = [guess]
    vol = guess
    for _ in range(steps):
        v = float(vega(f, k, tau, vol)) if vol > 0 else 0.0
        if v < 1e-12:
            break
        vol = vol - (float(call(f, k, tau, vol)) - price) / v
        path.append(vol)
    return path


def style(ax) -> None:
    ax.tick_params(labelsize=9, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)


def main() -> None:
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.6, 3.9))

    vols = np.linspace(0.005, 0.60, 400)
    axL.plot(vols * 100, put(F, 90.0, TAU, vols), color=GOLD, lw=2.0, label="90 put")
    axL.plot(vols * 100, call(F, 100.0, TAU, vols), color=TEAL, lw=2.0, label="100 call")
    axL.plot(vols * 100, call(F, 110.0, TAU, vols), color=RUST, lw=2.0, label="110 call")
    market = float(call(F, 100.0, TAU, 0.20))
    axL.plot([0, 20], [market, market], color=INK, lw=1.0, ls="--")
    axL.plot([20, 20], [0, market], color=INK, lw=1.0, ls="--")
    axL.plot([20], [market], "o", color=INK, ms=5)
    axL.annotate("market price 2.29", xy=(1, market), xytext=(1.5, market + 0.55), fontsize=9, color=INK)
    axL.annotate("implied volatility 20%", xy=(20, 0), xytext=(21.5, 1.65), fontsize=9, color=INK)
    axL.set_xlim(0, 60)
    axL.set_ylim(0, 8)
    axL.set_xlabel("volatility (%)", fontsize=10, color=MUTED)
    axL.set_ylabel("30-day option price ($, forward 100)", fontsize=10, color=MUTED)
    axL.set_title("The price curve, read backwards", fontsize=11, color=INK, loc="left", pad=8)
    axL.legend(frameon=False, fontsize=9.5, loc="upper left")
    style(axL)

    strikes = np.linspace(70, 130, 601)
    for days, color, label in ((7, RUST, "7 days"), (30, TEAL, "30 days"), (180, GOLD, "180 days")):
        tau = days / 365
        err = 100 * 0.05 / vega(F, strikes, tau, 0.20)
        axR.semilogy(strikes, err, color=color, lw=2.0, label=label)
    axR.axhline(1.0, color=GREY, lw=0.8, ls=":")
    axR.text(112.5, 1.12, "one volatility point", fontsize=9, color=MUTED)
    axR.set_ylim(0.05, 100)
    axR.set_xlim(70, 130)
    axR.set_yticks([0.1, 1, 10, 100], labels=["0.1", "1", "10", "100"])
    axR.minorticks_off()
    axR.set_xlabel("strike (forward 100, volatility 20%)", fontsize=10, color=MUTED)
    axR.set_ylabel("vol points from a $0.05 price error", fontsize=10, color=MUTED)
    axR.set_title("Where vega is small, noise is large", fontsize=11, color=INK, loc="left", pad=8)
    axR.legend(frameon=False, fontsize=9.5, loc="lower left")
    style(axR)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print(f"ATM 30d call at 20%: {market:.4f}; vega per vol point {float(vega(F, 100.0, TAU, 0.20)) / 100:.4f}")
    guess = market / (0.4 * F * math.sqrt(TAU))
    exact_factor = market / (F * 0.20 * math.sqrt(TAU))
    print(f"ATM shortcut guess C/(0.4 F sqrt(tau)) = {guess:.5f}; exact C/(F sigma sqrt(tau)) = {exact_factor:.5f}")
    print("Newton from shortcut:", [f"{v:.8f}" for v in implied_newton(market, F, 100.0, TAU, guess, 3)])
    p110 = float(call(F, 110.0, TAU, 0.25))
    print(f"110 call at 25%: price {p110:.5f}")
    print("Newton on 110 call from 20%:", [f"{v:.8f}" for v in implied_newton(p110, F, 110.0, TAU, 0.20, 5)])
    mk = math.sqrt(2 * abs(math.log(F / 110.0)) / TAU)
    print(f"Manaster-Koehler inflection start for 110: {mk:.4f}")
    print("Newton on 110 call from inflection:", [f"{v:.6f}" for v in implied_newton(p110, F, 110.0, TAU, mk, 6)])
    print(
        f"vega of 110 call at 5%: {float(vega(F, 110.0, TAU, 0.05)):.3e}; at 10%: {float(vega(F, 110.0, TAU, 0.10)):.4f}"
    )
    print("Newton on 110 call from 10%:", [f"{v:.4f}" for v in implied_newton(p110, F, 110.0, TAU, 0.10, 4)])

    print("vol-point error from a $0.05 price error (flat 20%):")
    for days in (7, 30, 180):
        tau = days / 365
        row = []
        for k in (80, 90, 95, 100, 105, 110, 120):
            e = 100 * 0.05 / float(vega(F, k, tau, 0.20))
            px = float(put(F, k, tau, 0.20)) if k < 100 else float(call(F, k, tau, 0.20))
            row.append(f"K{k}: {e:7.2f}vp (otm px {px:.3f})")
        print(f"  {days:3d}d  " + "  ".join(row))

    # A wrong forward: price the market at F=100, invert at F=99.5.
    true_c = float(call(F, 100.0, TAU, 0.20))
    true_p = float(put(F, 100.0, TAU, 0.20))
    lo, hi = 0.01, 1.0
    for name, price, fn in (("call", true_c, call), ("put", true_p, put)):
        a, b = lo, hi
        for _ in range(100):
            mid = 0.5 * (a + b)
            if float(fn(99.5, 100.0, TAU, mid)) > price:
                b = mid
            else:
                a = mid
        print(f"forward misestimated at 99.5: {name} implied vol {100 * mid:.3f}%")

    cal = 6 / (365 * 24)
    trd = 6 / (252 * 6.5)
    print(
        f"six hours as calendar years {cal:.6f}, as trading years {trd:.6f}, ratio {trd / cal:.3f}, vol ratio {math.sqrt(trd / cal):.3f}"
    )
    straddle = true_c + true_p
    print(
        f"ATM straddle {straddle:.4f}; sd of move {100 * 0.20 * math.sqrt(TAU):.4f}; sqrt(2/pi)*sd {100 * 0.20 * math.sqrt(TAU) * math.sqrt(2 / math.pi):.4f}"
    )


main()

# What a delta-hedged short option actually earns, by simulation.
#
#   Left  — a dealer sells a 30-day at-the-money call at 20% implied volatility
#           and hedges it once a day. Each dot is one simulated path whose true
#           volatility is drawn between 5% and 40%. The P&L is a bet on realised
#           volatility: the line is the exact expectation, BS(implied) minus
#           BS(realised), and the scatter around it is hedging error.
#   Right — with realised volatility equal to implied (a fairly priced option),
#           the hedged P&L has mean zero but not zero spread. Its standard
#           deviation falls like 1/sqrt(number of rehedges), matching the
#           Derman-Kamal approximation sqrt(pi/4) * vega * sigma / sqrt(N).
#
# Every calendar day is treated as a trading day, and rates and dividends are
# zero, so that nothing but gamma and theta is on the page.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import math
import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "dh_hedge_pnl"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

S0, K, IMPLIED, DAYS = 100.0, 100.0, 0.20, 30
T = DAYS / 365

_erf = np.vectorize(math.erf)


def ncdf(x: np.ndarray) -> np.ndarray:
    return 0.5 * (1 + _erf(np.asarray(x) / math.sqrt(2)))


def call_price(s: np.ndarray | float, tau: float, vol: np.ndarray | float) -> np.ndarray:
    s = np.asarray(s, dtype=float)
    vol = np.asarray(vol, dtype=float)
    d1 = (np.log(s / K) + 0.5 * vol**2 * tau) / (vol * np.sqrt(tau))
    return s * ncdf(d1) - K * ncdf(d1 - vol * np.sqrt(tau))


def call_delta(s: np.ndarray, tau: float, vol: float) -> np.ndarray:
    d1 = (np.log(s / K) + 0.5 * vol**2 * tau) / (vol * math.sqrt(tau))
    return ncdf(d1)


def hedged_short_call(rng: np.random.Generator, realised: np.ndarray, steps: int) -> np.ndarray:
    dt = T / steps
    paths = len(realised)
    s = np.full(paths, S0)
    pnl = np.full(paths, float(call_price(S0, T, IMPLIED)))
    for k in range(steps):
        tau = T - k * dt
        hedge = call_delta(s, tau, IMPLIED)
        z = rng.standard_normal(paths)
        s_next = s * np.exp(-0.5 * realised**2 * dt + realised * math.sqrt(dt) * z)
        pnl += hedge * (s_next - s)
        s = s_next
    return pnl - np.maximum(s - K, 0.0)


def style(ax) -> None:
    ax.tick_params(labelsize=9, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)


def main() -> None:
    rng = np.random.default_rng(20260912)
    premium = float(call_price(S0, T, IMPLIED))
    d1 = 0.5 * IMPLIED * math.sqrt(T)
    vega = S0 * math.sqrt(T) * math.exp(-0.5 * d1**2) / math.sqrt(2 * math.pi)

    realised = rng.uniform(0.05, 0.40, 2500)
    pnl = hedged_short_call(rng, realised, DAYS)
    grid = np.linspace(0.05, 0.40, 200)
    expected = premium - call_price(S0, T, grid)

    steps_list = [2, 4, 8, 15, 30, 60, 120, 240, 480]
    stds = []
    for steps in steps_list:
        errs = hedged_short_call(rng, np.full(20000, IMPLIED), steps)
        stds.append(errs.std())
    stds = np.array(stds)
    dk = math.sqrt(math.pi / 4) * vega * IMPLIED / np.sqrt(steps_list)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.6, 3.9))

    axL.axhline(0, color=GREY, lw=0.8)
    axL.axvline(IMPLIED * 100, color=GREY, lw=0.8, ls=":")
    axL.scatter(realised * 100, pnl, s=5, color=TEAL, alpha=0.35, linewidths=0)
    axL.plot(grid * 100, expected, color=INK, lw=2.0, label="expected: BS(20%) − BS(realised)")
    axL.set_xlabel("realised volatility over the option's life (%)", fontsize=10, color=MUTED)
    axL.set_ylabel("hedged P&L per option ($)", fontsize=10, color=MUTED)
    axL.set_title("Short gamma is a short position in volatility", fontsize=11, color=INK, loc="left", pad=8)
    axL.text(21, 1.9, "sold at 20%", fontsize=9, color=MUTED)
    axL.legend(frameon=False, fontsize=9.5, loc="lower left")
    style(axL)

    axR.loglog(steps_list, stds, "o", color=RUST, ms=5, label="simulated standard deviation")
    axR.loglog(steps_list, dk, color=INK, lw=1.6, label="√(π/4) · vega · σ / √N")
    axR.set_xticks([2, 8, 30, 120, 480], labels=["2", "8", "30", "120", "480"])
    axR.set_yticks([0.1, 0.2, 0.5, 1.0], labels=["0.1", "0.2", "0.5", "1.0"])
    axR.minorticks_off()
    axR.set_xlabel("number of rehedges over 30 days", fontsize=10, color=MUTED)
    axR.set_ylabel("hedging error, std ($ per option)", fontsize=10, color=MUTED)
    axR.set_title("Hedging error shrinks only like 1/√N", fontsize=11, color=INK, loc="left", pad=8)
    axR.legend(frameon=False, fontsize=9.5, loc="lower left")
    style(axR)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print(f"premium {premium:.4f}  vega per 1.00 vol {vega:.4f}")
    for lo, hi in ((0.05, 0.10), (0.10, 0.15), (0.15, 0.25), (0.25, 0.30), (0.30, 0.40)):
        m = (realised >= lo) & (realised < hi)
        print(
            f"realised {lo:.2f}-{hi:.2f}: mean pnl {pnl[m].mean():+.3f}, sd {pnl[m].std():.3f}, "
            f"share of paths losing {np.mean(pnl[m] < 0):.2f}"
        )
    for vol in (0.10, 0.20, 0.30):
        print(f"expected pnl at realised {vol:.2f}: {premium - float(call_price(S0, T, vol)):+.4f}")
    for steps, sd, approx in zip(steps_list, stds, dk, strict=True):
        print(f"N={steps:4d}: sd {sd:.4f} ({100 * sd / premium:5.1f}% of premium), Derman-Kamal {approx:.4f}")


main()

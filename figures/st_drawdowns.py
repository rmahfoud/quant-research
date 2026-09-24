# What a genuinely good strategy feels like from the inside. Simulate ten years
# of daily returns for strategies whose *true* Sharpe ratio is 0.3, 0.5 or 1.0,
# all at 10% annual volatility, and record the deepest drawdown and the longest
# spell below a previous peak. Nothing here is broken; every path is a strategy
# that works exactly as designed.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "st_drawdowns"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path
from statistics import NormalDist

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

VOL = 0.10
YEARS = 10
DAYS = 252
PATHS = 20000
CHUNK = 1000


def path_stats(sr: float, rng: np.random.Generator) -> dict[str, np.ndarray]:
    mu, sd = sr * VOL / DAYS, VOL / np.sqrt(DAYS)
    mdd, under, losing_year, total = [], [], [], []
    for _ in range(PATHS // CHUNK):
        r = mu + sd * rng.standard_normal((CHUNK, YEARS * DAYS))
        logw = np.cumsum(np.log1p(r), axis=1)
        peak = np.maximum.accumulate(np.maximum(logw, 0.0), axis=1)
        dd = np.exp(logw - peak) - 1
        mdd.append(dd.min(axis=1))
        below = dd < 0
        longest = np.zeros(CHUNK)
        run = np.zeros(CHUNK)
        for t in range(below.shape[1]):
            run = np.where(below[:, t], run + 1, 0)
            longest = np.maximum(longest, run)
        under.append(longest / DAYS)
        yearly = r.reshape(CHUNK, YEARS, DAYS).sum(axis=2)
        losing_year.append((yearly < 0).mean(axis=1))
        total.append(logw[:, -1])
    return {
        "mdd": np.concatenate(mdd),
        "under": np.concatenate(under),
        "losing_year": np.concatenate(losing_year),
        "total": np.concatenate(total),
    }


def cusum_run_lengths(sr: float, mean: float, h: float, reps: int, rng: np.random.Generator) -> np.ndarray:
    """Months until a one-sided CUSUM, tuned to a strategy with Sharpe ratio sr, raises an alarm."""
    mu0, sd = sr * VOL / 12, VOL / np.sqrt(12)
    x = rng.normal(mean, sd, (reps, 6000))
    s, done, alive = np.zeros(reps), np.full(reps, 6000.0), np.ones(reps, bool)
    for m in range(x.shape[1]):
        s = np.maximum(0.0, s + mu0 / 2 - x[:, m])
        hit = alive & (s > h * sd)
        done[hit] = m + 1
        alive &= ~hit
        if not alive.any():
            break
    return done / 12


def cusum_table(rng: np.random.Generator) -> None:
    sr = 0.5
    print(f"\nCUSUM on monthly returns of a Sharpe-{sr} strategy; alarm threshold h in monthly sd")
    print(f"{'h':>4}{'false alarm, mean':>19}{'detect death, mean':>20}{'median':>8}{'1 in 10':>9}")
    for h in (8, 10, 12):
        working = cusum_run_lengths(sr, sr * VOL / 12, h, 3000, rng)
        dead = cusum_run_lengths(sr, 0.0, h, 3000, rng)
        print(f"{h:4d}{working.mean():17.1f}y{dead.mean():18.1f}y{np.median(dead):7.1f}y{np.quantile(dead, 0.9):8.1f}y")


def main() -> None:
    rng = np.random.default_rng(20260924)
    cases = [(0.3, RUST), (0.5, INK), (1.0, TEAL)]
    results = {sr: path_stats(sr, rng) for sr, _ in cases}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.8, 3.9))
    for sr, colour in cases:
        res = results[sr]
        depth = np.sort(-res["mdd"] * 100)
        ax1.plot(depth, np.linspace(0, 1, len(depth)), color=colour, lw=2.0, label=f"true Sharpe {sr}")
        spell = np.sort(res["under"])
        ax2.plot(spell, np.linspace(0, 1, len(spell)), color=colour, lw=2.0, label=f"true Sharpe {sr}")
    ax1.set_xlabel("deepest drawdown in 10 years (%)", fontsize=9, color=MUTED)
    ax2.set_xlabel("longest spell below a previous peak (years)", fontsize=9, color=MUTED)
    ax1.set_ylabel("share of ten-year paths at or below", fontsize=9, color=MUTED)
    ax1.set_xlim(0, 50)
    ax2.set_xlim(0, 10)
    for ax in (ax1, ax2):
        ax.set_ylim(0, 1)
        ax.axhline(0.5, color=GREY, lw=0.7, ls=":")
        ax.axhline(0.9, color=GREY, lw=0.7, ls=":")
        ax.tick_params(labelsize=8.5, colors=MUTED)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GREY)
    ax2.legend(fontsize=8.2, frameon=False, loc="lower right")
    fig.suptitle(
        "Ten years of a strategy that works, at 10% volatility  (20,000 simulated paths each)", fontsize=10, color=INK
    )
    fig.text(
        0.5,
        -0.03,
        "Dotted lines mark the median and the 90th percentile. Normal daily returns: real "
        "strategies have fatter tails, so these understate the pain.",
        ha="center",
        fontsize=8.2,
        color=MUTED,
    )
    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    nd = NormalDist()
    print(
        f"{'SR':>5}{'MDD med':>9}{'MDD p90':>9}{'under med':>11}{'under p90':>11}"
        f"{'P(lose yr)':>12}{'theory':>8}{'P(10y<0)':>10}{'theory':>8}"
    )
    for sr, _ in cases:
        res = results[sr]
        print(
            f"{sr:5.1f}{-np.median(res['mdd']):9.1%}{-np.quantile(res['mdd'], 0.1):9.1%}"
            f"{np.median(res['under']):11.1f}{np.quantile(res['under'], 0.9):11.1f}"
            f"{res['losing_year'].mean():12.1%}{nd.cdf(-sr):8.1%}"
            f"{(res['total'] < 0).mean():10.1%}"
            f"{nd.cdf(-(sr * VOL - VOL**2 / 2) * np.sqrt(YEARS) / VOL):8.1%}"
        )

    cusum_table(rng)


main()

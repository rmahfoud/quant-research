# The best of M backtests, when none of them has any skill. Each "strategy" is
# pure noise with a true Sharpe ratio of zero; we keep the one with the highest
# in-sample Sharpe ratio. Lines: the extreme-value approximation used by the
# deflated Sharpe ratio. Dots: Monte Carlo. The point is how quickly selection
# alone manufactures a Sharpe ratio that looks like a career.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "st_best_of_n"
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

EULER = 0.5772156649
Z = NormalDist().inv_cdf


def expected_max_z(n: int) -> float:
    """E[max of n iid standard normals], the approximation in Bailey & Lopez de Prado."""
    if n == 1:
        return 0.0
    return (1 - EULER) * Z(1 - 1 / n) + EULER * Z(1 - 1 / (n * np.e))


def simulate(n: int, years: int, reps: int, rng: np.random.Generator) -> float:
    months = 12 * years
    best = np.empty(reps)
    for i in range(reps):
        r = rng.standard_normal((months, n))
        sr = r.mean(axis=0) / r.std(axis=0, ddof=1) * np.sqrt(12)
        best[i] = sr.max()
    return float(best.mean())


def main() -> None:
    rng = np.random.default_rng(20260924)
    horizons = [(5, RUST), (10, INK), (20, TEAL)]
    grid = np.unique(np.round(np.logspace(0, 3, 120)).astype(int))
    marks = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]

    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    table = {}
    for years, colour in horizons:
        se = 1 / np.sqrt(years)
        theory = [se * expected_max_z(n) for n in grid]
        ax.plot(grid, theory, color=colour, lw=2.0, label=f"{years}-year backtest")
        sims = [simulate(n, years, 400 if n <= 200 else 120, rng) for n in marks]
        ax.scatter(marks, sims, s=24, color=colour, zorder=5, edgecolor="white", linewidth=0.6)
        table[years] = [(n, se * expected_max_z(n), s) for n, s in zip(marks, sims, strict=True)]

    for level, text in (
        (0.5, "0.5: a respectable long-run equity Sharpe ratio"),
        (1.0, "1.0: what gets a strategy funded"),
    ):
        ax.axhline(level, color=GREY, lw=0.8, ls=":")
        ax.text(1.05, level + 0.03, text, fontsize=7.8, color=MUTED)

    ax.set_xscale("log")
    ax.set_xlim(1, 1000)
    ax.set_xticks([1, 10, 100, 1000])
    ax.set_xticklabels(["1", "10", "100", "1,000"])
    ax.set_ylim(0, 1.6)
    ax.set_xlabel("number of strategy variants tried, M  (all with zero true skill)", fontsize=9.5, color=MUTED)
    ax.set_ylabel("expected best annualised Sharpe ratio", fontsize=9.5, color=MUTED)
    ax.set_title(
        "The best of M skill-less backtests  (lines: approximation, dots: simulation)", fontsize=10, color=INK, pad=10
    )
    ax.tick_params(labelsize=8.5, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)
    ax.legend(fontsize=8.5, frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.93))
    fig.text(
        0.5,
        -0.04,
        "Independent trials. Correlated variants behave like fewer independent ones, "
        "which lowers the curve but does not remove it.",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )
    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print(f"{'M':>6}" + "".join(f"{f'{y}y approx':>12}{f'{y}y sim':>10}" for y, _ in horizons))
    for i, n in enumerate(marks):
        row = "".join(f"{table[y][i][1]:12.2f}{table[y][i][2]:10.2f}" for y, _ in horizons)
        print(f"{n:6d}{row}")


main()

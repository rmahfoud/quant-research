# How the information ratio grows with breadth, and why it stops. A monthly
# cross-sectional strategy holds weights proportional to a standardised signal
# across N stocks. The signal's true information coefficient averages 0.05 but
# varies from month to month with standard deviation sigma_IC. Lines: the
# approximation IR = sqrt(12) * IC / sqrt(sigma_IC^2 + 1/N). Dots: simulation.
# sigma_IC = 0 is Grinold's fundamental law; any month-to-month variation in the
# IC puts a ceiling of sqrt(12) * IC / sigma_IC on the IR however many stocks
# are added.
#
# Run standalone:  uv run --no-project --with matplotlib python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "ei_breadth"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

IC = 0.05
MONTHS = 240
REPS = 40


def theory(n: np.ndarray, sigma_ic: float) -> np.ndarray:
    return np.sqrt(12) * IC / np.sqrt(sigma_ic**2 + (1 - IC**2) / n)


def simulate(n: int, sigma_ic: float, rng: np.random.Generator) -> float:
    irs = np.empty(REPS)
    for k in range(REPS):
        ic_t = IC + sigma_ic * rng.standard_normal(MONTHS)
        ic_t = np.clip(ic_t, -0.95, 0.95)
        s = rng.standard_normal((MONTHS, n))
        r = ic_t[:, None] * s + np.sqrt(1 - ic_t[:, None] ** 2) * rng.standard_normal((MONTHS, n))
        pnl = (s * r).mean(axis=1)
        irs[k] = pnl.mean() / pnl.std(ddof=1) * np.sqrt(12)
    return float(irs.mean())


def main() -> None:
    rng = np.random.default_rng(20261004)
    grid = np.logspace(1, 3, 200)
    marks = [10, 30, 100, 300, 1000]
    cases = [
        (0.0, INK, "IC constant (the fundamental law)"),
        (0.05, TEAL, "IC varies, sd 0.05 a month"),
        (0.10, RUST, "IC varies, sd 0.10 a month"),
    ]

    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    rows = {}
    for sigma, colour, label in cases:
        ax.plot(grid, theory(grid, sigma), color=colour, lw=2.0, label=label)
        sims = [simulate(n, sigma, rng) for n in marks]
        ax.scatter(marks, sims, s=26, color=colour, zorder=5, edgecolor="white", linewidth=0.6)
        if sigma > 0:
            cap = np.sqrt(12) * IC / sigma
            ax.axhline(cap, color=colour, lw=0.8, ls=":")
            ax.text(1000, cap + 0.08, f"ceiling {cap:.2f}", fontsize=8, color=colour, ha="right")
        rows[sigma] = [(n, float(theory(np.array([n]), sigma)[0]), s) for n, s in zip(marks, sims, strict=True)]

    ax.set_xscale("log")
    ax.set_xlim(10, 1000)
    ax.set_xticks([10, 30, 100, 300, 1000])
    ax.set_xticklabels(["10", "30", "100", "300", "1,000"])
    ax.set_ylim(0, 6.0)
    ax.set_xlabel("number of stocks, N  (rebalanced monthly; average IC 0.05)", fontsize=9.5, color=MUTED)
    ax.set_ylabel("annualised information ratio", fontsize=9.5, color=MUTED)
    ax.set_title("Breadth multiplies skill until the IC's own variability takes over", fontsize=10, color=INK, pad=10)
    ax.tick_params(labelsize=8.5, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)
    ax.legend(fontsize=8.5, frameon=False, loc="upper left")
    fig.text(
        0.5,
        -0.04,
        "Lines: IR = sqrt(12) x IC / sqrt(sd(IC)^2 + 1/N).  Dots: simulation, 20 years of months, "
        "averaged over 40 runs.  No costs, no constraints.",
        ha="center",
        fontsize=8.2,
        color=MUTED,
    )
    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print(f"{'N':>6}" + "".join(f"{f'sd {s:.2f} th':>14}{'sim':>8}" for s, _, _ in cases))
    for i, n in enumerate(marks):
        print(f"{n:6d}" + "".join(f"{rows[s][i][1]:14.2f}{rows[s][i][2]:8.2f}" for s, _, _ in cases))


main()

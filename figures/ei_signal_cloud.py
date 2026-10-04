# What an information coefficient looks like. Each panel is 3,000 forecast/outcome
# pairs drawn from a bivariate normal with the stated correlation, both standardised.
# Grey dots are the individual bets; the dark line joins the average outcome within
# each of twenty forecast bins. At IC = 0.05 the cloud is indistinguishable from
# noise point by point, and the signal shows up only in the averages.
#
# Run standalone:  uv run --no-project --with matplotlib python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "ei_signal_cloud"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

N = 3000
BINS = 20


def draw(rho: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    x = rng.standard_normal(N)
    y = rho * x + np.sqrt(1 - rho**2) * rng.standard_normal(N)
    return x, y


def binned(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    order = np.argsort(x)
    chunks_x = np.array_split(x[order], BINS)
    chunks_y = np.array_split(y[order], BINS)
    return np.array([c.mean() for c in chunks_x]), np.array([c.mean() for c in chunks_y])


def main() -> None:
    rng = np.random.default_rng(20261003)
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.3), sharey=True)
    for ax, rho in zip(axes, (0.05, 0.30), strict=True):
        x, y = draw(rho, rng)
        bx, by = binned(x, y)
        ax.scatter(x, y, s=4, color=GREY, alpha=0.35, linewidths=0)
        grid = np.linspace(-3.5, 3.5, 2)
        ax.plot(grid, rho * grid, color=RUST, lw=1.4, ls="--", label=f"true slope = IC = {rho:.2f}")
        ax.plot(bx, by, color=INK, lw=1.8, marker="o", ms=3.5, label="average outcome in each forecast bin")
        sample_ic = float(np.corrcoef(x, y)[0, 1])
        top = y[x > np.quantile(x, 0.9)].mean()
        bottom = y[x < np.quantile(x, 0.1)].mean()
        hit = float(np.mean(np.sign(x) == np.sign(y)))
        ax.set_title(f"IC = {rho:.2f}", fontsize=10.5, color=INK, pad=8)
        ax.text(
            0.03,
            0.04,
            f"sample IC {sample_ic:.3f}   hit rate {hit:.1%}\n"
            f"top-decile minus bottom-decile outcome {top - bottom:+.2f} sd",
            transform=ax.transAxes,
            fontsize=8.2,
            color=MUTED,
        )
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-3.6, 3.6)
        ax.set_xlabel("forecast (standardised)", fontsize=9.5, color=MUTED)
        ax.tick_params(labelsize=8.5, colors=MUTED)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GREY)
        print(
            f"IC {rho:.2f}: sample IC {sample_ic:.3f}, hit rate {hit:.3f}, "
            f"top-bottom decile spread {top - bottom:+.3f} sd, "
            f"binned-mean range {by.min():+.3f} to {by.max():+.3f}"
        )
    axes[0].set_ylabel("outcome (standardised)", fontsize=9.5, color=MUTED)
    axes[0].legend(fontsize=8.2, frameon=False, loc="upper left")
    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")


main()

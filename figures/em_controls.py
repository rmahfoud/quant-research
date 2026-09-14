# Good and bad controls: what "controlling for" a variable does depends on its
# causal position, not on how strongly it correlates with anything.
#
# In every scenario the causal effect of D on Y is 1. Each row is the estimated
# coefficient on D from 2,000 simulated samples of 1,000 observations: the dot
# is the mean, the bar the 5th-95th percentile range.
#
#   confounder  C -> D, C -> Y.        Omitting C biases; controlling fixes it;
#                                      controlling a noisy proxy fixes only part.
#   mediator    D -> M -> Y.           Omitting M gives the total effect (1);
#                                      controlling M leaves the direct part (0.2).
#   collider    D -> K <- Y.           Omitting K is right; controlling K, or
#                                      keeping only units with K > 0, is wrong.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "em_controls"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

N = 1000
TRIALS = 2000


def coef_on_first(y: np.ndarray, *regressors: np.ndarray) -> float:
    X = np.column_stack([np.ones(len(y)), *regressors])
    return float(np.linalg.lstsq(X, y, rcond=None)[0][1])


def main() -> None:
    rng = np.random.default_rng(20260913)
    rows: dict[str, list[float]] = {}

    def add(label: str, value: float) -> None:
        rows.setdefault(label, []).append(value)

    for _ in range(TRIALS):
        c = rng.standard_normal(N)
        d = 0.8 * c + rng.standard_normal(N)
        y = 1.0 * d + 1.0 * c + rng.standard_normal(N)
        proxy = c + rng.standard_normal(N)  # reliability 0.5
        add("confounder omitted", coef_on_first(y, d))
        add("confounder controlled", coef_on_first(y, d, c))
        add("noisy proxy of confounder controlled", coef_on_first(y, d, proxy))

        d = rng.standard_normal(N)
        m = 0.8 * d + rng.standard_normal(N)
        y = 0.2 * d + 1.0 * m + rng.standard_normal(N)
        add("mediator omitted", coef_on_first(y, d))
        add("mediator controlled", coef_on_first(y, d, m))

        d = rng.standard_normal(N)
        y = 1.0 * d + rng.standard_normal(N)
        k = d + y + 0.5 * rng.standard_normal(N)
        add("collider omitted", coef_on_first(y, d))
        add("collider controlled", coef_on_first(y, d, k))
        keep = k > 0
        add("sample selected on collider (K > 0)", coef_on_first(y[keep], d[keep]))

    order = [
        ("confounder omitted", RUST),
        ("confounder controlled", TEAL),
        ("noisy proxy of confounder controlled", RUST),
        ("mediator omitted", TEAL),
        ("mediator controlled", RUST),
        ("collider omitted", TEAL),
        ("collider controlled", RUST),
        ("sample selected on collider (K > 0)", RUST),
    ]

    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    ypos = np.arange(len(order))[::-1].astype(float)
    ypos[:3] += 0.6
    ypos[3:5] += 0.3
    ax.axvline(1.0, color=GREY, lw=1.2, ls="--")
    ax.text(1.02, ypos[-1] - 0.75, "true effect = 1", fontsize=9, color=MUTED)
    ax.axvline(0.0, color=GREY, lw=0.8, ls=":")

    print(f"{'scenario':40s} {'mean':>7} {'p5':>7} {'p95':>7}")
    for (label, colour), yv in zip(order, ypos):
        vals = np.array(rows[label])
        lo, hi = np.percentile(vals, [5, 95])
        ax.plot([lo, hi], [yv, yv], color=colour, lw=2.4, solid_capstyle="round")
        ax.plot(vals.mean(), yv, "o", color=colour, ms=7, mec="white", mew=0.8)
        ax.text(hi + 0.04, yv, f"{vals.mean():.2f}", fontsize=9, color=colour, va="center")
        print(f"{label:40s} {vals.mean():7.3f} {lo:7.3f} {hi:7.3f}")

    ax.set_xlim(-0.8, 1.75)
    ax.set_ylim(ypos[-1] - 0.9, ypos[0] + 0.5)
    ax.set_xticks([-0.5, 0, 0.5, 1.0, 1.5])
    ax.set_yticks(ypos)
    ax.set_yticklabels([label for label, _ in order], fontsize=9.5, color=INK)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("estimated coefficient on D", fontsize=10, color=MUTED)
    ax.set_title(
        "Controlling for a confounder removes bias; controlling for a mediator or collider creates it",
        fontsize=11,
        color=INK,
        loc="left",
        pad=8,
    )
    ax.tick_params(axis="x", labelsize=9, colors=MUTED)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GREY)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")


main()

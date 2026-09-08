# What the aspect ratio q = N/T does to a minimum-variance portfolio built on a
# sample covariance matrix. Theory curves are the large-(N,T) limits; the points
# are simulation. The headline is the top curve: realised volatility exceeds
# predicted volatility by a factor of 1/(1-q), with no misspecification at all.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "pc_risk_ratio"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

T = 500
TRIALS = 40


def true_cov(n: int, rng: np.random.Generator) -> np.ndarray:
    """One factor plus idiosyncratic risk — a realistic, well-conditioned truth."""
    beta = rng.uniform(0.6, 1.4, n)
    idio = rng.uniform(0.15, 0.35, n)
    return 0.16**2 * np.outer(beta, beta) + np.diag(idio**2)


def gmv(cov: np.ndarray) -> np.ndarray:
    one = np.ones(len(cov))
    w = np.linalg.solve(cov, one)
    return w / w.sum()


def simulate(n: int, rng: np.random.Generator) -> tuple[float, float, float]:
    cov = true_cov(n, rng)
    opt = 1.0 / (np.ones(n) @ np.linalg.solve(cov, np.ones(n)))
    pred, real = [], []
    for _ in range(TRIALS):
        sample = rng.multivariate_normal(np.zeros(n), cov, size=T)
        s = np.cov(sample, rowvar=False)
        w = gmv(s)
        pred.append(w @ s @ w)
        real.append(w @ cov @ w)
    return float(np.mean(pred)) / opt, float(np.mean(real)) / opt, opt


def main() -> None:
    rng = np.random.default_rng(20260907)

    grid = np.linspace(0.01, 0.82, 300)
    pred_theory = np.sqrt(1 - grid)
    real_theory = 1 / np.sqrt(1 - grid)
    ratio_theory = 1 / (1 - grid)

    ns = [10, 25, 50, 100, 150, 200, 250, 300, 350, 400]
    qs, pred_sim, real_sim = [], [], []
    for n in ns:
        p, r, _ = simulate(n, rng)
        qs.append(n / T)
        pred_sim.append(np.sqrt(p))
        real_sim.append(np.sqrt(r))

    qs = np.array(qs)
    pred_sim = np.array(pred_sim)
    real_sim = np.array(real_sim)

    fig, ax = plt.subplots(figsize=(7.8, 4.6))

    ax.axhline(1.0, color=GREY, lw=1.0, ls=":")

    ax.plot(grid, ratio_theory, color=RUST, lw=2.2, label="realised ÷ predicted  =  1/(1−q)")
    ax.plot(grid, real_theory, color=INK, lw=1.9, label="realised ÷ true optimum  =  1/√(1−q)")
    ax.plot(grid, pred_theory, color=TEAL, lw=1.9, label="predicted ÷ true optimum  =  √(1−q)")

    ax.scatter(qs, real_sim / pred_sim, s=26, color=RUST, zorder=5, edgecolor="white", linewidth=0.6)
    ax.scatter(qs, real_sim, s=26, color=INK, zorder=5, edgecolor="white", linewidth=0.6)
    ax.scatter(qs, pred_sim, s=26, color=TEAL, zorder=5, edgecolor="white", linewidth=0.6)

    for q_mark, label in ((0.1, "N=50\nT=500"), (0.5, "N=250\nT=500"), (0.8, "N=400\nT=500")):
        ax.axvline(q_mark, color=GREY, lw=0.8, ls="--", alpha=0.6)
        ax.text(q_mark + 0.008, 0.12, label, fontsize=7.5, color=MUTED, va="bottom")

    ax.set_xlabel("q = N / T", fontsize=9.5, color=MUTED)
    ax.set_ylabel("volatility ratio", fontsize=9.5, color=MUTED)
    ax.set_title(
        "Minimum-variance portfolio risk against the aspect ratio  (lines: theory, dots: simulation)",
        fontsize=10,
        color=INK,
        pad=10,
    )
    ax.set_xlim(0, 0.85)
    ax.set_ylim(0, 5.0)
    ax.tick_params(labelsize=8.5, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)
    ax.legend(fontsize=8.5, frameon=False, loc="upper left")

    fig.text(
        0.5,
        -0.04,
        "The optimiser is simultaneously understating its own risk and taking more of it. "
        "Both errors come from the same place, and they compound.",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print(f"{'q':>6} {'pred/opt':>10} {'real/opt':>10} {'real/pred':>10} {'theory':>8}")
    for q, p, r in zip(qs, pred_sim, real_sim):
        print(f"{q:6.2f} {p:10.3f} {r:10.3f} {r / p:10.3f} {1 / (1 - q):8.3f}")


main()

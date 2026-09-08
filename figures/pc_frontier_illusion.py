# The three frontiers. An optimiser fed sample estimates reports the dashed
# curve, actually delivers the lower solid curve, and the truth it was reaching
# for is in between. The gap between "estimated" and "realised" is the entire
# subject of the note; it is manufactured by estimation error alone, since the
# data here are drawn from the very model the optimiser assumes.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "pc_frontier_illusion"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"
FAINT = "#DCE4E6"

N = 50
T = 500
A = 252


def true_model(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """One market factor plus idiosyncratic risk; modest, realistic alphas."""
    beta = rng.uniform(0.6, 1.4, N)
    idio = rng.uniform(0.15, 0.35, N)
    sigma_m = 0.16
    cov = sigma_m**2 * np.outer(beta, beta) + np.diag(idio**2)
    mu = 0.05 * beta + rng.normal(0, 0.01, N)
    return mu, cov


def frontier(mu: np.ndarray, cov: np.ndarray, targets: np.ndarray) -> np.ndarray:
    """Fully invested minimum-variance weights for each target return."""
    inv = np.linalg.inv(cov)
    one = np.ones(N)
    a = one @ inv @ one
    b = one @ inv @ mu
    c = mu @ inv @ mu
    d = a * c - b**2
    out = np.empty((len(targets), N))
    for i, m in enumerate(targets):
        lam = (c - b * m) / d
        gam = (a * m - b) / d
        out[i] = inv @ (lam * one + gam * mu)
    return out


def risk_return(w: np.ndarray, mu: np.ndarray, cov: np.ndarray):
    ret = w @ mu
    vol = np.sqrt(np.einsum("ij,jk,ik->i", w, cov, w))
    return vol, ret


def main() -> None:
    rng = np.random.default_rng(20260907)
    mu, cov = true_model(rng)

    sample = rng.multivariate_normal(mu / A, cov / A, size=T)
    mu_hat = sample.mean(axis=0) * A
    cov_hat = np.cov(sample, rowvar=False) * A

    targets = np.linspace(0.02, 0.14, 60)

    w_true = frontier(mu, cov, targets)
    v_true, r_true = risk_return(w_true, mu, cov)

    w_hat = frontier(mu_hat, cov_hat, targets)
    v_est, r_est = risk_return(w_hat, mu_hat, cov_hat)  # what the optimiser reports
    v_real, r_real = risk_return(w_hat, mu, cov)  # what those weights deliver

    fig, ax = plt.subplots(figsize=(7.6, 4.6))

    ax.plot(v_est, r_est, color=RUST, lw=2.0, ls="--", label="Estimated — what the optimiser reports")
    ax.plot(v_true, r_true, color=TEAL, lw=2.2, label="True frontier — the best actually available")
    ax.plot(v_real, r_real, color=INK, lw=2.6, label="Realised — what those same weights deliver")

    top = -1
    ax.annotate(
        f"promises {r_est[top]:.0%} at {v_est[top]:.0%} vol",
        xy=(v_est[top], r_est[top]),
        xytext=(v_est[top] + 0.035, r_est[top] + 0.004),
        fontsize=8.5,
        color=RUST,
        arrowprops=dict(arrowstyle="->", color=RUST, lw=1.1),
    )
    ax.annotate(
        f"delivers {r_real[top]:.1%} at {v_real[top]:.0%} vol",
        xy=(v_real[top], r_real[top]),
        xytext=(v_real[top] + 0.055, r_real[top] - 0.012),
        fontsize=8.5,
        color=INK,
        arrowprops=dict(arrowstyle="->", color=INK, lw=1.1),
    )
    ax.annotate(
        "",
        xy=(v_real[top], r_real[top]),
        xytext=(v_est[top], r_est[top]),
        arrowprops=dict(arrowstyle="->", color=GREY, lw=1.3, ls=":"),
    )
    ax.text(
        v_est[top] - 0.004,
        (r_est[top] + r_real[top]) / 2,
        "the whole\nascent is\nestimation\nerror",
        fontsize=8.5,
        color=MUTED,
        va="center",
        ha="right",
    )

    sr_true = np.sqrt(mu @ np.linalg.solve(cov, mu))
    sr_est = np.sqrt(mu_hat @ np.linalg.solve(cov_hat, mu_hat))
    ax.text(
        0.985,
        0.06,
        f"maximum Sharpe ratio\nreported: {sr_est:.2f}      true: {sr_true:.2f}",
        transform=ax.transAxes,
        fontsize=8.5,
        color=MUTED,
        ha="right",
        va="bottom",
    )

    ax.set_xlabel("annualised volatility", fontsize=9.5, color=MUTED)
    ax.set_ylabel("annualised expected return", fontsize=9.5, color=MUTED)
    ax.set_title(
        f"The frontier illusion — N = {N} assets, T = {T} daily observations (q = {N / T:.2f})",
        fontsize=10.5,
        color=INK,
        pad=10,
    )
    ax.tick_params(labelsize=8.5, colors=MUTED)
    ax.set_xlim(left=0)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)
    ax.legend(fontsize=8.5, frameon=False, loc="upper left")

    fig.text(
        0.5,
        -0.04,
        "Returns are drawn from exactly the model the optimiser assumes, so every part of the gap is "
        "estimation error — none of it is misspecification.\nAsk the estimated frontier for more return "
        "and it hands you more leverage on noise: the realised curve barely moves.",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    j = np.argmin(np.abs(targets - 0.10))
    print(f"at target return {targets[j]:.3f}:")
    print(f"  estimated vol {v_est[j]:.4f}, realised vol {v_real[j]:.4f}, true-frontier vol {v_true[j]:.4f}")
    print(f"  realised/estimated vol ratio = {v_real[j] / v_est[j]:.2f}")
    print(f"  estimated Sharpe {r_est[j] / v_est[j]:.2f} vs realised {r_real[j] / v_real[j]:.2f}")
    print(f"  max abs weight, estimated frontier: {np.abs(w_hat[j]).max():.2f}; gross {np.abs(w_hat[j]).sum():.1f}")
    print(f"sample mean range: {mu_hat.min():.3f} to {mu_hat.max():.3f} (true: {mu.min():.3f} to {mu.max():.3f})")
    print(f"realised return range across the whole frontier: {r_real.min():.4f} to {r_real.max():.4f}")
    print(f"realised vol range: {v_real.min():.4f} to {v_real.max():.4f}")


main()

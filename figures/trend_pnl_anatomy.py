# The exact algebraic decomposition of an EWMA trend rule's P&L into a convex
# "trend energy" term and a "realised variance" cost, drawn on one simulated path.
#
#   sum_t x_t r_{t+1} = (x_T^2 - x_0^2)/(2a(1-a))
#                     + (2-a)/(2(1-a)) * sum_t x_t^2
#                     - a/(2(1-a))     * sum_t r_t^2
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
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

ALPHA = 0.04
N = 900


def path_with_trends(rng: np.random.Generator) -> np.ndarray:
    """Returns from a slowly mean-reverting hidden drift plus noise."""
    phi, sig_eps = 1 - 1 / 180, 0.010
    sig_eta = 0.11 * sig_eps * np.sqrt(1 - phi**2)
    mu = np.zeros(N)
    for i in range(1, N):
        mu[i] = phi * mu[i - 1] + rng.normal(0, sig_eta)
    return mu + rng.normal(0, sig_eps, N)


def main() -> None:
    rng = np.random.default_rng(20240401)
    r = path_with_trends(rng)

    x = np.zeros(N + 1)
    for i, rr in enumerate(r):
        x[i + 1] = (1 - ALPHA) * x[i] + ALPHA * rr
    x = x[:-1]

    pnl = np.cumsum(x * r)
    energy = (2 - ALPHA) / (2 * (1 - ALPHA)) * np.cumsum(x**2)
    variance = ALPHA / (2 * (1 - ALPHA)) * np.cumsum(r**2)
    gamma = (x**2 - x[0] ** 2) / (2 * ALPHA * (1 - ALPHA))

    fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(7.6, 5.6), height_ratios=[1.0, 1.25], sharex=True)
    fig.patch.set_alpha(0.0)
    for ax in (ax0, ax1):
        ax.patch.set_alpha(0.0)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GREY)
        ax.tick_params(colors=MUTED, labelsize=8.5, length=3)
        ax.grid(True, color=FAINT, linewidth=0.7)
        ax.set_axisbelow(True)

    t = np.arange(N)
    p = np.cumsum(r)
    ax0.plot(t, 100 * p, color=INK, linewidth=1.3)
    ax0.fill_between(t, 100 * p, 100 * p.min(), color=INK, alpha=0.05, linewidth=0)
    ax0.set_ylabel("cumulative\nlog price (%)", fontsize=9.5, color=MUTED)
    ax0.set_title(
        "One path: hidden drift plus noise, and where the trend rule's money comes from",
        fontsize=10.5,
        color=INK,
        loc="left",
        pad=9,
    )

    ax1.axhline(0, color=GREY, linewidth=0.9)
    ax1.plot(
        t, 1e4 * energy, color=TEAL, linewidth=1.5, label=r"trend energy  $+\frac{2-\alpha}{2(1-\alpha)}\sum x_t^2$"
    )
    ax1.plot(
        t,
        -1e4 * variance,
        color=RUST,
        linewidth=1.5,
        label=r"realised variance  $-\frac{\alpha}{2(1-\alpha)}\sum r_t^2$",
    )
    ax1.plot(
        t,
        1e4 * gamma,
        color=GREY,
        linewidth=1.2,
        linestyle=(0, (4, 2)),
        label=r"convexity term  $\frac{x_T^2-x_0^2}{2\alpha(1-\alpha)}$",
    )
    ax1.plot(t, 1e4 * pnl, color=INK, linewidth=2.1, label="cumulative P&L (their sum)")
    ax1.set_ylabel("contribution\n(bp of unit exposure)", fontsize=9.5, color=MUTED)
    ax1.set_xlabel("bar", fontsize=9.5, color=MUTED)
    leg = ax1.legend(loc="upper left", frameon=False, fontsize=9, labelcolor=INK, handlelength=2.4)
    for txt in leg.get_texts():
        txt.set_color(INK)

    ax1.annotate(
        "the two large terms nearly cancel;\nthe strategy lives on the residual",
        xy=(N * 0.86, 1e4 * pnl[int(N * 0.86)]),
        xytext=(N * 0.50, 1e4 * (-variance.max() * 0.42)),
        fontsize=8.8,
        color=MUTED,
        ha="center",
        arrowprops=dict(arrowstyle="->", color=GREY, linewidth=0.9),
    )

    fig.tight_layout()
    out = Path(__file__).with_suffix(".svg")
    fig.savefig(out, transparent=True, bbox_inches="tight")
    print(f"  wrote {out.name}")


if __name__ == "__main__":
    main()

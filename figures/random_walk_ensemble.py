"""Static snapshot of the random-walk ensemble figure, for PDF output.

The HTML build uses an interactive canvas version of the same picture; this
renders the equivalent still for LaTeX. Run from the repo root:

    uv run --no-project --with matplotlib python quant-research/figures/random_walk_ensemble.py
"""

import os
import pathlib

import matplotlib
import numpy as np

# Pin the PDF CreationDate so reruns are byte-identical and don't churn git.
os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

INK = "#10171B"
ROSE = "#A63D62"
TEAL = "#0B6E75"
FAINT = "#8A979D"
RULE = "#DCE4E6"

STEPS = 180
NPATHS = 140
T_SLICE = 96


def build_paths(seed: int = 20260801) -> np.ndarray:
    rng = np.random.default_rng(seed)
    steps = rng.choice([-1, 1], size=(NPATHS, STEPS))
    walks = np.zeros((NPATHS, STEPS + 1), dtype=np.int64)
    walks[:, 1:] = steps.cumsum(axis=1)
    return walks


def render(out_path: pathlib.Path) -> None:
    walks = build_paths()
    t = np.arange(STEPS + 1)

    fig, ax = plt.subplots(figsize=(7.2, 3.3))

    ax.axhline(0, color=RULE, lw=0.8, zorder=1)
    for sign in (1, -1):
        ax.plot(t, sign * np.sqrt(t), color=FAINT, lw=0.9, ls=(0, (3, 4)), alpha=0.75, zorder=2)

    for walk in walks[1:]:
        ax.plot(t, walk, color=INK, lw=0.6, alpha=0.09, zorder=3)

    vals = walks[:, T_SLICE]
    counts, edges = np.histogram(vals, bins=22)
    widths = counts / counts.max() * 26.0
    ax.barh(
        (edges[:-1] + edges[1:]) / 2,
        widths,
        height=np.diff(edges),
        left=T_SLICE + 1,
        color=TEAL,
        alpha=0.28,
        zorder=4,
    )

    ax.axvline(T_SLICE, color=TEAL, lw=1.4, zorder=5)
    ax.plot(t, walks[0], color=ROSE, lw=1.6, zorder=6)
    ax.plot([T_SLICE], [walks[0, T_SLICE]], "o", color=ROSE, ms=4.5, zorder=7)

    lim = 3.5 * np.sqrt(STEPS)
    ax.set_xlim(0, STEPS)
    ax.set_ylim(-lim, lim)
    ax.set_xlabel("t", style="italic", color=FAINT, fontsize=9)
    ax.tick_params(colors=FAINT, labelsize=8)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(RULE)

    handles = [
        plt.Line2D([], [], color=ROSE, lw=1.6, label="one ω — a single sample path"),
        plt.Line2D([], [], color=TEAL, lw=1.4, label=f"one t — the marginal of X_t (t = {T_SLICE})"),
        plt.Line2D([], [], color=FAINT, lw=0.9, ls=(0, (3, 4)), label="± √t (one standard deviation)"),
    ]
    ax.legend(
        handles=handles,
        loc="upper left",
        frameon=False,
        fontsize=7.5,
        labelcolor=FAINT,
        handlelength=1.8,
    )

    fig.tight_layout(pad=0.4)
    fig.savefig(out_path, format="pdf", transparent=True)
    plt.close(fig)


if __name__ == "__main__":
    out = pathlib.Path(__file__).parent / "random_walk_ensemble.pdf"
    render(out)
    print(f"wrote {out}")

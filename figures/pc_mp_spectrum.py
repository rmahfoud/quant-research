# Sample eigenvalue spectra against the Marchenko-Pastur law, for returns with
# no structure at all (left) and with a single market factor (right). The point
# of the pair: the bulk is noise whose shape is known in advance, and only the
# eigenvalues outside the bulk carry information.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "pc_mp_spectrum"
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

N = 200
T = 600
Q = N / T


def mp_support(q: float, var: float = 1.0) -> tuple[float, float]:
    return var * (1 - np.sqrt(q)) ** 2, var * (1 + np.sqrt(q)) ** 2


def mp_density(x: np.ndarray, q: float, var: float = 1.0) -> np.ndarray:
    """Marchenko-Pastur density for noise of variance `var` at aspect ratio q."""
    lo, hi = mp_support(q, var)
    out = np.zeros_like(x)
    inside = (x > lo) & (x < hi)
    out[inside] = np.sqrt((hi - x[inside]) * (x[inside] - lo)) / (2 * np.pi * q * var * x[inside])
    return out


def correlation_eigenvalues(returns: np.ndarray) -> np.ndarray:
    c = np.corrcoef(returns, rowvar=False)
    return np.sort(np.linalg.eigvalsh(c))[::-1]


def main() -> None:
    rng = np.random.default_rng(20260907)

    pure = rng.standard_normal((T, N))

    # One market factor loading on every name, plus idiosyncratic noise. The
    # factor explains ~30% of the average name's variance.
    beta = rng.uniform(0.5, 0.9, N)
    factor = rng.standard_normal((T, 1))
    structured = factor @ beta[None, :] + rng.standard_normal((T, N))

    fig, axes = plt.subplots(1, 2, figsize=(9.8, 3.9))

    panels = (
        (axes[0], pure, 1.0, "No structure — every eigenvalue is noise"),
        (axes[1], structured, None, "One market factor — a spike, and a noise bulk"),
    )

    for ax, data, fixed_var, title in panels:
        ev = correlation_eigenvalues(data)

        # Laloux-style fit: the market mode absorbs part of the trace, so the
        # residual noise has variance below 1 and its bulk shrinks to match.
        if fixed_var is not None:
            var = fixed_var
            outliers = np.array([])
        else:
            var = 1.0
            for _ in range(8):
                _, edge = mp_support(Q, var)
                outliers = ev[ev > edge]
                var = (N - outliers.sum()) / N
            _, edge = mp_support(Q, var)
            outliers = ev[ev > edge]

        lo, hi = mp_support(Q, var)
        grid = np.linspace(1e-4, hi * 1.08, 900)
        bulk = ev[ev <= hi]

        ax.hist(
            bulk,
            bins=40,
            density=True,
            color=FAINT,
            edgecolor=GREY,
            linewidth=0.5,
            label="sample eigenvalues (bulk)",
        )
        ax.plot(
            grid,
            mp_density(grid, Q, var),
            color=TEAL,
            lw=2.0,
            label="Marchenko–Pastur" + ("" if fixed_var is not None else f", σ² = {var:.2f}"),
        )
        ax.axvline(1.0, color=RUST, lw=1.5, ls="--", label="average eigenvalue (= 1)")
        ax.axvspan(lo, hi, color=TEAL, alpha=0.06)

        ax.set_title(title, fontsize=10, color=INK, pad=8)
        ax.set_xlabel("eigenvalue", fontsize=9, color=MUTED)
        ax.set_xlim(0, 2.65)
        ax.set_ylim(0, 1.55)
        ax.tick_params(labelsize=8, colors=MUTED)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GREY)

        if len(outliers):
            ax.text(
                0.97,
                0.72,
                f"λ₁ = {outliers[0]:.0f}, far off\nthe right of the axis:\nthe market factor",
                transform=ax.transAxes,
                fontsize=8.5,
                color=RUST,
                ha="right",
                va="top",
            )
            ax.text(
                0.97,
                0.44,
                f"the other {len(bulk)} carry\nno information",
                transform=ax.transAxes,
                fontsize=8.5,
                color=MUTED,
                ha="right",
                va="top",
            )
        else:
            ax.annotate(
                f"noise alone spreads\nthe spectrum {hi / lo:.0f}-fold,\nfrom {lo:.2f} to {hi:.2f}",
                xy=(hi, 0.06),
                xytext=(1.75, 1.20),
                fontsize=8.5,
                color=MUTED,
                ha="left",
                va="top",
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.0),
            )

        ax.legend(fontsize=8, frameon=False, loc="upper left")

    axes[0].set_ylabel("density", fontsize=9, color=MUTED)

    fig.text(
        0.5,
        -0.04,
        f"N = {N} assets, T = {T} observations, q = N/T = {Q:.2f}. Left: the truth is a single "
        f"eigenvalue at 1, and the sample smears it across the shaded band.\nRight: once the market "
        f"mode's share of the trace is taken out, what remains still matches the same law — which is "
        f"exactly what makes it safe to discard.",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    lo1, hi1 = mp_support(Q, 1.0)
    print(f"q = {Q:.4f}, MP support (var=1) = [{lo1:.4f}, {hi1:.4f}], ratio = {hi1 / lo1:.2f}")
    ev_pure = correlation_eigenvalues(pure)
    print(f"pure noise: lambda_max = {ev_pure[0]:.3f}, lambda_min = {ev_pure[-1]:.4f}")
    print(f"  condition number = {ev_pure[0] / ev_pure[-1]:.1f}")
    ev_struct = correlation_eigenvalues(structured)
    print(f"one factor: lambda_1 = {ev_struct[0]:.2f}, lambda_2 = {ev_struct[1]:.3f}")


main()

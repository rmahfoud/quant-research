# Two ways that honest-looking significance overstates the evidence.
#
#   Left  — specification search. Try K specifications of a regression when the
#           true effect is zero and report whether any of them is significant at
#           5%. Specifications that share data are correlated, which slows the
#           damage but does not stop it: with correlation 0.5 between every pair,
#           twenty tries still find "significance" about 40% of the time.
#           Computed exactly by integrating over the common component.
#   Right — the winner's curse. When a study is underpowered, the estimates
#           that clear the significance bar are, by construction, the ones that
#           overshot. Conditional on significance, the average estimate
#           overstates the true effect by the plotted factor.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import math
import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "em_forking_paths"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

Z = 1.959964
_erf = np.vectorize(math.erf)


def ncdf(x: np.ndarray) -> np.ndarray:
    return 0.5 * (1 + _erf(np.asarray(x, dtype=float) / math.sqrt(2)))


def p_any_significant(K: np.ndarray, rho: float) -> np.ndarray:
    """P(max_k |t_k| > Z) for K equicorrelated standard normal t-statistics under the null."""
    if rho == 0:
        return 1 - (1 - 0.05) ** K
    c = np.linspace(-9, 9, 6001)
    w = np.exp(-0.5 * c**2)
    w /= w.sum()
    a = np.sqrt(rho) * c
    s = np.sqrt(1 - rho)
    inside = ncdf((Z - a) / s) - ncdf((-Z - a) / s)
    return np.array([1 - np.sum(w * inside**k) for k in K])


def winners_curse(theta: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Power, exaggeration ratio E[|b| | significant] / theta, and sign-error rate, for b ~ N(theta, 1)."""
    b = np.linspace(-12, 20, 64001)
    db = b[1] - b[0]
    powers, ratios, type_s = [], [], []
    for th in theta:
        dens = np.exp(-0.5 * (b - th) ** 2) / math.sqrt(2 * math.pi)
        sig = np.abs(b) > Z
        p = np.sum(dens[sig]) * db
        powers.append(p)
        ratios.append(np.sum(np.abs(b[sig]) * dens[sig]) * db / p / th)
        type_s.append(np.sum(dens[b < -Z]) * db / p)
    return np.array(powers), np.array(ratios), np.array(type_s)


def main() -> None:
    rng = np.random.default_rng(20260913)

    K = np.unique(np.round(np.logspace(0, 3, 40)).astype(int))
    curves = {rho: p_any_significant(K, rho) for rho in (0.0, 0.5, 0.9)}

    theta = np.linspace(0.05, 4.5, 400)
    power, ratio, type_s = winners_curse(theta)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.6, 3.9))

    for rho, colour, style in ((0.0, RUST, "-"), (0.5, INK, "--"), (0.9, TEAL, "-")):
        axL.plot(K, curves[rho], color=colour, lw=2.0, ls=style, label=f"ρ = {rho:g}")
    axL.axhline(0.05, color=GREY, lw=1.0, ls=":")
    axL.set_xscale("log")
    axL.set_ylim(0, 1.0)
    axL.set_xlabel("number of specifications tried (K)", fontsize=10, color=MUTED)
    axL.set_ylabel("P(at least one |t| > 1.96)", fontsize=10, color=MUTED)
    axL.set_title("Search long enough and something is significant", fontsize=11, color=INK, loc="left", pad=8)
    axL.set_xticks([1, 10, 100, 1000])
    axL.set_xticklabels(["1", "10", "100", "1000"])
    legend = axL.legend(frameon=False, fontsize=9.5, loc="upper left", title="correlation between\nspecifications", title_fontsize=9)
    legend.get_title().set_color(MUTED)

    axR.plot(power, ratio, color=RUST, lw=2.2)
    axR.axhline(1.0, color=GREY, lw=1.0, ls=":")
    for target in (0.1, 0.2, 0.5, 0.8):
        i = int(np.argmin(np.abs(power - target)))
        axR.plot(power[i], ratio[i], "o", color=INK, ms=5)
        axR.text(power[i] + 0.02, ratio[i] + 0.12, f"{ratio[i]:.1f}×", fontsize=9, color=INK)
    axR.set_xlim(0.05, 1.0)
    axR.set_ylim(0.8, 5.0)
    axR.set_xlabel("statistical power of the study", fontsize=10, color=MUTED)
    axR.set_ylabel("exaggeration of significant estimates", fontsize=10, color=MUTED)
    axR.set_title("The winner's curse", fontsize=11, color=INK, loc="left", pad=8)

    for ax in (axL, axR):
        ax.tick_params(labelsize=9, colors=MUTED)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GREY)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print("Left panel: P(at least one |t| > 1.96) under the null")
    print(f"{'K':>6} {'rho=0':>7} {'rho=0.5':>8} {'rho=0.9':>8}   E[max|t|], independent (simulated)")
    for k_show in (1, 2, 5, 10, 20, 50, 100, 1000):
        vals = [p_any_significant(np.array([k_show]), rho)[0] for rho in (0.0, 0.5, 0.9)]
        emax = np.abs(rng.standard_normal((4000, k_show))).max(axis=1).mean()
        print(f"{k_show:6d} {vals[0]:7.3f} {vals[1]:8.3f} {vals[2]:8.3f}   {emax:.2f}")
    print()
    print("Right panel: b ~ N(theta, 1), significant if |b| > 1.96")
    print(f"{'power':>6} {'theta (SEs)':>12} {'exaggeration':>13} {'P(wrong sign | sig)':>20}")
    for target in (0.06, 0.1, 0.18, 0.2, 0.3, 0.5, 0.8, 0.9):
        i = int(np.argmin(np.abs(power - target)))
        print(f"{power[i]:6.2f} {theta[i]:12.2f} {ratio[i]:13.2f} {type_s[i]:20.3f}")


main()

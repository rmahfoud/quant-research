# What dealer hedging does to prices, in the simplest model that has the effect.
#
# A fundamental return e_t arrives each bar. Dealers rebalance their hedge
# against the previous bar's move, and their trade moves the price linearly:
#
#     r_t = e_t - kappa * r_{t-1},    kappa = (price impact per $) * (dealer $ gamma)
#
# kappa > 0 when dealers are long gamma (they sell rallies, buy dips); kappa < 0
# when they are short gamma (they buy rallies, sell dips).
#
#   Left  — volatility over a whole day, relative to no dealers, against kappa.
#           The line is 1/(1 + kappa), the result of solving the feedback loop
#           exactly; the dots are the lagged simulation. Short gamma amplifies,
#           long gamma dampens, and kappa -> -1 is a singularity.
#   Right — one simulated day from identical fundamental shocks. Long gamma
#           turns every move into a partial reversal; short gamma extends it.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "dh_feedback"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

BARS = 390
DAYS = 4000
BAR_VOL = 0.01 / np.sqrt(BARS)  # 1% daily volatility without dealers


def simulate(e: np.ndarray, kappa: float) -> np.ndarray:
    r = np.zeros_like(e)
    r[..., 0] = e[..., 0]
    for t in range(1, e.shape[-1]):
        r[..., t] = e[..., t] - kappa * r[..., t - 1]
    return r


def style(ax) -> None:
    ax.tick_params(labelsize=9, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)


def main() -> None:
    rng = np.random.default_rng(20260913)
    e = rng.normal(0.0, BAR_VOL, (DAYS, BARS))
    base = e.sum(axis=1).std()

    kappas = np.array([-0.6, -0.45, -0.3, -0.15, 0.0, 0.15, 0.3, 0.45, 0.6, 0.8])
    ratios, acs, bar_ratios = [], [], []
    for k in kappas:
        r = simulate(e, k)
        ratios.append(r.sum(axis=1).std() / base)
        bar_ratios.append(r.std() / e.std())
        x, y = r[:, :-1].ravel(), r[:, 1:].ravel()
        acs.append(np.corrcoef(x, y)[0, 1])

    grid = np.linspace(-0.85, 0.9, 400)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.6, 3.9))

    axL.axvspan(-1.0, -0.85, color=RUST, alpha=0.10, linewidth=0)
    axL.axhline(1, color=GREY, lw=0.8)
    axL.axvline(0, color=GREY, lw=0.8)
    axL.plot(grid, 1 / (1 + grid), color=INK, lw=2.0, label="exact loop: 1 / (1 + κ)")
    axL.scatter(kappas, ratios, s=26, color=RUST, zorder=5, edgecolor="white", linewidth=0.6, label="lagged simulation")
    axL.set_xlim(-1.0, 0.9)
    axL.set_ylim(0, 6.2)
    axL.set_xlabel("κ = price impact × dealer gamma", fontsize=10, color=MUTED)
    axL.set_ylabel("daily volatility ÷ no-dealer volatility", fontsize=10, color=MUTED)
    axL.set_title("Feedback multiplies volatility", fontsize=11, color=INK, loc="left", pad=8)
    axL.text(-0.55, 4.6, "short gamma:\namplifies", fontsize=9.5, color=RUST)
    axL.text(0.45, 1.5, "long gamma:\ndampens", fontsize=9.5, color=TEAL)
    axL.legend(frameon=False, fontsize=9.5, loc="upper right")
    style(axL)

    day = rng.normal(0.0, BAR_VOL, (1, BARS))
    minutes = np.arange(BARS + 1)
    for k, color, label in (
        (0.0, GREY, "no dealers"),
        (0.5, TEAL, "dealers long gamma (κ = +0.5)"),
        (-0.5, RUST, "dealers short gamma (κ = −0.5)"),
    ):
        path = 100 * np.exp(np.concatenate([[0.0], np.cumsum(simulate(day, k)[0])]))
        axR.plot(minutes, path, color=color, lw=1.5 if k else 1.2, label=label)
    axR.set_xlim(0, BARS)
    axR.set_xticks([0, 90, 180, 270, 390], labels=["open", "1.5h", "3h", "4.5h", "close"])
    axR.set_ylabel("price", fontsize=10, color=MUTED)
    axR.set_title("Same news, three different days", fontsize=11, color=INK, loc="left", pad=8)
    axR.legend(frameon=False, fontsize=9, loc="best")
    style(axR)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print(
        f"{'kappa':>6} {'daily vol ratio':>16} {'theory':>8} {'bar vol ratio':>14} {'lag-1 autocorr':>15} {'VR theory':>10}"
    )
    for k, ratio, bar, ac in zip(kappas, ratios, bar_ratios, acs, strict=True):
        print(f"{k:6.2f} {ratio:16.3f} {1 / (1 + k):8.3f} {bar:14.3f} {ac:15.3f} {(1 - k) / (1 + k):10.3f}")


main()

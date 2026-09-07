# Two facts about a trend rule run on a PURE RANDOM WALK — zero predictability
# by construction, so expected P&L is exactly zero.
#
#   Left  — conditional on the size of the year's move, the payoff is a smile.
#           Both responses are convex; the linear one is more convex.
#   Right — unconditionally, the linear rule's P&L is right-skewed with a
#           NEGATIVE median: it loses in most years and makes it back in a few.
#           The sign response, having thrown away magnitude, is near-symmetric.
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

BARS = 256
SIMS = 60_000
ALPHA = 2 / 65


def simulate(rng: np.random.Generator):
    r = rng.normal(0, 0.01, (SIMS, BARS))
    x = np.zeros((SIMS, BARS))
    for i in range(1, BARS):
        x[:, i] = (1 - ALPHA) * x[:, i - 1] + ALPHA * r[:, i - 1]
    lin = (x * r).sum(axis=1)
    sgn = (np.sign(x) * r).sum(axis=1)
    return r.sum(axis=1), lin / lin.std(), sgn / sgn.std()


def binned(move, pnl, edges):
    idx = np.digitize(move, edges) - 1
    xs, ys = [], []
    for b in range(len(edges) - 1):
        m = idx == b
        if m.sum() > 80:
            xs.append(0.5 * (edges[b] + edges[b + 1]))
            ys.append(pnl[m].mean())
    return np.array(xs), np.array(ys)


def style(ax):
    ax.patch.set_alpha(0.0)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)
    ax.tick_params(colors=MUTED, labelsize=8.5, length=3)
    ax.grid(True, color=FAINT, linewidth=0.7)
    ax.set_axisbelow(True)


def main() -> None:
    rng = np.random.default_rng(20240402)
    move, lin, sgn = simulate(rng)

    for name, v in (("linear", lin), ("sign", sgn)):
        skew = float(((v - v.mean()) ** 3).mean() / v.std() ** 3)
        print(
            f"  {name:>6}: mean {v.mean():+.4f}  median {np.median(v):+.4f}  "
            f"P(profit) {np.mean(v > 0):.3f}  skew {skew:+.2f}"
        )

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.4, 3.9), width_ratios=[1.15, 1.0])
    fig.patch.set_alpha(0.0)
    style(axL)
    style(axR)

    edges = np.quantile(move, np.linspace(0.004, 0.996, 26))
    xl, yl = binned(move, lin, edges)
    xs, ys = binned(move, sgn, edges)

    axL.axhline(0, color=GREY, linewidth=0.9)
    axL.scatter(100 * move[:3000], lin[:3000], s=3, color=TEAL, alpha=0.09, linewidths=0)
    axL.plot(100 * xl, yl, color=TEAL, linewidth=2.2, marker="o", markersize=3.6, label="linear  $\\pi_t \\propto x_t$")
    axL.plot(
        100 * xs,
        ys,
        color=RUST,
        linewidth=2.0,
        marker="s",
        markersize=3.4,
        linestyle=(0, (5, 2)),
        label="sign  $\\pi_t = \\mathrm{sign}(x_t)$",
    )
    axL.set_xlabel("underlying's move over the year (%)", fontsize=9.5, color=MUTED)
    axL.set_ylabel("mean P&L (risk units)", fontsize=9.5, color=MUTED)
    axL.set_title("Conditional on the move: a smile", fontsize=10.5, color=INK, loc="left", pad=8)
    leg = axL.legend(loc="upper center", frameon=False, fontsize=9, handlelength=2.4)
    for txt in leg.get_texts():
        txt.set_color(INK)

    bins = np.linspace(-3.2, 4.6, 90)
    axR.hist(lin, bins=bins, color=TEAL, alpha=0.42, linewidth=0, density=True, label="linear")
    axR.hist(sgn, bins=bins, color=RUST, alpha=0.34, linewidth=0, density=True, label="sign")
    axR.axvline(0, color=GREY, linewidth=0.9)
    axR.axvline(np.median(lin), color=TEAL, linewidth=1.7, linestyle=(0, (3, 2)))
    axR.axvline(np.median(sgn), color=RUST, linewidth=1.7, linestyle=(0, (3, 2)))
    axR.set_xlabel("annual P&L (risk units)", fontsize=9.5, color=MUTED)
    axR.set_ylabel("density", fontsize=9.5, color=MUTED)
    axR.set_title("Unconditionally: only the linear rule is skewed", fontsize=10.5, color=INK, loc="left", pad=8)
    leg = axR.legend(loc="upper left", frameon=False, fontsize=9)
    for txt in leg.get_texts():
        txt.set_color(INK)
    axR.annotate(
        f"linear median {np.median(lin):+.2f}\nprofitable in only {100 * np.mean(lin > 0):.0f}% of years",
        xy=(np.median(lin), 0.12),
        xytext=(0.9, 0.44),
        fontsize=8.8,
        color=MUTED,
        arrowprops=dict(arrowstyle="->", color=GREY, linewidth=0.9),
    )

    fig.tight_layout()
    out = Path(__file__).with_suffix(".svg")
    fig.savefig(out, transparent=True, bbox_inches="tight")
    print(f"  wrote {out.name}")


if __name__ == "__main__":
    main()

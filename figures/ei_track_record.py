# How long it takes a track record to say anything. Left: the 95% range of the
# Sharpe ratio measured over T years, for strategies whose true annual Sharpe
# ratio is 0.5 and 1.0 (normal, independent returns; the standard error of an
# annualised Sharpe ratio is close to 1 / sqrt(T) when it is estimated from
# daily or monthly data). Right: the years needed before a strategy's t-statistic
# is expected to clear the significance bar, when that bar is corrected for the
# number of strategies tried (Bonferroni, two-sided 5% family-wise level).
#
# Run standalone:  uv run --no-project --with matplotlib python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "ei_track_record"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path
from statistics import NormalDist

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"
GOLD = "#8C6D1F"

Z = NormalDist().inv_cdf


def style(ax: plt.Axes) -> None:
    ax.tick_params(labelsize=8.5, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)


def main() -> None:
    fig, (left, right) = plt.subplots(1, 2, figsize=(9.6, 4.4))

    years = np.linspace(1, 30, 300)
    for sr, colour in ((0.5, RUST), (1.0, TEAL)):
        half = 1.96 / np.sqrt(years)
        left.fill_between(years, sr - half, sr + half, color=colour, alpha=0.16, linewidth=0)
        left.plot(years, np.full_like(years, sr), color=colour, lw=1.8, label=f"true Sharpe {sr:.1f}")
        left.plot(years, sr - half, color=colour, lw=0.8)
        clear = (1.96 / sr) ** 2
        left.axvline(clear, color=colour, lw=0.8, ls=":")
        left.text(
            clear + 0.4,
            -0.95 if sr == 0.5 else -0.75,
            f"lower edge clears zero\nafter {clear:.1f} years",
            fontsize=7.8,
            color=colour,
        )
    left.axhline(0, color=INK, lw=0.8)
    left.set_xlim(1, 30)
    left.set_ylim(-1.2, 2.6)
    left.set_xlabel("length of track record, years", fontsize=9.5, color=MUTED)
    left.set_ylabel("measured annual Sharpe ratio (95% range)", fontsize=9.5, color=MUTED)
    left.set_title("What a track record can show", fontsize=10, color=INK, pad=8)
    left.legend(fontsize=8.3, frameon=False, loc="upper right")
    style(left)

    srs = np.linspace(0.2, 3.0, 300)
    trials = [(1, INK), (10, TEAL), (100, RUST), (1000, GOLD)]
    table = {}
    for k, colour in trials:
        t = Z(1 - 0.025 / k)
        need = (t / srs) ** 2
        right.plot(
            srs, need, color=colour, lw=1.9, label=f"{k:,} strateg{'y' if k == 1 else 'ies'} tried  (t > {t:.2f})"
        )
        table[k] = t
    right.set_yscale("log")
    right.set_xlim(0.2, 3.0)
    right.set_ylim(0.3, 200)
    right.set_yticks([0.5, 1, 2, 5, 10, 20, 50, 100, 200])
    right.set_yticklabels(["0.5", "1", "2", "5", "10", "20", "50", "100", "200"])
    right.set_xlabel("true annual Sharpe ratio", fontsize=9.5, color=MUTED)
    right.set_ylabel("years for expected t-statistic to clear the bar", fontsize=9.5, color=MUTED)
    right.set_title("What it costs to have looked at many", fontsize=10, color=INK, pad=8)
    right.legend(fontsize=8.0, frameon=False, loc="upper right")
    style(right)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print("years for the lower edge of the 95% range to clear zero:")
    for sr in (0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0):
        print(f"  SR {sr:4.2f}: {(1.96 / sr) ** 2:6.1f}")
    print("Bonferroni thresholds and years needed (expected t = SR sqrt(T)):")
    for k, _ in trials:
        t = table[k]
        cells = "  ".join(f"SR {sr:.1f}: {(t / sr) ** 2:6.1f}y" for sr in (0.5, 1.0, 2.0))
        print(f"  K={k:5d}  t={t:.2f}  evidence t^2/2 = {t * t / 2:.2f} nats   {cells}")


main()

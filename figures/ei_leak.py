# Where an edge goes between the forecast and the P&L. One monthly signal on 500
# stocks with an average information coefficient of 0.04, followed from the
# number the fundamental law promises to the number that survives. Bars are the
# annualised information ratio at each stage; labels give the share of the
# original information (IR squared) that is left. The stages are illustrative
# but each multiplier is a typical value (see the text): IC that varies from month
# to month with sd 0.08, a transfer coefficient of 0.6, a 10% loss of IC to
# execution delay, and 1.5% a year of trading costs at 5% active risk.
#
# Run standalone:  uv run --no-project --with matplotlib python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "ei_leak"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

IC = 0.04
N = 500
SD_IC = 0.08
TC = 0.6
DELAY = 0.9
ACTIVE_RISK = 0.05
COSTS = 0.015


def stages() -> list[tuple[str, float]]:
    naive = IC * np.sqrt(12 * N)
    breadth = np.sqrt(12) * IC / np.sqrt(SD_IC**2 + 1 / N)
    transfer = TC * breadth
    delayed = DELAY * transfer
    net = delayed - COSTS / ACTIVE_RISK
    return [
        ("the fundamental law's promise\nIC x sqrt(500 stocks x 12 months)", naive),
        ("breadth that is really there\nIC varies month to month (sd 0.08)", breadth),
        ("after constraints\ntransfer coefficient 0.6", transfer),
        ("after execution delay\n10% of the IC lost", delayed),
        ("after trading costs\n1.5% a year at 5% active risk", net),
    ]


def main() -> None:
    rows = stages()
    labels = [r[0] for r in rows]
    values = np.array([r[1] for r in rows])
    share = values**2 / values[0] ** 2

    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    y = np.arange(len(rows))[::-1]
    colours = [GREY, TEAL, TEAL, TEAL, RUST]
    ax.barh(y, values, color=colours, height=0.58)
    for yi, v, s in zip(y, values, share, strict=True):
        ax.text(
            v + 0.05,
            yi,
            f"IR {v:.2f}   ({s:.0%} of the information)" if s >= 0.1 else f"IR {v:.2f}   ({s:.1%} of the information)",
            va="center",
            fontsize=8.6,
            color=INK,
        )
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8.6, color=INK)
    ax.set_xlim(0, 4.6)
    ax.set_xlabel("annualised information ratio", fontsize=9.5, color=MUTED)
    ax.set_title("One signal, from forecast to P&L: information only leaks", fontsize=10, color=INK, pad=10)
    ax.tick_params(axis="x", labelsize=8.5, colors=MUTED)
    ax.tick_params(axis="y", length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GREY)
    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    for (label, v), s in zip(rows, share, strict=True):
        name = label.split("\n")[0]
        years = 4 / v**2
        print(f"{name:34s} IR {v:5.2f}  info share {s:6.1%}  nats/yr {v * v / 2:5.3f}  years to t=2 {years:5.1f}")


main()

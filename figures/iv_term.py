# The term structure of implied volatility, and why total variance is the
# natural coordinate for it.
#
#   Left  — at-the-money implied volatility against expiry in three settings: a
#           calm index market (upward sloping), a stressed one (inverted), and a
#           single stock with an earnings announcement 20 days out (a hump that
#           appears only for expiries after the event).
#   Right — the same curves as total implied variance, sigma^2 * T. Total
#           variance adds up over time, so the slope of each curve is the
#           forward variance the market prices for that interval, and an event
#           appears as a vertical step of known size.
#
# The index curves use the expected integrated variance of a mean-reverting
# variance process; the stock curve is a flat 25% plus one event whose move has
# a standard deviation of 6%. Prints the forward volatilities and the implied
# event move quoted in the text.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import math
import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "iv_term"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"
GOLD = "#B7791F"

KAPPA, THETA = 4.0, 0.19**2
EVENT_DAY, EVENT_SD, BASE = 20, 0.06, 0.25


def total_variance_index(days: np.ndarray, v0: float) -> np.ndarray:
    t = np.asarray(days, dtype=float) / 365
    return THETA * t + (v0 - THETA) * (1 - np.exp(-KAPPA * t)) / KAPPA


def total_variance_stock(days: np.ndarray) -> np.ndarray:
    t = np.asarray(days, dtype=float) / 365
    return BASE**2 * t + EVENT_SD**2 * (np.asarray(days) >= EVENT_DAY)


def iv(w: np.ndarray, days: np.ndarray) -> np.ndarray:
    return np.sqrt(w / (np.asarray(days, dtype=float) / 365))


def style(ax) -> None:
    ax.tick_params(labelsize=9, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)


def main() -> None:
    days = np.arange(2, 366, dtype=float)
    calm = total_variance_index(days, 0.11**2)
    stressed = total_variance_index(days, 0.45**2)
    stock = total_variance_stock(days)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.6, 3.9))
    for w, color, label in (
        (stressed, RUST, "index, stressed"),
        (stock, GOLD, "stock, earnings on day 20"),
        (calm, TEAL, "index, calm"),
    ):
        axL.plot(days, 100 * iv(w, days), color=color, lw=2.0, label=label)
    axL.axvline(EVENT_DAY, color=GREY, lw=0.8, ls=":")
    axL.set_xlim(0, 365)
    axL.set_ylim(0, 50)
    axL.set_xlabel("days to expiry", fontsize=10, color=MUTED)
    axL.set_ylabel("at-the-money implied volatility (%)", fontsize=10, color=MUTED)
    axL.set_title("Term structure: contango, inversion, a hump", fontsize=11, color=INK, loc="left", pad=8)
    axL.legend(frameon=False, fontsize=9.5, loc="upper right")
    style(axL)

    axR.plot(days, stressed, color=RUST, lw=2.0)
    axR.plot(days, stock, color=GOLD, lw=2.0)
    axR.plot(days, calm, color=TEAL, lw=2.0)
    axR.annotate(
        "event variance\n= 0.06² = 0.0036",
        xy=(EVENT_DAY + 1, BASE**2 * EVENT_DAY / 365 + EVENT_SD**2 / 2),
        xytext=(35, 0.066),
        fontsize=9,
        color=GOLD,
        arrowprops=dict(arrowstyle="->", color=GOLD, lw=0.9),
    )
    a, b = 30.0, 91.0
    wa, wb = (
        float(total_variance_index(np.array([a]), 0.11**2)[0]),
        float(total_variance_index(np.array([b]), 0.11**2)[0]),
    )
    axR.plot([a, b], [wa, wb], color=INK, lw=1.2, ls="--")
    axR.plot([a, b], [wa, wb], "o", color=INK, ms=4)
    fwd = math.sqrt((wb - wa) / ((b - a) / 365))
    axR.annotate(
        f"slope = forward variance\n30→91 days: {100 * fwd:.1f}% vol",
        xy=(0.5 * (a + b), 0.5 * (wa + wb)),
        xytext=(165, 0.0015),
        fontsize=9,
        color=INK,
        arrowprops=dict(arrowstyle="->", color=INK, lw=0.9),
    )
    axR.set_xlim(0, 365)
    axR.set_ylim(0, 0.08)
    axR.set_xlabel("days to expiry", fontsize=10, color=MUTED)
    axR.set_ylabel("total implied variance, σ² T", fontsize=10, color=MUTED)
    axR.set_title("Total variance adds up; slopes are forwards", fontsize=11, color=INK, loc="left", pad=8)
    style(axR)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    grid = np.array([7, 30, 60, 91, 182, 365], dtype=float)
    for name, v0 in (("calm", 0.11**2), ("stressed", 0.45**2)):
        w = total_variance_index(grid, v0)
        print(f"{name}: " + ", ".join(f"{int(d)}d {100 * v:.1f}%" for d, v in zip(grid, iv(w, grid))))
    print(f"calm forward vol 30->91: {100 * fwd:.2f}%")
    w = total_variance_stock(np.array([19.0, 21.0, 30.0, 60.0, 91.0]))
    print(
        "stock: "
        + ", ".join(
            f"{int(d)}d {100 * v:.2f}%"
            for d, v in zip((19, 21, 30, 60, 91), iv(w, np.array([19.0, 21.0, 30.0, 60.0, 91.0])))
        )
    )

    # Worked forward and event examples used in the text.
    f12 = math.sqrt((0.22**2 * 2 - 0.20**2 * 1) / 1)
    print(f"1M at 20%, 2M at 22% -> 1M-2M forward vol {100 * f12:.2f}%")
    t_after, t_before = 28 / 365, 14 / 365
    w_after = float(total_variance_stock(np.array([28.0]))[0])
    w_before = float(total_variance_stock(np.array([14.0]))[0])
    iv_after, iv_before = math.sqrt(w_after / t_after), math.sqrt(w_before / t_before)
    ev = w_after - w_before - iv_before**2 * (t_after - t_before)
    print(
        f"14d IV {100 * iv_before:.2f}%, 28d IV {100 * iv_after:.2f}%, event variance recovered {ev:.5f}, event sd {100 * math.sqrt(ev):.2f}%, mean abs move {100 * math.sqrt(ev) * math.sqrt(2 / math.pi):.2f}%"
    )
    w30 = 0.40**2 * 30 / 365
    base = 0.25**2 * 30 / 365
    ev2 = w30 - base
    print(
        f"30d IV 40% with base 25%: event variance {ev2:.5f}, sd {100 * math.sqrt(ev2):.2f}%, mean abs {100 * math.sqrt(ev2) * math.sqrt(2 / math.pi):.2f}%"
    )


main()

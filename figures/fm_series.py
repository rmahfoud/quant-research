# Three ways to glue the same contracts into one price history. A simulated
# market with monthly contracts spends six years in contango and then six in
# backwardation. All three series end at today's price; they disagree about the past.
# The back-adjusted (panama) series is today's price minus the dollars one
# contract has earned since, so it goes negative once a contract has earned more
# than today's price. The ratio-adjusted series is today's price divided by the
# growth since, which is the excess-return index rescaled. The unadjusted front
# month tracks spot and books a fake return at every roll (bottom panel).
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "fm_series"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
NAVY = "#1F3A6E"
GREY = "#9AA5AB"
FAINT = "#DCE4E6"

OUT = Path(__file__).with_suffix("")
YEAR = 252
N = 12 * YEAR
CYCLE = 21
ROLL = 5


def simulate(seed: int = 13) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    half = N // 2
    mu = np.where(np.arange(N) < half, -0.02, 0.14)
    log_s = np.log(40.0) + np.cumsum(mu / YEAR + 0.28 / np.sqrt(YEAR) * rng.standard_normal(N))
    target = np.where(np.arange(N) < half, 0.14, -0.14)
    c = np.empty(N)
    c[0] = target[0]
    for i in range(1, N):
        c[i] = c[i - 1] + 0.01 * (target[i] - c[i - 1]) + 0.006 * rng.standard_normal()
    return np.exp(log_s), c


def main() -> None:
    spot, c = simulate()
    expiries = np.arange(CYCLE, N + 3 * CYCLE, CYCLE)

    def price(expiry: int, day: int) -> float:
        return float(spot[day] * np.exp(c[day] * (expiry - day) / YEAR))

    def front(day: int) -> int:
        return int(expiries[np.argmax(expiries - day > ROLL)])

    unadj = np.array([price(front(i), i) for i in range(N)])
    true_ret = np.zeros(N)
    dollar = np.zeros(N)
    roll_days = []
    for i in range(1, N):
        held = front(i - 1)
        true_ret[i] = np.log(price(held, i) / price(held, i - 1))
        dollar[i] = price(held, i) - price(held, i - 1)
        if front(i) != held:
            roll_days.append(i)

    after = np.concatenate([np.cumsum(true_ret[::-1])[::-1][1:], [0.0]])
    ratio = unadj[-1] * np.exp(-after)
    after_d = np.concatenate([np.cumsum(dollar[::-1])[::-1][1:], [0.0]])
    panama = unadj[-1] - after_d
    fake = np.diff(np.log(unadj), prepend=np.log(unadj[0])) - true_ret

    years = np.arange(N) / YEAR
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(10.4, 6.6), gridspec_kw={"height_ratios": [2.3, 1.0]}, sharex=True)
    ax.plot(years, spot, color=GREY, lw=1.0, label="spot")
    ax.plot(years, unadj, color=NAVY, lw=1.1, label="unadjusted front month")
    ax.plot(years, ratio, color=TEAL, lw=1.7, label="ratio-adjusted (= excess-return index, rescaled)")
    ax.plot(years, panama, color=RUST, lw=1.7, label="back-adjusted (panama)")
    ax.axhline(0, color=INK, lw=0.8)
    ax.axvline(6, color=FAINT, lw=1.0, zorder=0)
    top = max(ratio.max(), panama.max(), spot.max())
    ax.text(0.15, top * 0.97, "six years of contango:\nholding futures lags spot", fontsize=8.5, color=MUTED, va="top")
    ax.text(
        6.15, top * 0.97, "six years of backwardation:\nholding futures beats spot", fontsize=8.5, color=MUTED, va="top"
    )
    neg = np.where(panama < 0)[0]
    if len(neg):
        k = neg[len(neg) // 2]
        ax.annotate(
            "negative 'price': one contract has since\nearned more than today's price",
            xy=(years[k], panama[k]),
            xytext=(1.6, -0.32 * top),
            fontsize=8.3,
            color=RUST,
            arrowprops=dict(arrowstyle="->", color=RUST, lw=0.9),
        )
    ax.annotate(
        "all three agree today",
        xy=(years[-1], unadj[-1]),
        xytext=(7.7, 0.80 * top),
        fontsize=8.3,
        color=INK,
        arrowprops=dict(arrowstyle="->", color=INK, lw=0.9),
    )
    ax.set_ylabel("price", fontsize=9)
    ax.set_title("Same contracts, three histories", fontsize=10.5, color=INK, loc="left")
    ax.legend(fontsize=8.3, frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.74), ncol=2)
    ax.set_ylim(min(panama.min(), 0) * 1.25 - 0.08 * top, top * 1.05)

    idx = np.array(roll_days)
    bx.vlines(years[idx], 0, fake[idx] * 100, color=NAVY, lw=0.9)
    bx.axhline(0, color=INK, lw=0.8)
    bx.axvline(6, color=FAINT, lw=1.0, zorder=0)
    bx.set_ylabel("fake return (%)", fontsize=9)
    bx.set_xlabel("years", fontsize=9)
    bx.set_title(
        "What the unadjusted series books on each roll day: the price gap between contracts, not a return",
        fontsize=9.6,
        color=INK,
        loc="left",
    )

    for a in (ax, bx):
        a.tick_params(labelsize=8.5, colors=MUTED)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            a.spines[s].set_color(FAINT)

    fig.tight_layout()
    for ext in ("pdf", "svg"):
        fig.savefig(f"{OUT}.{ext}", transparent=True, bbox_inches="tight")

    print(f"spot {spot[0]:.1f} -> {spot[N // 2]:.1f} -> {spot[-1]:.1f}")
    print(f"panama min {panama.min():.1f}, ratio start {ratio[0]:.1f}, unadj start {unadj[0]:.1f}")
    print(f"mean |fake| per roll {np.abs(fake[idx]).mean() * 100:.2f}% over {len(idx)} rolls")
    first, second = idx[idx < N // 2], idx[idx >= N // 2]
    print(f"sum fake first half {fake[first].sum() * 100:.1f}%, second half {fake[second].sum() * 100:.1f}%")


if __name__ == "__main__":
    main()

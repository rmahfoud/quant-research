# Putting implied volatility against history: the volatility cone, and the
# difference between implied-volatility rank and implied-volatility percentile.
#
#   Left  — a volatility cone (Burghardt & Lane, 1990): percentiles of realised
#           volatility measured over windows of 10 to 252 trading days, from 30
#           years of simulated daily returns, with a calm implied term
#           structure laid over it. Short windows have a wide range; long ones
#           a narrow range, because variance averages out.
#   Right — one simulated year of 30-day implied volatility containing a single
#           spike. Rank measures today's level against the year's minimum and
#           maximum; percentile counts the days below today. One spike drags
#           rank down and leaves percentile almost untouched.
#
# Returns follow a GARCH(1,1) with Student-t shocks. Implied volatility is the
# model's own expected volatility over the next 21 trading days, scaled up by
# 15% as a stand-in for the variance risk premium. Everything is simulated.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import math
import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "iv_cone"
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

ALPHA, BETA, LONG_VOL, DOF = 0.09, 0.88, 0.17, 6
YEARS = 30
HORIZONS = (10, 21, 42, 63, 126, 252)
CALM_IMPLIED = {10: 11.8, 21: 12.5, 42: 13.6, 63: 14.5, 126: 16.0, 252: 17.4}


def simulate(rng: np.random.Generator, days: int) -> tuple[np.ndarray, np.ndarray]:
    long_var = LONG_VOL**2 / 252
    omega = (1 - ALPHA - BETA) * long_var
    shocks = rng.standard_t(DOF, days) / math.sqrt(DOF / (DOF - 2))
    var = np.empty(days)
    ret = np.empty(days)
    v = long_var
    for i in range(days):
        var[i] = v
        ret[i] = math.sqrt(v) * shocks[i]
        v = omega + ALPHA * ret[i] ** 2 + BETA * v
    return ret, var


def expected_vol(var: np.ndarray, horizon: int) -> np.ndarray:
    long_var = LONG_VOL**2 / 252
    persistence = ALPHA + BETA
    j = np.arange(1, horizon + 1)
    mean_factor = np.mean(persistence**j)
    return np.sqrt(252 * (long_var + mean_factor * (var - long_var)))


def style(ax) -> None:
    ax.tick_params(labelsize=9, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)


def main() -> None:
    rng = np.random.default_rng(1)
    ret, var = simulate(rng, 252 * YEARS)

    pct = {q: [] for q in (5, 25, 50, 75, 95)}
    lows, highs = [], []
    for h in HORIZONS:
        csum = np.concatenate([[0.0], np.cumsum(ret**2)])
        rv = 100 * np.sqrt(252 / h * (csum[h:] - csum[:-h]))
        for q in pct:
            pct[q].append(np.percentile(rv, q))
        lows.append(rv.min())
        highs.append(rv.max())

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.6, 3.9))
    x = np.array(HORIZONS)
    axL.fill_between(x, pct[5], pct[95], color=TEAL, alpha=0.15, lw=0, label="5th–95th percentile")
    axL.fill_between(x, pct[25], pct[75], color=TEAL, alpha=0.35, lw=0, label="25th–75th percentile")
    axL.plot(x, pct[50], color=TEAL, lw=2.0, label="median realised")
    axL.plot(x, [CALM_IMPLIED[h] for h in HORIZONS], "o-", color=RUST, lw=1.6, ms=4, label="implied today (calm)")
    axL.set_xscale("log")
    axL.set_xticks(list(HORIZONS), labels=[str(h) for h in HORIZONS])
    axL.minorticks_off()
    axL.set_xlim(9, 280)
    axL.set_ylim(0, 45)
    axL.set_xlabel("measurement window (trading days)", fontsize=10, color=MUTED)
    axL.set_ylabel("annualised volatility (%)", fontsize=10, color=MUTED)
    axL.set_title("A volatility cone", fontsize=11, color=INK, loc="left", pad=8)
    axL.legend(frameon=False, fontsize=9, loc="upper right")
    style(axL)

    iv = 100 * 1.15 * expected_vol(var, 21)
    best, best_score = 0, -1.0
    for start in range(0, len(iv) - 252, 21):
        window = iv[start : start + 252]
        if window[-1] > np.percentile(window, 60) or window[-1] < np.percentile(window, 45):
            continue
        score = window.max() / np.median(window)
        if score > best_score:
            best, best_score = start, score
    window = iv[best : best + 252]
    today = window[-1]
    rank = (today - window.min()) / (window.max() - window.min())
    percentile = np.mean(window < today)
    days = np.arange(252)
    axR.plot(days, window, color=TEAL, lw=1.6)
    axR.axhline(window.max(), color=GREY, lw=0.8, ls="--")
    axR.axhline(window.min(), color=GREY, lw=0.8, ls="--")
    axR.axhline(today, color=RUST, lw=1.0, ls=":")
    axR.plot([251], [today], "o", color=RUST, ms=5, clip_on=False, zorder=5)
    axR.text(3, window.max() + 0.8, f"year's high {window.max():.1f}%", fontsize=9, color=MUTED)
    axR.text(3, window.min() - 2.6, f"year's low {window.min():.1f}%", fontsize=9, color=MUTED)
    axR.text(
        140,
        window.max() * 0.62,
        f"today {today:.1f}%\nrank {100 * rank:.0f}%\npercentile {100 * percentile:.0f}%",
        fontsize=9.5,
        color=RUST,
    )
    axR.set_xlim(0, 252)
    axR.set_ylim(max(0, window.min() - 5), window.max() + 5)
    axR.set_xlabel("trading days over the past year", fontsize=10, color=MUTED)
    axR.set_ylabel("30-day implied volatility (%)", fontsize=10, color=MUTED)
    axR.set_title("Rank and percentile disagree", fontsize=11, color=INK, loc="left", pad=8)
    style(axR)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print("cone percentiles (5/25/50/75/95) and min/max:")
    for i, h in enumerate(HORIZONS):
        print(
            f"  {h:3d}d: "
            + " / ".join(f"{pct[q][i]:.1f}" for q in (5, 25, 50, 75, 95))
            + f"   min {lows[i]:.1f} max {highs[i]:.1f}"
            f"   implied {CALM_IMPLIED[h]}"
        )
    print(f"full-sample realised vol {100 * math.sqrt(252 * np.mean(ret**2)):.2f}%")
    print(
        f"window start {best}: today {today:.2f}, low {window.min():.2f}, high {window.max():.2f}, rank {100 * rank:.1f}%, percentile {100 * percentile:.1f}%, median {np.median(window):.2f}"
    )


main()

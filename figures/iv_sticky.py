# How the smile moves when the price moves, and why local volatility counts the
# skew twice.
#
#   Left  — a 30-day equity-index smile with the price at 100 (grey), and three
#           rules for where it goes after the price falls to 95. Sticky strike:
#           every strike keeps its volatility, so the at-the-money volatility
#           slides up the skew. Sticky moneyness: the smile travels with the
#           price, so at-the-money volatility is unchanged. Local volatility:
#           the whole smile also rises by the skew move, so at-the-money
#           volatility moves about twice as far as under sticky strike.
#   Right — in the short-maturity limit, implied volatility at a strike is the
#           harmonic mean of local volatility between the price and the strike.
#           A local-volatility function that falls linearly in log-moneyness
#           produces an implied skew with half its slope.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import math
import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "iv_sticky"
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

T = 30 / 365
SKEW = (0.00134, 0.030, -0.55, 0.02, 0.05)
S0, S1 = 100.0, 95.0


def smile(strike: np.ndarray, spot: float) -> np.ndarray:
    a, b, rho, m, s = SKEW
    k = np.log(np.asarray(strike, dtype=float) / spot)
    return np.sqrt((a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + s**2))) / T)


def style(ax) -> None:
    ax.tick_params(labelsize=9, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)


def main() -> None:
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.6, 3.9))

    strikes = np.linspace(82, 112, 400)
    before = smile(strikes, S0)
    atm0 = float(smile(np.array(S0), S0))
    sticky_strike = before
    sticky_moneyness = smile(strikes, S1)
    shift = float(smile(np.array(S1), S0)) - atm0
    local_vol = before + shift

    axL.plot(strikes, 100 * before, color=GREY, lw=2.0, label="before: price 100")
    axL.plot(strikes, 100 * sticky_moneyness, color=TEAL, lw=2.0, label="after, sticky moneyness")
    axL.plot(strikes, 100 * sticky_strike, color=GOLD, lw=2.0, ls="--", label="after, sticky strike")
    axL.plot(strikes, 100 * local_vol, color=RUST, lw=2.0, label="after, local volatility")
    atms = {
        "sticky moneyness": float(smile(np.array(S1), S1)),
        "sticky strike": float(smile(np.array(S1), S0)),
        "local volatility": float(smile(np.array(S1), S0)) + shift,
    }
    axL.plot([S0], [100 * atm0], "o", color=GREY, ms=5)
    for (name, v), color in zip(atms.items(), (TEAL, GOLD, RUST)):
        axL.plot([S1], [100 * v], "o", color=color, ms=5)
    axL.axvline(S1, color=GREY, lw=0.8, ls=":")
    axL.set_xlim(82, 112)
    axL.set_ylim(10, 45)
    axL.set_xlabel("strike", fontsize=10, color=MUTED)
    axL.set_ylabel("30-day implied volatility (%)", fontsize=10, color=MUTED)
    axL.set_title("The price falls 5%: three rules", fontsize=11, color=INK, loc="left", pad=8)
    axL.legend(frameon=False, fontsize=9, loc="upper right")
    style(axL)

    sigma0, beta = 0.20, 1.0
    k = np.linspace(math.log(0.80), math.log(1.12), 400)
    local = sigma0 - beta * k
    with np.errstate(divide="ignore", invalid="ignore"):
        implied = np.where(np.abs(k) < 1e-9, sigma0, -beta * k / np.log(1 - beta * k / sigma0))
    axR.plot(100 * np.exp(k), 100 * local, color=RUST, lw=2.0, label="local volatility")
    axR.plot(100 * np.exp(k), 100 * implied, color=TEAL, lw=2.0, label="implied volatility")
    axR.set_xlim(80, 112)
    axR.set_ylim(0, 45)
    axR.set_xlabel("strike (price 100)", fontsize=10, color=MUTED)
    axR.set_ylabel("volatility (%)", fontsize=10, color=MUTED)
    axR.set_title("Implied skew is half the local skew", fontsize=11, color=INK, loc="left", pad=8)
    axR.legend(frameon=False, fontsize=9.5, loc="upper right")
    style(axR)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print(f"before: ATM {100 * atm0:.2f}%, vol at strike 95 {100 * float(smile(np.array(95.0), S0)):.2f}%")
    for name, v in atms.items():
        print(f"after drop to 95, {name}: ATM {100 * v:.2f}% (change {100 * (v - atm0):+.2f} points)")
    skew_k = (float(smile(np.array(100.5), S0)) - float(smile(np.array(99.5), S0))) / math.log(100.5 / 99.5)
    move = math.log(S1 / S0)
    for ratio in (0.0, 1.0, 1.5, 2.0):
        print(f"linearised ATM change for skew-stickiness ratio {ratio}: {100 * ratio * skew_k * move:+.2f} points")
    for strike in (80.0, 90.0, 95.0, 105.0, 110.0):
        kk = math.log(strike / 100)
        imp = sigma0 if abs(kk) < 1e-12 else -beta * kk / math.log(1 - beta * kk / sigma0)
        print(f"strike {strike}: local {100 * (sigma0 - beta * kk):.2f}%, implied {100 * imp:.2f}%")


main()

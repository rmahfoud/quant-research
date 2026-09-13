# Dealer gamma exposure for a synthetic index option chain.
#
#   Top    — exposure by strike at today's price, under the convention that
#            dealers are long the calls customers sold and short the puts
#            customers bought. Calls add positive gamma, puts negative.
#   Bottom — total exposure re-computed at hypothetical prices, holding each
#            strike's implied volatility fixed. Where the curve crosses zero is
#            the gamma flip. The dashed curve is the same book one week later,
#            after the front expiry has rolled off: the long gamma that sat in
#            expiring calls is gone, and the flip moves up towards the price.
#
# Also prints the five-strike worked example of the text.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import math
import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "dh_gex_profile"
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

S0 = 100.0
MULT = 100
FRONT_DAYS, BACK_DAYS = 7, 35


def gamma(s: np.ndarray, k: np.ndarray, tau: np.ndarray, vol: np.ndarray) -> np.ndarray:
    d1 = (np.log(s / k) + 0.5 * vol**2 * tau) / (vol * np.sqrt(tau))
    return np.exp(-0.5 * d1**2) / math.sqrt(2 * math.pi) / (s * vol * np.sqrt(tau))


def skew(k: np.ndarray) -> np.ndarray:
    return np.clip(0.16 - 0.55 * np.log(k / S0), 0.10, 0.40)


def bump(k: np.ndarray, centre: float, height: float, width: float) -> np.ndarray:
    return height * np.exp(-0.5 * ((k - centre) / width) ** 2)


def chain() -> list[dict]:
    k = np.arange(80.0, 121.0, 1.0)
    round5 = np.where(k % 5 == 0, 1.0, 0.35)
    front_calls = (bump(k, 100, 30_000, 1.0) + bump(k, 102, 25_000, 1.2) + bump(k, 105, 20_000, 1.5) + 1_500) * round5
    front_puts = (bump(k, 98, 8_000, 1.2) + bump(k, 95, 20_000, 1.5) + 1_500) * round5
    back_calls = (bump(k, 105, 30_000, 2.0) + bump(k, 110, 30_000, 2.5) + 1_500) * round5
    back_puts = (bump(k, 95, 45_000, 2.0) + bump(k, 90, 60_000, 3.0) + 2_500) * round5
    return [
        {"k": k, "oi": front_calls, "sign": +1, "days": FRONT_DAYS, "kind": "call"},
        {"k": k, "oi": front_puts, "sign": -1, "days": FRONT_DAYS, "kind": "put"},
        {"k": k, "oi": back_calls, "sign": +1, "days": BACK_DAYS, "kind": "call"},
        {"k": k, "oi": back_puts, "sign": -1, "days": BACK_DAYS, "kind": "put"},
    ]


def gex(spot: np.ndarray, legs: list[dict], elapsed_days: float = 0.0) -> np.ndarray:
    spot = np.atleast_1d(spot)[:, None]
    total = np.zeros(spot.shape[0])
    for leg in legs:
        days = leg["days"] - elapsed_days
        if days <= 0:
            continue
        g = gamma(spot, leg["k"][None, :], days / 365, skew(leg["k"])[None, :])
        total += (leg["sign"] * leg["oi"][None, :] * MULT * g * spot**2 * 0.01).sum(axis=1)
    return total / 1e6


def flip(grid: np.ndarray, curve: np.ndarray) -> float:
    idx = np.where(np.diff(np.sign(curve)) != 0)[0]
    i = idx[np.argmin(np.abs(grid[idx] - S0))]
    return float(grid[i] - curve[i] * (grid[i + 1] - grid[i]) / (curve[i + 1] - curve[i]))


def worked_example() -> None:
    k = np.array([90.0, 95.0, 100.0, 105.0, 110.0])
    vol = np.array([0.24, 0.22, 0.20, 0.18, 0.17])
    call_oi = np.array([2_000, 5_000, 20_000, 30_000, 15_000])
    put_oi = np.array([25_000, 30_000, 15_000, 3_000, 1_000])
    tau = 30 / 365
    print("\nWorked example: 30-day chain, dealers long calls / short puts, $ per 1% move")
    g = gamma(np.full(5, S0), k, np.full(5, tau), vol)
    per_contract = g * S0**2 * 0.01 * MULT
    call_gex = call_oi * per_contract
    put_gex = -put_oi * per_contract
    for i in range(5):
        print(
            f"  K={k[i]:.0f} vol={vol[i]:.2f} gamma={g[i]:.5f} $/1% per contract={per_contract[i]:7.1f} "
            f"calls={call_gex[i] / 1e6:+.3f}m puts={put_gex[i] / 1e6:+.3f}m net={(call_gex[i] + put_gex[i]) / 1e6:+.3f}m"
        )
    print(
        f"  total at S=100: {(call_gex.sum() + put_gex.sum()) / 1e6:+.3f}m "
        f"(calls {call_gex.sum() / 1e6:+.3f}m, puts {put_gex.sum() / 1e6:+.3f}m)"
    )
    print(f"  if dealers were short everything: {-(call_oi + put_oi) @ per_contract / 1e6:+.3f}m")
    for s in (94.0, 96.0, 97.0, 98.0, 99.0, 100.0, 102.0, 104.0, 106.0):
        gs = gamma(np.full(5, s), k, np.full(5, tau), vol) * s**2 * 0.01 * MULT
        print(f"  S={s:.0f}: total {((call_oi - put_oi) * gs).sum() / 1e6:+.3f}m")
    grid = np.linspace(90, 110, 2001)
    curve = np.array(
        [((call_oi - put_oi) * gamma(np.full(5, s), k, np.full(5, tau), vol) * s**2 * 0.01 * MULT).sum() for s in grid]
    )
    print(f"  worked-example flip: {flip(grid, curve):.2f}")


def main() -> None:
    legs = chain()
    grid = np.linspace(85, 115, 1201)
    today = gex(grid, legs)
    week_later = gex(grid, legs, elapsed_days=FRONT_DAYS)
    flip_today, flip_later = flip(grid, today), flip(grid, week_later)

    k = legs[0]["k"]
    call_bar = np.zeros_like(k)
    put_bar = np.zeros_like(k)
    for leg in legs:
        g = gamma(np.full_like(k, S0), k, np.full_like(k, leg["days"] / 365), skew(k))
        contrib = leg["sign"] * leg["oi"] * MULT * g * S0**2 * 0.01 / 1e6
        if leg["kind"] == "call":
            call_bar += contrib
        else:
            put_bar += contrib
    call_wall = float(k[np.argmax(call_bar)])
    put_wall = float(k[np.argmin(put_bar)])

    fig, (axT, axB) = plt.subplots(2, 1, figsize=(7.4, 6.4), height_ratios=[1.0, 1.25])

    axT.bar(k, call_bar, width=0.8, color=TEAL, label="calls (dealers long)")
    axT.bar(k, put_bar, width=0.8, color=RUST, label="puts (dealers short)")
    axT.axhline(0, color=GREY, lw=0.8)
    axT.axvline(S0, color=INK, lw=1.0, ls=":")
    axT.annotate(
        f"call wall {call_wall:.0f}",
        (call_wall, call_bar.max()),
        xytext=(call_wall + 3, call_bar.max() * 0.9),
        fontsize=9.5,
        color=MUTED,
        arrowprops={"arrowstyle": "-", "color": GREY, "lw": 0.8},
    )
    axT.annotate(
        f"put wall {put_wall:.0f}",
        (put_wall, put_bar.min()),
        xytext=(put_wall - 11, put_bar.min() * 0.9),
        fontsize=9.5,
        color=MUTED,
        arrowprops={"arrowstyle": "-", "color": GREY, "lw": 0.8},
    )
    axT.set_xlim(85, 115)
    axT.set_ylabel("$m per 1% move", fontsize=10, color=MUTED)
    axT.set_title("Dealer gamma by strike, at today's price of 100", fontsize=11, color=INK, loc="left", pad=8)
    axT.legend(frameon=False, fontsize=9.5, loc="upper left")

    axB.axhline(0, color=GREY, lw=0.8)
    axB.fill_between(grid, today, 0, where=today > 0, color=TEAL, alpha=0.12, linewidth=0)
    axB.fill_between(grid, today, 0, where=today < 0, color=RUST, alpha=0.12, linewidth=0)
    axB.plot(grid, today, color=INK, lw=2.2, label="today")
    axB.plot(grid, week_later, color=INK, lw=1.6, ls="--", label="after the front expiry")
    axB.axvline(S0, color=INK, lw=1.0, ls=":")
    axB.scatter([flip_today, flip_later], [0, 0], s=30, color=RUST, zorder=5)
    axB.annotate(
        f"flip {flip_today:.1f}",
        (flip_today, 0),
        xytext=(92.5, 0.3 * today.max()),
        fontsize=9.5,
        color=MUTED,
        arrowprops={"arrowstyle": "-", "color": GREY, "lw": 0.8},
    )
    axB.annotate(
        f"flip after expiry {flip_later:.1f}",
        (flip_later, 0),
        xytext=(103.5, 0.5 * today.min()),
        fontsize=9.5,
        color=MUTED,
        arrowprops={"arrowstyle": "-", "color": GREY, "lw": 0.8},
    )
    axB.text(107.5, 0.08 * today.max(), "dealers long gamma:\nhedging dampens moves", fontsize=9.5, color=TEAL)
    axB.text(85.6, 0.3 * today.min(), "dealers short gamma:\nhedging amplifies moves", fontsize=9.5, color=RUST)
    axB.set_xlim(85, 115)
    axB.set_xlabel("hypothetical underlying price", fontsize=10, color=MUTED)
    axB.set_ylabel("total, $m per 1% move", fontsize=10, color=MUTED)
    axB.set_title(
        "The gamma profile: total dealer gamma if the price were elsewhere", fontsize=11, color=INK, loc="left", pad=8
    )
    axB.legend(frameon=False, fontsize=9.5, loc="upper left")

    for ax in (axT, axB):
        ax.tick_params(labelsize=9, colors=MUTED)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GREY)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    at_spot = float(gex(np.array([S0]), legs)[0])
    at_spot_later = float(gex(np.array([S0]), legs, elapsed_days=FRONT_DAYS)[0])
    print(f"synthetic chain: GEX at 100 today {at_spot:+.1f}m, after front expiry {at_spot_later:+.1f}m")
    print(
        f"flip today {flip_today:.2f}, after front expiry {flip_later:.2f}; call wall {call_wall:.0f}, put wall {put_wall:.0f}"
    )
    print(
        f"profile max {today.max():+.1f}m at {grid[np.argmax(today)]:.1f}; min {today.min():+.1f}m at {grid[np.argmin(today)]:.1f}"
    )
    worked_example()


main()

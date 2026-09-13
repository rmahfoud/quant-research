# The four basic option positions, drawn as P&L against the underlying price.
#
# Dashed: P&L at expiry, net of the premium paid or received.
# Solid:  P&L if the price jumped there immediately, 30 days before expiry.
#
# The solid curve is the one a hedger lives on. Its slope at the current price
# is delta and its curvature is gamma: a smile for the two long positions, a
# frown for the two short ones. Call versus put changes the slope; long versus
# short changes the curvature.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import math
import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "dh_payoffs"
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

S0, K, VOL, TAU = 100.0, 100.0, 0.20, 30 / 365
N_OPT = 100  # one contract

_erf = np.vectorize(math.erf)


def ncdf(x: np.ndarray) -> np.ndarray:
    return 0.5 * (1 + _erf(np.asarray(x) / math.sqrt(2)))


def bs(cp: str, s: np.ndarray, tau: float) -> tuple[np.ndarray, np.ndarray]:
    s = np.asarray(s, dtype=float)
    d1 = (np.log(s / K) + 0.5 * VOL**2 * tau) / (VOL * math.sqrt(tau))
    d2 = d1 - VOL * math.sqrt(tau)
    if cp == "c":
        return s * ncdf(d1) - K * ncdf(d2), ncdf(d1)
    return K * ncdf(-d2) - s * ncdf(-d1), ncdf(d1) - 1


def panel(ax, cp: str, sign: int, title: str, hedge_now: str, hedge_up: str, text_x: float = 0.03) -> None:
    s = np.linspace(82, 118, 400)
    prem, _ = bs(cp, S0, TAU)
    payoff = np.maximum(s - K, 0) if cp == "c" else np.maximum(K - s, 0)
    value, _ = bs(cp, s, TAU)
    expiry_pnl = sign * (payoff - prem)
    now_pnl = sign * (value - prem)
    color = TEAL if sign > 0 else RUST

    ax.axhline(0, color=GREY, lw=0.8)
    ax.axvline(S0, color=FAINT, lw=1.0, zorder=0)
    ax.plot(s, expiry_pnl, color=color, lw=1.4, ls="--", alpha=0.75)
    ax.plot(s, now_pnl, color=color, lw=2.3)

    _, d0 = bs(cp, S0, TAU)
    slope = sign * float(d0)
    xs = np.array([S0 - 6, S0 + 6])
    ax.plot(xs, slope * (xs - S0), color=INK, lw=1.0, ls=":")
    ax.scatter([S0], [0], s=22, color=INK, zorder=5)

    ax.set_title(title, fontsize=11, color=INK, loc="left", pad=6)
    ax.text(text_x, 0.96, hedge_now, transform=ax.transAxes, fontsize=9.5, color=MUTED, va="top")
    ax.text(text_x, 0.86, hedge_up, transform=ax.transAxes, fontsize=9.5, color=MUTED, va="top")
    ax.set_xlim(82, 118)
    ax.set_ylim(-14, 14)
    ax.tick_params(labelsize=9, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)


def main() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.4, 6.2), sharex=True, sharey=True)
    panel(axes[0, 0], "c", +1, "Long call:  Δ > 0,  Γ > 0", "hedge now: sell 51 shares", "after +1%: sell 7 more")
    panel(axes[0, 1], "c", -1, "Short call:  Δ < 0,  Γ < 0", "hedge now: buy 51 shares", "after +1%: buy 7 more")
    panel(axes[1, 0], "p", +1, "Long put:  Δ < 0,  Γ > 0", "hedge now: buy 49 shares", "after +1%: sell 7", text_x=0.5)
    panel(axes[1, 1], "p", -1, "Short put:  Δ > 0,  Γ < 0", "hedge now: sell 49 shares", "after +1%: buy back 7")
    for ax in axes[1]:
        ax.set_xlabel("underlying price", fontsize=10, color=MUTED)
    for ax in axes[:, 0]:
        ax.set_ylabel("P&L per option", fontsize=10, color=MUTED)

    fig.text(
        0.5,
        -0.015,
        "Solid: P&L if the price moved now (30 days to expiry).  Dashed: P&L at expiry.  "
        "Dotted: the delta tangent.\nStrike 100, volatility 20%, hedge sizes per contract of 100 options.",
        ha="center",
        va="top",
        fontsize=9.5,
        color=MUTED,
    )
    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    for cp in ("c", "p"):
        prem, d = bs(cp, S0, TAU)
        _, d_up = bs(cp, S0 * 1.01, TAU)
        print(
            f"{cp}: premium {float(prem):.4f}, delta {float(d):+.4f} ({float(d) * N_OPT:+.1f} sh/contract), "
            f"delta after +1% {float(d_up):+.4f}, change {float(d_up - d) * N_OPT:+.1f} sh/contract"
        )


main()

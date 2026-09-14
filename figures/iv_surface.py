# Four ways to look at the same implied volatility surface.
#
#   Top left     — implied volatility against strike, one line per expiry. The
#                  familiar picture, but short expiries look steep and long ones
#                  flat partly because a 10% strike move means different things.
#   Top right    — implied volatility divided by at-the-money volatility, against
#                  standardised moneyness, log(K/F) / (ATM vol * sqrt T): distance
#                  from the money in standard deviations. In these coordinates
#                  the four expiries of this surface fall on one curve, so the
#                  surface is a level, a term structure and a single shape.
#   Bottom left  — total implied variance against log-moneyness. Calendar
#                  arbitrage would show up as two slices crossing; here they nest.
#   Bottom right — the whole surface as a heat map over moneyness and expiry.
#
# The surface is SSVI (Gatheral & Jacquier, 2014) with a power-law skew and a
# calm, upward-sloping at-the-money term structure. Prints at-the-money levels
# and skews, 25-delta risk reversals and butterflies, and numerical no-arbitrage
# checks.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import math
import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "iv_surface"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"
GOLD = "#B7791F"

RHO, ETA, GAMMA = -0.7, 1.15, 0.5
KAPPA, LONG_VAR, V0 = 4.0, 0.19**2, 0.11**2
EXPIRIES = ((7, RUST, "7 days"), (30, GOLD, "30 days"), (91, TEAL, "91 days"), (365, GREY, "1 year"))

_erf = np.vectorize(math.erf)


def atm_total_variance(days: np.ndarray | float) -> np.ndarray:
    t = np.asarray(days, dtype=float) / 365
    return LONG_VAR * t + (V0 - LONG_VAR) * (1 - np.exp(-KAPPA * t)) / KAPPA


def phi(theta: np.ndarray) -> np.ndarray:
    return ETA / (theta**GAMMA * (1 + theta) ** (1 - GAMMA))


def total_variance(k: np.ndarray, days: np.ndarray | float) -> np.ndarray:
    theta = atm_total_variance(days)
    p = phi(theta)
    return 0.5 * theta * (1 + RHO * p * k + np.sqrt((p * k + RHO) ** 2 + 1 - RHO**2))


def implied(k: np.ndarray, days: np.ndarray | float) -> np.ndarray:
    return np.sqrt(total_variance(k, days) / (np.asarray(days, dtype=float) / 365))


def butterfly_g(k: np.ndarray, days: float) -> np.ndarray:
    h = 1e-4
    w = total_variance(k, days)
    wp = (total_variance(k + h, days) - total_variance(k - h, days)) / (2 * h)
    wpp = (total_variance(k + h, days) - 2 * w + total_variance(k - h, days)) / h**2
    return (1 - k * wp / (2 * w)) ** 2 - wp**2 / 4 * (1 / w + 0.25) + wpp / 2


def strike_for_delta(days: float, call_delta: float) -> float:
    target = math.sqrt(2) * _inverse_erf(2 * call_delta - 1)
    lo, hi = -2.0, 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        w = float(total_variance(np.array(mid), days))
        d1 = -mid / math.sqrt(w) + 0.5 * math.sqrt(w)
        if d1 > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _inverse_erf(y: float) -> float:
    lo, hi = -6.0, 6.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if math.erf(mid) < y:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def style(ax) -> None:
    ax.tick_params(labelsize=9, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)


def main() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(8.6, 7.4))
    (axA, axB), (axC, axD) = axes

    k = np.linspace(math.log(0.70), math.log(1.15), 500)
    for days, color, label in EXPIRIES:
        theta = float(atm_total_variance(days))
        axA.plot(100 * np.exp(k), 100 * implied(k, days), color=color, lw=2.0, label=label)
        z = np.linspace(-4.0, 2.0, 400)
        kz = z * math.sqrt(theta)
        axB.plot(z, implied(kz, days) / math.sqrt(theta / (days / 365)), color=color, lw=2.0, label=label)
        axC.semilogy(k, total_variance(k, days), color=color, lw=2.0, label=label)

    axA.set_xlim(70, 115)
    axA.set_ylim(0, 60)
    axA.set_xlabel("strike (% of forward)", fontsize=10, color=MUTED)
    axA.set_ylabel("implied volatility (%)", fontsize=10, color=MUTED)
    axA.set_title("By strike", fontsize=11, color=INK, loc="left", pad=8)
    axA.legend(frameon=False, fontsize=9.5, loc="upper right")
    style(axA)

    axB.set_xlim(-4.0, 2.0)
    axB.set_ylim(0.5, 3.0)
    axB.axhline(1.0, color=GREY, lw=0.8, ls=":")
    axB.set_xlabel("standard deviations from the money, log(K/F) / (σ_ATM √T)", fontsize=10, color=MUTED)
    axB.set_ylabel("implied vol ÷ at-the-money vol", fontsize=10, color=MUTED)
    axB.set_title("Rescaled: all four expiries coincide", fontsize=11, color=INK, loc="left", pad=8)
    style(axB)

    axC.set_xlim(math.log(0.70), math.log(1.15))
    axC.set_ylim(6e-5, 0.12)
    axC.set_xlabel("log-moneyness, log(K/F)", fontsize=10, color=MUTED)
    axC.set_ylabel("total implied variance, σ² T (log scale)", fontsize=10, color=MUTED)
    axC.set_title("Total variance: slices must not cross", fontsize=11, color=INK, loc="left", pad=8)
    style(axC)

    days_grid = np.linspace(7, 365, 240)
    money = np.linspace(0.75, 1.12, 240)
    kk, dd = np.meshgrid(np.log(money), days_grid, indexing="xy")
    surface = 100 * implied(kk, dd)
    cmap = LinearSegmentedColormap.from_list("vol", ["#F3F6F6", "#9CC9C7", TEAL, "#7A3A2A"])
    mesh = axD.pcolormesh(100 * money, days_grid, surface, cmap=cmap, shading="auto", vmin=8, vmax=50, rasterized=True)
    levels = [12, 15, 20, 25, 30, 40]
    cs = axD.contour(100 * money, days_grid, surface, levels=levels, colors=INK, linewidths=0.7)
    axD.clabel(cs, fmt="%d%%", fontsize=8)
    axD.set_xlabel("strike (% of forward)", fontsize=10, color=MUTED)
    axD.set_ylabel("days to expiry", fontsize=10, color=MUTED)
    axD.set_title("The whole surface", fontsize=11, color=INK, loc="left", pad=8)
    cbar = fig.colorbar(mesh, ax=axD, fraction=0.05, pad=0.02)
    cbar.ax.tick_params(labelsize=8, colors=MUTED)
    cbar.outline.set_edgecolor(GREY)
    style(axD)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight", dpi=200)

    kgrid = np.linspace(-1.5, 1.0, 5001)
    skews = {}
    for days, _, _ in EXPIRIES:
        atm = float(implied(np.array(0.0), days))
        up, dn = float(implied(np.array(math.log(1.005)), days)), float(implied(np.array(math.log(0.995)), days))
        skew = 100 * (up - dn) / 1.0
        skews[days] = skew
        kc, kp = strike_for_delta(days, 0.25), strike_for_delta(days, 0.75)
        vc, vp = float(implied(np.array(kc), days)), float(implied(np.array(kp), days))
        print(
            f"{days:3d}d: ATM {100 * atm:.2f}%  skew {skew:+.3f} vol pts per 1% strike  "
            f"25d call strike {100 * math.exp(kc):.1f}% vol {100 * vc:.2f}%  25d put strike {100 * math.exp(kp):.1f}% vol {100 * vp:.2f}%  "
            f"RR {100 * (vc - vp):+.2f}  BF {100 * (0.5 * (vc + vp) - atm):+.2f}  min g {butterfly_g(kgrid, days).min():.4f}"
        )
    exponent = math.log(skews[365] / skews[30]) / math.log(365 / 30)
    print(f"ATM skew term-structure exponent between 30d and 1y: {exponent:.3f}")
    dgrid = np.linspace(2, 400, 800)
    kk2, dd2 = np.meshgrid(np.linspace(-1.0, 0.5, 301), dgrid, indexing="xy")
    wsurf = total_variance(kk2, dd2)
    print(f"min dw/dT over grid: {np.diff(wsurf, axis=0).min():.3e}")
    for m in (0.80, 0.90, 1.10):
        print(
            f"  {int(100 * m)}% strike vol: "
            + ", ".join(f"{d}d {100 * float(implied(np.array(math.log(m)), d)):.2f}%" for d, _, _ in EXPIRIES)
        )


main()

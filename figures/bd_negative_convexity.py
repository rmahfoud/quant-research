# Negative convexity. A callable bond and a mortgage pass-through stop
# appreciating when rates fall, because the borrower's right to refinance is
# worth more exactly when the bond would otherwise be worth more. The right-hand
# panel is the consequence: their duration moves the wrong way.
#
# Both instruments are stylised. The callable is a 10-year 4% bond callable at
# par from year 5, valued as bullet minus a Black call on the forward price of
# the residual bond. The pass-through is a blend of a short and a long bond whose
# weight follows a logistic prepayment response to the refinancing incentive.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "bd_negative_convexity"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from math import erf

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
NAVY = "#1F3A6E"
FAINT = "#DCE4E6"

COUPON = 0.04
Y0 = 0.04
FREQ = 2
T_CALL = 5.0
STRIKE = 100.0
YIELD_VOL = 0.010  # 100bp of annual yield volatility


def ncdf(x: np.ndarray) -> np.ndarray:
    return 0.5 * (1.0 + np.vectorize(erf)(x / np.sqrt(2.0)))


def price(y: np.ndarray, maturity: float, coupon: float = COUPON) -> np.ndarray:
    n = int(round(maturity * FREQ))
    t = np.arange(1, n + 1)
    cf = np.full(n, 100.0 * coupon / FREQ)
    cf[-1] += 100.0
    d = (1.0 + np.asarray(y, dtype=float)[..., None] / FREQ) ** (-t)
    return (cf * d).sum(axis=-1)


def mod_duration(fn, y: np.ndarray, h: float = 2.5e-4) -> np.ndarray:
    """Effective duration by central difference: the practitioner's definition."""
    return -(fn(y + h) - fn(y - h)) / (2 * h) / fn(y)


def bullet(y: np.ndarray) -> np.ndarray:
    return price(y, 10.0)


def callable_bond(y: np.ndarray) -> np.ndarray:
    """Bullet minus the issuer's call, Black on the forward price of the stub."""
    fwd = price(y, 10.0 - T_CALL)          # value at call date if the curve is unchanged
    dur_stub = mod_duration(lambda z: price(z, 10.0 - T_CALL), y)
    sig = dur_stub * YIELD_VOL             # price vol implied by yield vol
    st = sig * np.sqrt(T_CALL)
    d1 = (np.log(fwd / STRIKE) + 0.5 * st**2) / st
    d2 = d1 - st
    disc = (1.0 + y / FREQ) ** (-FREQ * T_CALL)
    call = disc * (fwd * ncdf(d1) - STRIKE * ncdf(d2))
    return bullet(y) - call


def pass_through(y: np.ndarray) -> np.ndarray:
    """Prepayment shortens the pool exactly when rates fall."""
    incentive = (COUPON - y) * 100.0       # in percentage points of refi saving
    w_fast = 1.0 / (1.0 + np.exp(-2.2 * (incentive - 0.35)))
    return w_fast * price(y, 2.5) + (1.0 - w_fast) * price(y, 8.5)


def main() -> None:
    ys = np.linspace(0.005, 0.085, 500)
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.0, 4.3))

    series = [
        (bullet, "option-free bullet", NAVY, "-"),
        (callable_bond, "callable at par from year 5", RUST, "-"),
        (pass_through, "mortgage pass-through", TEAL, "--"),
    ]
    for fn, label, c, ls in series:
        ax.plot(ys * 100, fn(ys), color=c, lw=1.9, ls=ls, label=label)
        bx.plot(ys * 100, mod_duration(fn, ys), color=c, lw=1.9, ls=ls, label=label)

    ax.axhline(STRIKE, color=FAINT, lw=1.0, zorder=0)
    ax.axvline(Y0 * 100, color=FAINT, lw=1.0, zorder=0)
    ax.annotate(
        "the call caps the upside",
        xy=(1.6, float(callable_bond(np.array(0.016)))),
        xytext=(2.9, 128), fontsize=8.5, color=RUST, ha="left",
        arrowprops=dict(arrowstyle="->", color=RUST, lw=1.0),
    )
    ax.set_xlabel("yield (%)", fontsize=9)
    ax.set_ylabel("price (per 100 face)", fontsize=9)
    ax.set_title("Price against yield", fontsize=10.5, color=INK, loc="left")
    ax.legend(fontsize=8.5, frameon=False, loc="upper right")

    bx.axvline(Y0 * 100, color=FAINT, lw=1.0, zorder=0)
    bx.annotate(
        "duration falls as rates fall\n(you own less bond in a rally)",
        xy=(2.0, float(mod_duration(pass_through, np.array(0.020)))),
        xytext=(3.6, 1.1), fontsize=8.5, color=TEAL, ha="left",
        arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.0),
    )
    bx.set_xlabel("yield (%)", fontsize=9)
    bx.set_ylabel("effective duration (years)", fontsize=9)
    bx.set_title("Effective duration against yield", fontsize=10.5, color=INK, loc="left")
    bx.set_ylim(0, 9)

    for a in (ax, bx):
        a.tick_params(labelsize=8.5, colors=MUTED)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            a.spines[s].set_color(FAINT)

    fig.text(
        0.5, -0.05,
        "Positive convexity means duration lengthens into a rally and shortens into a sell-off — the holder is "
        "automatically on the right side.\nNegative convexity reverses both. Stylised instruments; the shapes "
        "are the point, not the levels.",
        ha="center", fontsize=8.5, color=MUTED,
    )
    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print(f"{'yield':>7} {'bullet P':>9} {'call P':>8} {'MBS P':>8} "
          f"{'bullet D':>9} {'call D':>8} {'MBS D':>7}")
    for yv in (0.02, 0.03, 0.04, 0.05, 0.06):
        a = np.array(yv)
        print(f"{yv * 100:6.1f}% {float(bullet(a)):9.2f} {float(callable_bond(a)):8.2f} "
              f"{float(pass_through(a)):8.2f} {float(mod_duration(bullet, a)):9.2f} "
              f"{float(mod_duration(callable_bond, a)):8.2f} {float(mod_duration(pass_through, a)):7.2f}")
    print()
    for fn, label, _, _ in series:
        p0 = float(fn(np.array(Y0)))
        up = float(fn(np.array(Y0 + 0.01))) / p0 - 1
        dn = float(fn(np.array(Y0 - 0.01))) / p0 - 1
        print(f"{label:>30}: -100bp {dn * 100:+6.2f}%   +100bp {up * 100:+6.2f}%   "
              f"asymmetry {(dn + up) * 100:+5.2f}pp")


main()

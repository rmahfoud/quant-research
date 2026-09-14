# Spurious regression: two independent random walks look related.
#
#   Left  — the t-statistic on the slope when y is regressed on x, for two
#           independent series of length 100. With white noise it is standard
#           normal, as the textbook promises. With random walks it is spread so
#           widely that |t| > 1.96 is the typical outcome, not the exception.
#   Right — the false-rejection rate of a nominal 5% test as the sample grows.
#           For white noise it sits at 5%. For random walks it *rises* with T,
#           because the t-statistic diverges at rate sqrt(T) (Phillips, 1986);
#           Newey-West standard errors slow the divergence but do not stop it.
#
# Every series is independent of every other, so every rejection is false.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "em_spurious"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

TRIALS = 4000
CHUNK = 500
LENGTHS = [25, 50, 100, 200, 400, 800, 1600]


def slope_stats(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """OLS of y on (1, x), row by row: t with classical SE, t with Newey-West SE, R-squared."""
    T = x.shape[1]
    xc = x - x.mean(axis=1, keepdims=True)
    yc = y - y.mean(axis=1, keepdims=True)
    sxx = (xc * xc).sum(axis=1)
    beta = (xc * yc).sum(axis=1) / sxx
    resid = yc - beta[:, None] * xc
    ssr = (resid * resid).sum(axis=1)
    t_ols = beta / np.sqrt(ssr / (T - 2) / sxx)

    lags = int(np.floor(4 * (T / 100) ** (2 / 9)))
    score = xc * resid
    meat = (score * score).sum(axis=1)
    for k in range(1, lags + 1):
        meat += 2 * (1 - k / (lags + 1)) * (score[:, k:] * score[:, :-k]).sum(axis=1)
    t_nw = beta / (np.sqrt(meat) / sxx)

    r2 = 1 - ssr / (yc * yc).sum(axis=1)
    return t_ols, t_nw, r2, beta


def simulate(T: int, walk: bool, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    t_ols, t_nw, r2 = [], [], []
    for start in range(0, TRIALS, CHUNK):
        n = min(CHUNK, TRIALS - start)
        x = rng.standard_normal((n, T))
        y = rng.standard_normal((n, T))
        if walk:
            x = x.cumsum(axis=1)
            y = y.cumsum(axis=1)
        a, b, c, _ = slope_stats(x, y)
        t_ols.append(a)
        t_nw.append(b)
        r2.append(c)
    return np.concatenate(t_ols), np.concatenate(t_nw), np.concatenate(r2)


def main() -> None:
    rng = np.random.default_rng(20260913)

    rows = []
    hist = {}
    for T in LENGTHS:
        t_iid, _, r2_iid = simulate(T, walk=False, rng=rng)
        t_rw, t_rw_nw, r2_rw = simulate(T, walk=True, rng=rng)
        rows.append(
            (
                T,
                np.mean(np.abs(t_iid) > 1.96),
                np.mean(np.abs(t_rw) > 1.96),
                np.mean(np.abs(t_rw_nw) > 1.96),
                np.median(np.abs(t_rw)),
                np.median(r2_iid),
                np.median(r2_rw),
                np.mean(r2_rw > 0.3),
            )
        )
        if T == 100:
            hist = {"iid": t_iid, "rw": t_rw}

    rows = np.array(rows)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.6, 3.9))

    bins = np.linspace(-20, 20, 121)
    axL.hist(np.clip(hist["iid"], -20, 20), bins=bins, density=True, color=TEAL, alpha=0.85, label="white noise")
    axL.hist(np.clip(hist["rw"], -20, 20), bins=bins, density=True, color=RUST, alpha=0.55, label="random walks")
    for v in (-1.96, 1.96):
        axL.axvline(v, color=INK, lw=0.9, ls="--")
    axL.set_xlim(-20, 20)
    axL.set_xlabel("t-statistic on the slope (T = 100, clipped at ±20)", fontsize=10, color=MUTED)
    axL.set_ylabel("density", fontsize=10, color=MUTED)
    axL.set_title("Same regression, same independence", fontsize=11, color=INK, loc="left", pad=8)
    axL.text(2.6, 0.33, "±1.96", fontsize=9, color=INK)
    axL.legend(frameon=False, fontsize=9.5, loc="upper left")

    Ts = rows[:, 0]
    axR.axhline(0.05, color=GREY, lw=1.0, ls=":")
    axR.plot(Ts, rows[:, 2], "o-", color=RUST, lw=2.0, ms=4.5, label="random walks, classical SE")
    axR.plot(Ts, rows[:, 3], "s--", color=INK, lw=1.6, ms=4.0, label="random walks, Newey–West SE")
    axR.plot(Ts, rows[:, 1], "o-", color=TEAL, lw=2.0, ms=4.5, label="white noise, classical SE")
    axR.set_xscale("log")
    axR.set_xticks(LENGTHS)
    axR.set_xticklabels([str(t) for t in LENGTHS])
    axR.set_ylim(0, 1.0)
    axR.set_xlabel("sample length T", fontsize=10, color=MUTED)
    axR.set_ylabel("share of |t| > 1.96", fontsize=10, color=MUTED)
    axR.set_title("More data makes it worse", fontsize=11, color=INK, loc="left", pad=8)
    axR.text(27, 0.075, "nominal 5%", fontsize=9, color=MUTED)
    axR.legend(frameon=False, fontsize=9.5, loc="center right", bbox_to_anchor=(1.0, 0.33))

    for ax in (axL, axR):
        ax.tick_params(labelsize=9, colors=MUTED)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GREY)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print(f"{'T':>5} {'rej iid':>8} {'rej RW':>8} {'rej RW NW':>10} {'med|t| RW':>10} {'medR2 iid':>10} {'medR2 RW':>9} {'P(R2>.3) RW':>12}")
    for r in rows:
        print(f"{int(r[0]):5d} {r[1]:8.3f} {r[2]:8.3f} {r[3]:10.3f} {r[4]:10.2f} {r[5]:10.4f} {r[6]:9.3f} {r[7]:12.3f}")


main()

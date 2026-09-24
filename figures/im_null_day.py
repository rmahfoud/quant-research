# What pure noise looks like inside a trading day.
#
# Every number here comes from price paths with no predictability at all:
# driftless random-walk days with a U-shaped intraday volatility profile,
# persistent day-to-day volatility and fat-tailed (Student-t, 5 d.o.f.) shocks.
# Anything a pipeline "finds" on these paths is an artefact.
#
#   Left  — the per-day variance ratio VR_d = (sum of the day's 5-minute
#           returns)^2 / (sum of their squares). On a random walk it is close to
#           chi-squared with one degree of freedom, whatever the volatility
#           profile, so about 5% of days exceed 3.84 by chance.
#   Right — lag-1 autocorrelation of last-trade returns when every bar closes on
#           a buy or a sell with equal probability (Roll's bounce). Lines are
#           Roll's formula -(s^2/4) / (sigma_bar^2 + s^2/2); dots are simulated.
#
# The script also prints three results quoted in the text but not plotted:
#   * the opening-range "noise area" rule (Zarattini, Aziz and Barbon, 2024,
#     base version, without the overnight-gap adjustment) run on the null days;
#   * the apparent profit of a one-minute reversal rule measured on last-trade
#     prices versus midquotes;
#   * the momentum a stale cash index manufactures at the open.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "im_null_day"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GOLD = "#9A6B00"
GREY = "#8A979D"

MINUTES = 390
DAYS = 20000
BURN = 14  # days of history the noise-area band needs
CHECKS = np.arange(30, 361, 30)  # 10:00, 10:30, ..., 15:30


def style(ax) -> None:
    ax.tick_params(labelsize=9, colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)


def t_shocks(rng: np.random.Generator, shape: tuple[int, ...], dof: float = 5.0) -> np.ndarray:
    return rng.standard_t(dof, shape) / np.sqrt(dof / (dof - 2.0))


def u_profile() -> np.ndarray:
    t = (np.arange(MINUTES) + 0.5) / MINUTES
    u = 1.0 + 3.0 * np.exp(-t / 0.05) + 1.2 * np.exp(-(1.0 - t) / 0.06)
    return u / u.sum()


def null_days(rng: np.random.Generator) -> np.ndarray:
    n = DAYS + BURN
    x = np.zeros(n)
    phi, sd = 0.97, 0.35
    eps = rng.normal(0.0, sd * np.sqrt(1 - phi**2), n)
    for d in range(1, n):
        x[d] = phi * x[d - 1] + eps[d]
    sigma = 0.0095 * np.exp(x - sd**2 / 2)
    return sigma[:, None] * np.sqrt(u_profile())[None, :] * t_shocks(rng, (n, MINUTES))


def variance_ratio(r: np.ndarray, bar: int) -> np.ndarray:
    rb = r.reshape(r.shape[0], -1, bar).sum(axis=2)
    return rb.sum(axis=1) ** 2 / (rb**2).sum(axis=1)


def efficiency_ratio(r: np.ndarray, bar: int) -> np.ndarray:
    rb = r.reshape(r.shape[0], -1, bar).sum(axis=2)
    return np.abs(rb.sum(axis=1)) / np.abs(rb).sum(axis=1)


def noise_area_rule(r: np.ndarray) -> dict[str, float]:
    price = np.exp(np.concatenate([np.zeros((r.shape[0], 1)), np.cumsum(r, axis=1)], axis=1))
    move = np.abs(price[:, CHECKS] - 1.0)
    csum = np.cumsum(np.vstack([np.zeros((1, len(CHECKS))), move]), axis=0)
    band = (csum[BURN:-1] - csum[: -BURN - 1]) / BURN  # mean of the previous 14 days
    p = price[BURN:]
    days = p.shape[0]
    pos = np.zeros(days)
    entry = np.ones(days)
    pnl = np.zeros(days)
    trans = np.zeros(days)
    entries = np.zeros(days)
    outside = 0
    for j, m in enumerate(CHECKS):
        now = p[:, m]
        up, dn = now > 1.0 + band[:, j], now < 1.0 - band[:, j]
        outside += np.count_nonzero(up | dn)
        new = np.where(up, 1.0, np.where(dn, -1.0, pos))
        exit_ = (new != pos) & (pos != 0)
        pnl += np.where(exit_, pos * (now / entry - 1.0), 0.0)
        trans += exit_
        enter = (new != pos) & (new != 0)
        entry = np.where(enter, now, entry)
        trans += enter
        entries += enter
        pos = new
    close = p[:, -1]
    pnl += np.where(pos != 0, pos * (close / entry - 1.0), 0.0)
    trans += pos != 0
    traded = entries > 0
    z = (pnl - pnl.mean()) / pnl.std()
    return {
        "share of checks outside the band": outside / (days * len(CHECKS)),
        "share of days with at least one entry": traded.mean(),
        "entries per day": entries.mean(),
        "transactions per day": trans.mean(),
        "gross P&L per day, bp": 1e4 * pnl.mean(),
        "t-stat of gross P&L": pnl.mean() / pnl.std() * np.sqrt(days),
        "annualised gross Sharpe": pnl.mean() / pnl.std() * np.sqrt(252),
        "hit rate on days traded": (pnl[traded] > 0).mean(),
        "skewness of daily P&L": (z**3).mean(),
        "net Sharpe at 0.1 bp per transaction": (pnl - 1e-5 * trans).mean() / pnl.std() * np.sqrt(252),
        "net Sharpe at 0.5 bp per transaction": (pnl - 5e-5 * trans).mean() / pnl.std() * np.sqrt(252),
    }


def bounce(rng: np.random.Generator, spreads_bp: tuple[float, ...], bars: tuple[int, ...]) -> dict:
    days = 5000
    bar_sigma = 0.02 / np.sqrt(MINUTES)  # 2% a day, spread evenly over the session
    mid = np.cumsum(bar_sigma * rng.normal(0.0, 1.0, (days, MINUTES)), axis=1)
    side = rng.choice([-1.0, 1.0], (days, MINUTES))
    out = {}
    for s in spreads_bp:
        last = mid + 0.5 * s * 1e-4 * side
        for b in bars:
            lr = np.diff(last[:, b - 1 :: b], axis=1)
            out[(s, b)] = np.corrcoef(lr[:, :-1].ravel(), lr[:, 1:].ravel())[0, 1]
        # a one-minute reversal rule: short the sign of the last one-minute return
        lr, mr = np.diff(last, axis=1), np.diff(mid, axis=1)
        pos = -np.sign(lr[:, :-1])
        out[(s, "last")] = 1e4 * (pos * lr[:, 1:]).mean()
        out[(s, "mid")] = 1e4 * (pos * mr[:, 1:]).mean()
    return out


def stale_index(rng: np.random.Generator) -> dict[str, float]:
    days, stocks, minutes = 4000, 200, 30
    beta = rng.uniform(0.7, 1.3, stocks)
    gap_m = rng.normal(0.0, 0.007, (days, 1))
    gap = beta * gap_m + rng.normal(0.0, 0.01, (days, stocks))
    f = rng.normal(0.0, 0.0006, (days, minutes))
    e = rng.normal(0.0, 0.0012, (days, stocks, minutes))
    path = gap[:, :, None] + np.cumsum(beta[None, :, None] * f[:, None, :] + e, axis=2)
    first = np.ceil(rng.exponential(2.0, (days, stocks))).astype(int)  # minute of first trade
    t = np.arange(1, minutes + 1)
    seen = np.where(t[None, None, :] >= first[:, :, None], path, 0.0)  # stale = yesterday's close
    stale = seen.mean(axis=1)  # log level relative to yesterday's close, minutes 1..30
    true = path.mean(axis=1)
    g = gap.mean(axis=1)  # the true index's overnight gap
    out = {}
    # The cash index's 9:30 print is yesterday's close: nothing has traded yet.
    a, b = stale[:, 4], stale[:, 29] - stale[:, 4]
    out["stale cash index: corr(9:30-9:35 change, 9:35-10:00 change)"] = np.corrcoef(a, b)[0, 1]
    a, b = true[:, 4] - g, true[:, 29] - true[:, 4]
    out["true index: corr(9:30-9:35 return, 9:35-10:00 return)"] = np.corrcoef(a, b)[0, 1]
    for minute in (1, 5, 10):
        seen_share = np.cov(stale[:, minute - 1], g)[0, 1] / g.var()
        out[f"share of the overnight gap visible in the cash index after {minute} min"] = seen_share
    return out


def main() -> None:
    rng = np.random.default_rng(20260923)
    r = null_days(rng)
    days = r[BURN:]

    vr5 = variance_ratio(days, 5)
    vr1 = variance_ratio(days, 1)
    spreads, bars = (2.0, 5.0, 15.0), (1, 2, 5, 10, 15, 30)
    bnc = bounce(rng, spreads, bars)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.8, 3.9))

    edges = np.linspace(0, 12, 61)
    axL.hist(vr5, bins=edges, density=True, color=GREY, alpha=0.55, label="simulated random-walk days")
    x = np.linspace(0.05, 12, 400)
    axL.plot(x, np.exp(-x / 2) / np.sqrt(2 * np.pi * x), color=INK, lw=1.6, label="χ² with 1 d.o.f.")
    axL.axvline(3.84, color=RUST, lw=1.2, ls="--")
    share = (vr5 > 3.84).mean()
    axL.text(4.2, 0.55, f"{100 * share:.1f}% of pure-noise days\nexceed 3.84, the 5% critical\nvalue: about 12 'trend days'\na year from noise alone",
             fontsize=9, color=RUST, va="top")
    axL.set_xlim(0, 12)
    axL.set_ylim(0, 1.2)
    axL.set_xlabel("per-day variance ratio, 5-minute bars", fontsize=10, color=MUTED)
    axL.set_ylabel("density", fontsize=10, color=MUTED)
    axL.set_title("Trend days happen by chance", fontsize=11, color=INK, loc="left", pad=8)
    axL.legend(frameon=False, fontsize=8.5, loc="upper right")
    style(axL)

    grid = np.geomspace(1, 30, 200)
    for s, color in zip(spreads, (TEAL, GOLD, RUST)):
        var = (0.02**2) * grid / MINUTES
        half2 = (0.5 * s * 1e-4) ** 2
        axR.plot(grid, -half2 / (var + 2 * half2), color=color, lw=1.8, label=f"spread {s:g} bp")
        axR.scatter(bars, [bnc[(s, b)] for b in bars], s=22, color=color, edgecolor="white", linewidth=0.6, zorder=5)
    axR.axhline(0, color=GREY, lw=0.8)
    axR.set_xscale("log")
    axR.set_xticks([1, 2, 5, 10, 30], labels=["1", "2", "5", "10", "30"])
    axR.minorticks_off()
    axR.set_xlabel("bar length, minutes (stock with 2% daily volatility)", fontsize=10, color=MUTED)
    axR.set_ylabel("lag-1 autocorrelation, last-trade prices", fontsize=10, color=MUTED)
    axR.set_title("The bounce manufactures reversal", fontsize=11, color=INK, loc="left", pad=8)
    axR.legend(frameon=False, fontsize=8.5, loc="lower right")
    style(axR)

    fig.tight_layout()
    out = Path(__file__).with_suffix("")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", transparent=True, bbox_inches="tight")

    print("Per-day variance ratio on null days")
    for name, vr in (("5-minute bars", vr5), ("1-minute bars", vr1)):
        print(f"  {name}: mean {vr.mean():.3f}, P(>2.71) {(vr > 2.71).mean():.3f}, "
              f"P(>3.84) {(vr > 3.84).mean():.3f}, P(>6.63) {(vr > 6.63).mean():.4f}")
    print("  chi-squared(1): P(>2.71) 0.100, P(>3.84) 0.050, P(>6.63) 0.010")
    for bar in (5, 1):
        er = efficiency_ratio(days, bar)
        print(f"Efficiency ratio on null days, {bar}-minute bars: mean {er.mean():.3f}, median {np.median(er):.3f}")
    print("Noise-area rule (base version) on null days")
    for k, v in noise_area_rule(r).items():
        print(f"  {k}: {v:.3f}")
    print("Bid-ask bounce: lag-1 autocorrelation of last-trade returns (simulated vs Roll)")
    for s in spreads:
        half2 = (0.5 * s * 1e-4) ** 2
        row = []
        for b in bars:
            roll = -half2 / ((0.02**2) * b / MINUTES + 2 * half2)
            row.append(f"{b}m {bnc[(s, b)]:+.3f}/{roll:+.3f}")
        print(f"  spread {s:g} bp: " + ", ".join(row))
        print(f"    one-minute reversal rule, mean P&L per bar: last-trade {bnc[(s, 'last')]:+.3f} bp, "
              f"midquote {bnc[(s, 'mid')]:+.3f} bp, half-spread {s / 2:.2f} bp")
    print("Stale cash index at the open")
    for k, v in stale_index(rng).items():
        print(f"  {k}: {v:.3f}")


if __name__ == "__main__":
    main()

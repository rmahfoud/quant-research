# Ninety-nine years of the four best-known US equity return sources, from the
# Kenneth French data library: how deep and how long their drawdowns ran, how
# their returns changed after publication, and how much of a 10-month moving-
# average timing rule's return is timing rather than simply being invested.
#
# The data are downloaded (and cached in the system temp directory) rather than
# committed. The sample is pinned to end in December 2025 so the printed tables
# are stable; the library occasionally revises history, which can move the last
# digit. Offline with outputs already present, the script leaves them alone.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "st_factor_history"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

import io
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
FILES = {
    "ff3": "F-F_Research_Data_Factors_CSV.zip",
    "mom": "F-F_Momentum_Factor_CSV.zip",
}
END = 202512
CACHE = Path(tempfile.gettempdir()) / "quant_research_french"
OUT = Path(__file__).with_suffix("")


def fetch(name: str) -> str:
    CACHE.mkdir(exist_ok=True)
    path = CACHE / FILES[name]
    if not path.exists():
        with urllib.request.urlopen(BASE + FILES[name], timeout=60) as r:
            path.write_bytes(r.read())
    with zipfile.ZipFile(path) as z:
        return z.read(z.namelist()[0]).decode("latin-1")


def monthly(text: str) -> tuple[list[str], dict[int, list[float]]]:
    """The first block of YYYYMM rows, keyed by month; stops at the annual block."""
    lines = io.StringIO(text).read().splitlines()
    header, rows, started = None, {}, False
    for line in lines:
        cells = [c.strip() for c in line.split(",")]
        if not started and len(cells) > 1 and cells[0] == "" and cells[1]:
            header = cells[1:]
            started = True
            continue
        if started:
            if not cells[0].isdigit() or len(cells[0]) != 6:
                break
            rows[int(cells[0])] = [float(c) / 100 for c in cells[1:]]
    return header, rows


def load() -> dict[str, np.ndarray]:
    h3, ff3 = monthly(fetch("ff3"))
    hm, mom = monthly(fetch("mom"))
    months = sorted(m for m in ff3 if m in mom and m <= END)
    data = {"month": np.array(months)}
    for i, name in enumerate(h3):
        data[name] = np.array([ff3[m][i] for m in months])
    data["Mom"] = np.array([mom[m][0] for m in months])
    return data


def drawdown(r: np.ndarray) -> tuple[np.ndarray, float, int, int, int]:
    """Underwater curve of compounded wealth; worst depth; longest spell and where."""
    wealth = np.cumprod(1 + r)
    peak = np.maximum.accumulate(np.concatenate([[1.0], wealth]))[1:]
    under = wealth / peak - 1
    longest, start, run, best_start = 0, 0, 0, 0
    for i, u in enumerate(under):
        if u < 0:
            if run == 0:
                start = i
            run += 1
            if run > longest:
                longest, best_start = run, start
        else:
            run = 0
    return under, float(under.min()), longest, best_start, best_start + longest


def stats(r: np.ndarray) -> tuple[float, float, float, float]:
    mean, vol = 12 * r.mean(), np.sqrt(12) * r.std(ddof=1)
    sr = mean / vol
    return mean, vol, sr, sr * np.sqrt(len(r) / 12)


def label(month: int) -> str:
    return f"{month // 100}-{month % 100:02d}"


def sma_timing(d: dict[str, np.ndarray]) -> None:
    mkt, rf = d["Mkt-RF"], d["RF"]
    tri = np.cumprod(1 + mkt + rf)
    sig = np.full(len(tri), np.nan)
    for t in range(9, len(tri)):
        sig[t] = 1.0 if tri[t] > tri[t - 9 : t + 1].mean() else 0.0
    w, r, months = sig[:-1], mkt[1:], d["month"][1:]
    keep = ~np.isnan(w) & (months >= 192701)
    w, r, months = w[keep], r[keep], months[keep]

    print("\n10-month moving-average timing of the US market (signal at month-end,")
    print("held the next month; out of the market means T-bills; no costs)")
    print(
        f"{'period':<16}{'E[w]':>7}{'strat':>8}{'static':>8}{'timing':>8}"
        f"{'t(tim)':>8}{'SR mkt':>8}{'SR str':>8}{'MDD mkt':>9}{'MDD str':>9}{'sw/yr':>7}"
    )
    periods = [
        ("1927-2025", 192701, 202512),
        ("1927-1962", 192701, 196212),
        ("1963-1999", 196301, 199912),
        ("2000-2025", 200001, 202512),
        ("ex 1929-07..32", 192701, 202512),
    ]
    for name, a, b in periods:
        m = (months >= a) & (months <= b)
        if name.startswith("ex"):
            m &= ~((months >= 192907) & (months <= 193206))
        ww, rr = w[m], r[m]
        strat = ww * rr
        static = 12 * ww.mean() * rr.mean()
        timing = 12 * np.mean((ww - ww.mean()) * (rr - rr.mean()))
        x = np.column_stack([np.ones(len(ww)), ww])
        beta, res, *_ = np.linalg.lstsq(x, rr, rcond=None)
        resid = rr - x @ beta
        s2 = resid @ resid / (len(rr) - 2)
        se = np.sqrt(s2 * np.linalg.inv(x.T @ x)[1, 1])
        t_timing = beta[1] / se
        rf_m = rf[1:][keep][m]
        _, mdd_m, *_ = drawdown(rr + rf_m)
        _, mdd_s, *_ = drawdown(strat + rf_m)
        switches = np.sum(np.abs(np.diff(ww))) / (len(ww) / 12)
        print(
            f"{name:<16}{ww.mean():7.2f}{12 * strat.mean():8.2%}{static:8.2%}{timing:8.2%}"
            f"{t_timing:8.2f}{stats(rr)[2]:8.2f}{stats(strat)[2]:8.2f}"
            f"{mdd_m:9.1%}{mdd_s:9.1%}{switches:7.2f}"
        )


def publication_split(d: dict[str, np.ndarray]) -> None:
    print("\nBefore and after publication (annualised excess return, t-statistic)")
    cases = [
        ("SMB (size; Banz 1981)", "SMB", 198112),
        ("HML (value; Fama-French 1992)", "HML", 199212),
        ("Mom (momentum; Jegadeesh-Titman 1993)", "Mom", 199312),
    ]
    for name, col, cut in cases:
        r, months = d[col], d["month"]
        pre, post = r[months <= cut], r[months > cut]
        mp, _, _, tp = stats(pre)
        mq, _, _, tq = stats(post)
        print(
            f"  {name:<40} pre {mp:6.2%} (t={tp:4.1f}, {len(pre) // 12}y)"
            f"   post {mq:6.2%} (t={tq:4.1f}, {len(post) // 12}y)   change {mq / mp - 1:+.0%}"
        )


def factor_table(d: dict[str, np.ndarray]) -> list[tuple[str, np.ndarray]]:
    series = [
        ("Market (Mkt-RF)", d["Mkt-RF"]),
        ("Size (SMB)", d["SMB"]),
        ("Value (HML)", d["HML"]),
        ("Momentum (Mom)", d["Mom"]),
    ]
    months = d["month"]
    print(
        f"\nFactor history {label(months[0])} to {label(months[-1])}"
        " (monthly excess returns compounded; long-short legs fully collateralised)"
    )
    print(
        f"{'factor':<18}{'mean':>7}{'vol':>7}{'SR':>6}{'t':>6}{'MDD':>8}"
        f"{'longest underwater':>34}{'worst 12m':>11}{'neg 10y':>9}"
    )
    for name, r in series:
        mean, vol, sr, t = stats(r)
        _, mdd, longest, a, b = drawdown(r)
        roll12 = np.array([np.prod(1 + r[i : i + 12]) - 1 for i in range(len(r) - 11)])
        roll120 = np.array([np.prod(1 + r[i : i + 120]) - 1 for i in range(len(r) - 119)])
        spell = f"{longest / 12:4.1f}y ({label(months[a])}..{label(months[min(b, len(months) - 1)])})"
        print(
            f"{name:<18}{mean:7.2%}{vol:7.2%}{sr:6.2f}{t:6.1f}{mdd:8.1%}{spell:>34}"
            f"{roll12.min():11.1%}{np.mean(roll120 < 0):9.0%}"
        )
    mix = 0.5 * d["HML"] + 0.5 * d["Mom"]
    mean, vol, sr, t = stats(mix)
    _, mdd, longest, a, b = drawdown(mix)
    roll12 = np.array([np.prod(1 + mix[i : i + 12]) - 1 for i in range(len(mix) - 11)])
    roll120 = np.array([np.prod(1 + mix[i : i + 120]) - 1 for i in range(len(mix) - 119)])
    spell = f"{longest / 12:4.1f}y ({label(months[a])}..{label(months[min(b, len(months) - 1)])})"
    print(
        f"{'50/50 HML+Mom':<18}{mean:7.2%}{vol:7.2%}{sr:6.2f}{t:6.1f}{mdd:8.1%}{spell:>34}"
        f"{roll12.min():11.1%}{np.mean(roll120 < 0):9.0%}"
        f"   corr(HML, Mom) = {np.corrcoef(d['HML'], d['Mom'])[0, 1]:.2f}"
    )
    since = months >= 200001
    print("  since 2000:")
    for name, r in series:
        mean, vol, sr, t = stats(r[since])
        print(f"  {name:<16}{mean:7.2%}{vol:7.2%}{sr:6.2f}{t:6.1f}")
    return series


def figure(d: dict[str, np.ndarray], series: list[tuple[str, np.ndarray]]) -> None:
    months = d["month"]
    x = months // 100 + (months % 100 - 0.5) / 12
    fig, axes = plt.subplots(4, 1, figsize=(7.8, 7.6), sharex=True)
    colours = [INK, GREY, TEAL, RUST]
    for ax, (name, r), c in zip(axes, series, colours, strict=True):
        under, mdd, longest, a, b = drawdown(r)
        ax.fill_between(x, under * 100, 0, color=c, alpha=0.28, lw=0)
        ax.plot(x, under * 100, color=c, lw=0.9)
        b = min(b, len(x) - 1)
        ax.axvspan(x[a], x[b], color=c, alpha=0.08, lw=0)
        ax.text(
            0.995,
            0.08,
            f"{name}   worst {mdd:.0%}   longest under water {longest / 12:.1f} years"
            + (", not yet recovered" if under[-1] < 0 and b == len(x) else ""),
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=8.5,
            color=INK,
        )
        ax.set_ylim(-100, 5)
        ax.set_yticks([-75, -50, -25, 0])
        ax.tick_params(labelsize=8, colors=MUTED)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GREY)
        ax.set_ylabel("%", fontsize=8.5, color=MUTED, rotation=0, labelpad=8)
    axes[0].set_title(
        "Distance below the previous peak, US equity factors, 1927–2025",
        fontsize=10,
        color=INK,
        pad=8,
    )
    axes[-1].set_xlim(x[0], x[-1] + 0.1)
    fig.text(
        0.5,
        -0.01,
        "Shaded band: the longest spell below a previous peak. Monthly data from the Kenneth R. French data library.",
        ha="center",
        fontsize=8.2,
        color=MUTED,
    )
    fig.tight_layout()
    for ext in ("pdf", "svg"):
        fig.savefig(f"{OUT}.{ext}", transparent=True, bbox_inches="tight")


def main() -> None:
    try:
        d = load()
    except OSError as e:
        if Path(f"{OUT}.svg").exists():
            print(f"offline ({e}); leaving the committed st_factor_history outputs in place")
            return
        sys.exit(f"cannot download the French data library: {e}")
    series = factor_table(d)
    publication_split(d)
    sma_timing(d)
    figure(d, series)


main()

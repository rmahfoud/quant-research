# Shared data and estimators for the value-at-risk figures (var_*.py), and the
# worked numbers quoted in value_at_risk.md: run this file directly to print them.
#
# Data are daily US equity returns from the Kenneth French data library: the
# value-weighted market, and the ten value-weighted industry portfolios that
# stand in for sector funds in the worked portfolio. They are downloaded (and
# cached in the system temp directory) rather than committed, and pinned to end
# in December 2025 so the printed tables are stable; the library occasionally
# revises history, which can move the last digit.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import io
import math
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
FILES = {
    "factors": "F-F_Research_Data_Factors_daily_CSV.zip",
    "industries": "10_Industry_Portfolios_daily_CSV.zip",
}
END = 20251231
CACHE = Path(tempfile.gettempdir()) / "quant_research_french"

Z95, Z99 = 1.6449, 2.3263
LAMBDA = 0.94

# The worked account: five sector funds, dollars held.
ACCOUNT = 100_000.0
POSITIONS = {"HiTec": 40_000.0, "Hlth": 20_000.0, "Enrgy": 15_000.0, "Utils": 15_000.0, "Durbl": 10_000.0}
LABELS = {"HiTec": "Technology", "Hlth": "Health care", "Enrgy": "Energy", "Utils": "Utilities", "Durbl": "Autos and durables"}


def fetch(name: str) -> str:
    CACHE.mkdir(exist_ok=True)
    path = CACHE / FILES[name]
    if not path.exists():
        with urllib.request.urlopen(BASE + FILES[name], timeout=60) as r:
            path.write_bytes(r.read())
    with zipfile.ZipFile(path) as z:
        return z.read(z.namelist()[0]).decode("latin-1")


def daily_block(text: str) -> tuple[list[str], np.ndarray, np.ndarray]:
    header, dates, rows, started = [], [], [], False
    for line in io.StringIO(text).read().splitlines():
        cells = [c.strip() for c in line.split(",")]
        if not started:
            if len(cells) > 1 and cells[0] == "" and cells[1]:
                header, started = cells[1:], True
            continue
        if not cells[0].isdigit() or len(cells[0]) != 8:
            break
        if int(cells[0]) > END:
            break
        dates.append(int(cells[0]))
        rows.append([float(c) / 100 for c in cells[1:]])
    return header, np.array(dates), np.array(rows)


def load_market() -> tuple[np.ndarray, np.ndarray]:
    header, dates, rows = daily_block(fetch("factors"))
    return dates, rows[:, header.index("Mkt-RF")] + rows[:, header.index("RF")]


def load_industries() -> tuple[list[str], np.ndarray, np.ndarray]:
    return daily_block(fetch("industries"))


def load_or_exit(out: Path, loader):
    try:
        return loader()
    except OSError as e:
        if out.with_suffix(".svg").exists():
            print(f"offline ({e}); leaving the committed {out.name} outputs in place")
            sys.exit(0)
        sys.exit(f"cannot download the French data library: {e}")


def year_fraction(dates: np.ndarray) -> np.ndarray:
    y, m, d = dates // 10000, dates // 100 % 100, dates % 100
    return y + (m - 1) / 12 + (d - 1) / 365


# --- volatility and VaR forecasts; entry t uses data through t-1 only --------


def ewma_vol(r: np.ndarray, lam: float = LAMBDA, seed: int = 250) -> np.ndarray:
    var = np.empty(len(r))
    var[0] = np.mean(r[:seed] ** 2)
    for t in range(1, len(r)):
        var[t] = lam * var[t - 1] + (1 - lam) * r[t - 1] ** 2
    return np.sqrt(var)


def rolling_vol(r: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(r), np.nan)
    w = np.lib.stride_tricks.sliding_window_view(r, n)
    out[n:] = w.std(axis=1, ddof=1)[:-1]
    return out


def hs_var(r: np.ndarray, n: int, level: float) -> np.ndarray:
    out = np.full(len(r), np.nan)
    w = np.lib.stride_tricks.sliding_window_view(r, n)
    out[n:] = -np.quantile(w, 1 - level, axis=1)[:-1]
    return out


def brw_var(r: np.ndarray, n: int, level: float, decay: float = 0.98) -> np.ndarray:
    out = np.full(len(r), np.nan)
    weights = decay ** np.arange(n - 1, -1, -1)
    weights /= weights.sum()
    w = np.lib.stride_tricks.sliding_window_view(r, n)[:-1]
    order = np.argsort(w, axis=1)
    cum = np.cumsum(weights[order], axis=1)
    idx = np.argmax(cum >= 1 - level, axis=1)
    out[n:] = -np.take_along_axis(w, np.take_along_axis(order, idx[:, None], axis=1), axis=1)[:, 0]
    return out


def fhs_var(r: np.ndarray, vol: np.ndarray, n: int, level: float) -> np.ndarray:
    z = r / vol
    out = np.full(len(r), np.nan)
    w = np.lib.stride_tricks.sliding_window_view(z, n)
    out[n:] = -np.quantile(w, 1 - level, axis=1)[:-1] * vol[n:]
    return out


# --- Student t without scipy --------------------------------------------------


def t_pdf(x: np.ndarray, nu: float) -> np.ndarray:
    c = math.gamma((nu + 1) / 2) / (math.sqrt(nu * math.pi) * math.gamma(nu / 2))
    return c * (1 + x**2 / nu) ** (-(nu + 1) / 2)


def t_quantile(p: float, nu: float) -> float:
    x = np.linspace(-200, 0, 2_000_001)
    cdf = np.cumsum(t_pdf(x, nu)) * (x[1] - x[0])
    cdf += 0.5 - cdf[-1]
    return float(-np.interp(1 - p, cdf, x)) if p > 0.5 else float(np.interp(p, cdf, x))


def t_es(p: float, nu: float) -> float:
    q = t_quantile(p, nu)
    return float(t_pdf(np.array([q]), nu)[0] / (1 - p) * (nu + q**2) / (nu - 1))


def norm_pdf(x: float) -> float:
    return math.exp(-(x**2) / 2) / math.sqrt(2 * math.pi)


# --- backtests ----------------------------------------------------------------


def chi2_1_pvalue(lr: float) -> float:
    return math.erfc(math.sqrt(max(lr, 0.0) / 2))


def xlogy(x: float, y: float) -> float:
    return 0.0 if x == 0 else x * math.log(y)


def kupiec(hits: np.ndarray, p: float) -> tuple[float, float]:
    n, x = len(hits), int(hits.sum())
    pi = x / n
    lr = -2 * (xlogy(n - x, 1 - p) + xlogy(x, p) - xlogy(n - x, 1 - pi) - xlogy(x, pi))
    return lr, chi2_1_pvalue(lr)


def christoffersen(hits: np.ndarray) -> tuple[float, float, float]:
    a, b = hits[:-1], hits[1:]
    n00, n01 = int(np.sum(~a & ~b)), int(np.sum(~a & b))
    n10, n11 = int(np.sum(a & ~b)), int(np.sum(a & b))
    p01, p11 = n01 / (n00 + n01), n11 / max(n10 + n11, 1)
    p = (n01 + n11) / (n00 + n01 + n10 + n11)
    l0 = xlogy(n00 + n10, 1 - p) + xlogy(n01 + n11, p)
    l1 = xlogy(n00, 1 - p01) + xlogy(n01, p01) + xlogy(n10, 1 - p11) + xlogy(n11, p11)
    lr = -2 * (l0 - l1)
    return p11, lr, chi2_1_pvalue(lr)


def pinball(r: np.ndarray, var: np.ndarray, level: float) -> float:
    q, tau = -var, 1 - level
    return float(np.mean((tau - (r < q)) * (r - q)))


def binom_cdf(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k + 1))


# --- the minimal recipe quoted in section 14 of the document -----------------


def ewma_cov(R: np.ndarray, lam: float = LAMBDA) -> np.ndarray:
    S = np.cov(R[:60], rowvar=False)
    for x in R[60:]:
        S = lam * S + (1 - lam) * np.outer(x, x)
    return S


def risk_report(R: np.ndarray, pos: np.ndarray, lam: float = LAMBDA, window: int = 500) -> dict:
    S = ewma_cov(R, lam)
    sigma = math.sqrt(pos @ S @ pos)
    component = Z95 * pos * (S @ pos) / sigma

    pnl = R[-window:] @ pos
    hs95, hs99 = -np.quantile(pnl, 0.05), -np.quantile(pnl, 0.01)
    es975 = -pnl[pnl <= np.quantile(pnl, 0.025)].mean()

    past_vol = ewma_vol(R @ pos, lam, seed=60)[-window:]
    fhs95 = -np.quantile(pnl / past_vol, 0.05) * sigma
    fhs99 = -np.quantile(pnl / past_vol, 0.01) * sigma

    tail = pnl <= np.quantile(pnl, 0.05)
    tail_share = (R[-window:][tail] * pos).mean(axis=0)
    return {
        "sigma": sigma,
        "normal95": Z95 * sigma,
        "normal99": Z99 * sigma,
        "component": component,
        "standalone": Z95 * np.abs(pos) * np.sqrt(np.diag(S)),
        "hs95": hs95,
        "hs99": hs99,
        "es975": es975,
        "fhs95": fhs95,
        "fhs99": fhs99,
        "tail_share": -tail_share,
    }


def minimal_report(R: np.ndarray, pos: np.ndarray, window: int = 500) -> tuple[float, float, float, float, np.ndarray]:
    S = ewma_cov(R)
    sigma = math.sqrt(pos @ S @ pos)
    component = Z95 * pos * (S @ pos) / sigma
    pnl = R @ pos
    z = (pnl / ewma_vol(pnl, seed=60))[-window:]
    var95, var99 = -np.quantile(z, [0.05, 0.01]) * sigma
    es975 = -z[z <= np.quantile(z, 0.025)].mean() * sigma
    return sigma, var95, var99, es975, component


def minimal_backtest(R: np.ndarray, pos: np.ndarray, level: float = 0.95, days: int = 500, window: int = 500) -> int:
    pnl = R @ pos
    vol = ewma_vol(pnl, seed=60)
    z = pnl / vol
    hits = 0
    for t in range(len(pnl) - days, len(pnl)):
        hits += pnl[t] < np.quantile(z[t - window : t], 1 - level) * vol[t]
    return int(hits)


# --- printed tables -----------------------------------------------------------


def unconditional(dates: np.ndarray, r: np.ndarray) -> None:
    mu, sd = r.mean(), r.std(ddof=1)
    z = (r - mu) / sd
    print(f"US market daily returns {dates[0]}..{dates[-1]}, n={len(r)}")
    print(
        f"  mean {mu:.4%}  sd {sd:.3%}  (annualised {sd * math.sqrt(252):.1%})"
        f"  skew {np.mean(z**3):.2f}  kurtosis {np.mean(z**4):.1f}"
    )
    for level, zq in ((0.95, Z95), (0.99, Z99), (0.999, 3.0902)):
        emp = -np.quantile(r, 1 - level)
        print(f"  {level:.1%} loss quantile: empirical {emp:.2%} = {emp / sd:.2f} sd; normal says {zq:.2f} sd")
    for k in (3, 4, 5, 6):
        expected = len(r) * 0.5 * math.erfc(k / math.sqrt(2))
        print(f"  days worse than -{k} sd: {int(np.sum(z < -k)):4d}   normal expects {expected:.3g}")
    ew = ewma_vol(r)
    print("  worst days: return, in full-sample sd, in that morning's EWMA(0.94) vol, and the EWMA vol")
    for i in np.argsort(r)[:8]:
        print(f"    {dates[i]}: {r[i]:7.2%}  {z[i]:6.1f} sd  {r[i] / ew[i]:6.1f} conditional  (vol {ew[i]:.2%})")
    zc = r[1000:] / ew[1000:]
    print(f"  EWMA-standardised returns from {dates[1000]}: sd {zc.std():.3f}  kurtosis {np.mean(((zc - zc.mean()) / zc.std()) ** 4):.1f}"
          f"  95% {-np.quantile(zc, 0.05):.2f}  99% {-np.quantile(zc, 0.01):.2f}  99.9% {-np.quantile(zc, 0.001):.2f}")
    i = int(np.argmin(r))
    print(f"  worst day {dates[i]}: {r[i]:.2%} = {z[i]:.1f} sd")
    last = r[-500:]
    print(
        f"  last 500 days: sd {last.std(ddof=1):.3%}; on $100k, normal 95%/99% VaR "
        f"${Z95 * last.std(ddof=1) * 1e5:,.0f} / ${Z99 * last.std(ddof=1) * 1e5:,.0f}; "
        f"HS 95%/99% ${-np.quantile(last, 0.05) * 1e5:,.0f} / ${-np.quantile(last, 0.01) * 1e5:,.0f}; "
        f"ES 97.5% ${-last[last <= np.quantile(last, 0.025)].mean() * 1e5:,.0f}; worst ${-last.min() * 1e5:,.0f}"
    )


def method_forecasts(r: np.ndarray, level: float) -> dict[str, np.ndarray]:
    z = Z95 if level == 0.95 else Z99
    nu = 5.0
    zt = -t_quantile(1 - level, nu) * math.sqrt((nu - 2) / nu)
    ew = ewma_vol(r)
    return {
        "Normal, 250d equal-weight vol": z * rolling_vol(r, 250),
        "Normal, EWMA 0.94 (RiskMetrics)": z * ew,
        "Student t(5), EWMA 0.94": zt * ew,
        "Historical simulation, 250d": hs_var(r, 250, level),
        "Historical simulation, 1000d": hs_var(r, 1000, level),
        "Age-weighted HS (BRW 0.98), 250d": brw_var(r, 250, level),
        "Filtered HS, EWMA + 1000d": fhs_var(r, ew, 1000, level),
    }


def backtests(dates: np.ndarray, r: np.ndarray) -> None:
    start = 1000
    for level in (0.95, 0.99):
        p = 1 - level
        print(f"\nOne-day {level:.0%} VaR backtest, {dates[start]}..{dates[-1]}, n={len(r) - start}, expected rate {p:.1%}")
        print(
            f"{'method':<34}{'hits':>6}{'rate':>7}{'Kupiec p':>10}{'P(hit|hit)':>11}{'indep p':>9}"
            f"{'mean VaR':>10}{'VaR sd':>8}{'loss/VaR':>9}{'pinball':>9}"
        )
        for name, var in method_forecasts(r, level).items():
            v, x = var[start:], r[start:]
            hits = x < -v
            _, pk = kupiec(hits, p)
            p11, _, pi = christoffersen(hits)
            print(
                f"{name:<34}{hits.sum():6d}{hits.mean():7.2%}{pk:10.3g}{p11:11.1%}{pi:9.2g}"
                f"{v.mean():10.2%}{v.std():8.2%}{np.mean(-x[hits] / v[hits]):9.2f}{pinball(x, v, level) * 1e4:9.3f}"
            )
    for label, a, b in (("2007-2009", 20070101, 20091231), ("2020", 20200101, 20201231), ("2017", 20170101, 20171231)):
        m = (dates >= a) & (dates <= b)
        print(f"\n99% exceedances in {label} ({m.sum()} days, expected {0.01 * m.sum():.1f}):")
        for name, var in method_forecasts(r, 0.99).items():
            print(f"  {name:<34}{int(np.sum(r[m] < -var[m])):4d}   95%: {int(np.sum(r[m] < -method_forecasts(r, 0.95)[name][m])):4d}")


def procyclicality(dates: np.ndarray, r: np.ndarray) -> None:
    ew = ewma_vol(r)
    print("\nEWMA(0.94) daily volatility, and the position a constant-VaR book could hold")
    for a, b in ((20070101, 20091231), (20190101, 20201231)):
        m = (dates >= a) & (dates <= b)
        lo, hi = int(np.argmin(np.where(m, ew, np.inf))), int(np.argmax(np.where(m, ew, -np.inf)))
        print(
            f"  {a // 10000}-{b // 10000}: low {ew[lo]:.2%} on {dates[lo]}, high {ew[hi]:.2%} on {dates[hi]}"
            f"  -> ratio {ew[hi] / ew[lo]:.1f}, position cut to {ew[lo] / ew[hi]:.0%}"
        )
    hs = hs_var(r, 250, 0.99)
    m = (dates >= 20070101) & (dates <= 20101231)
    lo, hi = int(np.argmin(np.where(m, hs, np.inf))), int(np.argmax(np.where(m, hs, -np.inf)))
    print(f"  250d HS 99% VaR: low {hs[lo]:.2%} on {dates[lo]}, high {hs[hi]:.2%} on {dates[hi]}")
    last_high = int(np.max(np.where(m & (hs > 0.9 * hs[hi]))[0]))
    print(f"  ...and stays within 10% of its high until {dates[last_high]}")


def root_time(dates: np.ndarray, r: np.ndarray) -> None:
    h = 10
    ew = ewma_vol(r)
    start = 1000
    logr = np.log1p(r)
    c = np.concatenate([[0.0], np.cumsum(logr)])
    idx = np.arange(start, len(r) - h)
    rh = np.expm1(c[idx + h] - c[idx])
    scaled = rh / (ew[idx] * math.sqrt(h))
    q1 = -np.quantile(r[start:], 0.01)
    print(f"\nSquare-root-of-time, {h}-day horizon, overlapping windows from {dates[start]}")
    print(f"  unconditional: 1-day 99% {q1:.2%} x sqrt({h}) = {q1 * math.sqrt(h):.2%}; empirical {h}-day 99% {-np.quantile(rh, 0.01):.2%}")
    edges = np.quantile(ew[idx], [0.2, 0.4, 0.6, 0.8])
    bucket = np.searchsorted(edges, ew[idx])
    print("  10-day loss / (today's EWMA vol x sqrt(10)), by today's volatility quintile; normal says 1.64 and 2.33")
    for b in range(5):
        s = scaled[bucket == b]
        print(
            f"    quintile {b + 1}: mean vol {ew[idx][bucket == b].mean():.2%}   95%: {-np.quantile(s, 0.05):.2f}"
            f"   99%: {-np.quantile(s, 0.01):.2f}   breach rate of scaled 99% VaR: {np.mean(s < -Z99):.2%}"
        )
    print(f"    all: 95%: {-np.quantile(scaled, 0.05):.2f}   99%: {-np.quantile(scaled, 0.01):.2f}   breach rate {np.mean(scaled < -Z99):.2%}")


def tail_ratios() -> None:
    print("\nExpected shortfall against VaR, in units of the standard deviation")
    es_n = norm_pdf(1.95996) / 0.025
    print(f"  normal: VaR99 {Z99:.3f}  ES97.5 {es_n:.3f}  ES99 {norm_pdf(Z99) / 0.01:.3f}  ES95 {norm_pdf(Z95) / 0.05:.3f}")
    for nu in (3.0, 4.0, 5.0, 6.0, 10.0):
        s = math.sqrt((nu - 2) / nu)
        print(
            f"  t({nu:.0f}): VaR95 {t_quantile(0.95, nu) * s:.3f}  VaR99 {t_quantile(0.99, nu) * s:.3f}"
            f"  ES97.5 {t_es(0.975, nu) * s:.3f}  ES99 {t_es(0.99, nu) * s:.3f}"
            f"  ES97.5/VaR99 {t_es(0.975, nu) / t_quantile(0.99, nu):.3f}"
        )


def traffic_light() -> None:
    print("\nBasel traffic light, 250 days at 99%")
    for p in (0.01, 0.02, 0.03, 0.04):
        green, red = binom_cdf(4, 250, p), 1 - binom_cdf(9, 250, p)
        print(f"  true breach rate {p:.0%}: P(green, <=4) {green:.1%}   P(yellow, 5-9) {1 - green - red:.1%}   P(red, >=10) {red:.2%}")
    for n in (250, 500):
        k = next(k for k in range(n) if 1 - binom_cdf(k - 1, n, 0.05) <= 0.05)
        print(f"  95% model, n={n}: reject if hits >= {k}; power against a true 7.5%: {1 - binom_cdf(k - 1, n, 0.075):.0%}, against 10%: {1 - binom_cdf(k - 1, n, 0.10):.0%}")
    for n in (250, 500, 1000, 2500):
        for p1 in (0.02,):
            k = next(k for k in range(n) if 1 - binom_cdf(k - 1, n, 0.01) <= 0.05)
            print(f"  n={n}: reject a 99% model at 5% if hits >= {k}; power against a true {p1:.0%}: {1 - binom_cdf(k - 1, n, p1):.0%}")


def estimation_error(trials: int = 20_000) -> dict[int, dict[str, np.ndarray]]:
    rng = np.random.default_rng(20261002)
    nu = 4.0
    s = math.sqrt((nu - 2) / nu)
    truth = {
        "VaR 95% (HS)": -t_quantile(0.05, nu) * s,
        "VaR 99% (HS)": -t_quantile(0.01, nu) * s,
        "ES 97.5% (HS)": t_es(0.975, nu) * s,
        "VaR 99% (normal)": -t_quantile(0.01, nu) * s,
    }
    out = {}
    print(f"\nSampling error of one-day risk estimates, IID Student t(4), {trials} trials; ratio of estimate to truth")
    print(f"{'window':>7}  " + "".join(f"{k:>30}" for k in truth))
    for n in (250, 500, 1000, 2500):
        x = rng.standard_t(nu, size=(trials, n)) * s
        q025 = np.quantile(x, 0.025, axis=1)
        est = {
            "VaR 95% (HS)": -np.quantile(x, 0.05, axis=1),
            "VaR 99% (HS)": -np.quantile(x, 0.01, axis=1),
            "ES 97.5% (HS)": -np.array([row[row <= q].mean() for row, q in zip(x, q025, strict=True)]),
            "VaR 99% (normal)": Z99 * x.std(axis=1, ddof=1),
        }
        out[n] = {k: est[k] / truth[k] for k in truth}
        cells = []
        for k in truth:
            lo, mid, hi = np.quantile(out[n][k], [0.05, 0.5, 0.95])
            cells.append(f"{mid:8.2f} [{lo:.2f}, {hi:.2f}]".rjust(30))
        print(f"{n:>7}  " + "".join(cells))
    print("  truth, in sd units: " + "  ".join(f"{k} {v:.3f}" for k, v in truth.items()))
    return out


def portfolio(names: list[str], dates: np.ndarray, rows: np.ndarray) -> None:
    cols = [names.index(k) for k in POSITIONS]
    R, pos = rows[:, cols], np.array(list(POSITIONS.values()))
    rep = risk_report(R, pos)
    print(f"\nWorked portfolio as of {dates[-1]}: ${pos.sum():,.0f} in five sector funds")
    print(f"  one-day sd ${rep['sigma']:,.0f}  normal VaR 95% ${rep['normal95']:,.0f}  99% ${rep['normal99']:,.0f}")
    print(f"  HS(500) VaR 95% ${rep['hs95']:,.0f}  99% ${rep['hs99']:,.0f}  ES 97.5% ${rep['es975']:,.0f}")
    print(f"  FHS(500) VaR 95% ${rep['fhs95']:,.0f}  99% ${rep['fhs99']:,.0f}")
    print(f"  10-day 99% by root-time: ${rep['normal99'] * math.sqrt(10):,.0f} (normal)  ${rep['fhs99'] * math.sqrt(10):,.0f} (FHS)")
    print(f"  sum of stand-alone 95% VaRs ${rep['standalone'].sum():,.0f}; diversification benefit ${rep['standalone'].sum() - rep['normal95']:,.0f}")
    print(f"{'position':<22}{'dollars':>10}{'weight':>8}{'daily vol':>10}{'standalone':>12}{'component':>11}{'risk share':>11}{'tail-day loss':>14}{'tail share':>11}")
    S = ewma_cov(R)
    for i, k in enumerate(POSITIONS):
        print(
            f"{LABELS[k]:<22}{pos[i]:10,.0f}{pos[i] / pos.sum():8.0%}{math.sqrt(S[i, i]):10.2%}{rep['standalone'][i]:12,.0f}"
            f"{rep['component'][i]:11,.0f}{rep['component'][i] / rep['normal95']:11.0%}"
            f"{rep['tail_share'][i]:14,.0f}{rep['tail_share'][i] / rep['tail_share'].sum():11.0%}"
        )
    corr = S / np.sqrt(np.outer(np.diag(S), np.diag(S)))
    print("  EWMA correlations:", np.array2string(corr, precision=2, suppress_small=True).replace("\n", " "))

    print("  incremental 95% VaR of removing each position entirely (full recomputation):")
    for i, k in enumerate(POSITIONS):
        p2 = pos.copy()
        p2[i] = 0
        print(f"    without {LABELS[k]:<20} VaR ${Z95 * math.sqrt(p2 @ S @ p2):,.0f}  change ${Z95 * math.sqrt(p2 @ S @ p2) - rep['normal95']:,.0f}")

    pnl = R @ pos
    print("  historical replays on today's dollar positions (one-day):")
    for d in (19871019, 20081015, 20200316, 20220913, 20250404):
        i = int(np.where(dates == d)[0][0])
        print(f"    {d}: ${pnl[i]:,.0f} ({pnl[i] / pos.sum():.1%}) = {-pnl[i] / rep['normal95']:.1f}x today's 95% VaR")
    c = np.concatenate([[0.0], np.cumsum(pnl)])
    for label, a, b in (("2000-03..2002-10", 20000324, 20021009), ("2007-10..2009-03", 20071009, 20090309), ("2020-02..2020-03", 20200219, 20200323), ("2022-01..2022-10", 20220103, 20221012)):
        ia, ib = int(np.searchsorted(dates, a)), int(np.searchsorted(dates, b))
        print(f"    {label}: ${c[ib + 1] - c[ia]:,.0f} (sum of daily P&L on constant dollar positions)")
    w20 = c[20:] - c[:-20]
    j = int(np.argmin(w20))
    print(f"    worst 20-day window ever: ${w20[j]:,.0f} ending {dates[j + 19]}; worst since 2000: ${w20[np.searchsorted(dates, 20000101):].min():,.0f}")

    sigma, v95, v99, es, comp = minimal_report(R, pos)
    print(f"  minimal recipe: sd ${sigma:,.0f}  FHS VaR 95% ${v95:,.0f}  99% ${v99:,.0f}  ES 97.5% ${es:,.0f}  components {np.round(comp).astype(int).tolist()}")
    print(f"  ...as multiples of sd: {v95 / sigma:.2f} / {v99 / sigma:.2f} / {es / sigma:.2f}")
    for level, days in ((0.95, 500), (0.99, 500), (0.95, 2500), (0.99, 2500)):
        print(f"  minimal backtest {level:.0%}, last {days} days: {minimal_backtest(R, pos, level, days)} hits (expected {days * (1 - level):.1f})")
    print("  walk-forward backtest of the recipe on these positions, last 2500 days:")
    n = 2500
    port = R @ pos
    vol = ewma_vol(port, seed=60)
    for name, var in (
        ("normal EWMA 95%", Z95 * vol),
        ("normal EWMA 99%", Z99 * vol),
        ("FHS 95%", fhs_var(port, vol, 500, 0.95)),
        ("FHS 99%", fhs_var(port, vol, 500, 0.99)),
        ("HS(500) 95%", hs_var(port, 500, 0.95)),
        ("HS(500) 99%", hs_var(port, 500, 0.99)),
    ):
        level = 0.95 if "95" in name else 0.99
        hits = port[-n:] < -var[-n:]
        _, pk = kupiec(hits, 1 - level)
        p11, _, pi = christoffersen(hits)
        print(f"    {name:<18} hits {hits.sum():4d} (expected {n * (1 - level):.0f})  Kupiec p {pk:.2g}  P(hit|hit) {p11:.1%}  indep p {pi:.2g}")


def norm_cdf(x: float) -> float:
    return 0.5 * math.erfc(-x / math.sqrt(2))


def bs_put(s: float, k: float, t: float, vol: float) -> tuple[float, float]:
    d1 = (math.log(s / k) + 0.5 * vol**2 * t) / (vol * math.sqrt(t))
    d2 = d1 - vol * math.sqrt(t)
    return k * norm_cdf(-d2) - s * norm_cdf(-d1), norm_cdf(d1) - 1


def option_example() -> None:
    s0, vol, t, shares = 100.0, 0.20, 30 / 365, 1000
    daily = vol / math.sqrt(252)
    print(f"\nShort 10 put contracts ({shares} shares), spot {s0:.0f}, implied vol {vol:.0%}, 30 days; underlying daily vol {daily:.2%}")
    for k in (100.0, 90.0):
        price, delta = bs_put(s0, k, t, vol)
        dn = -delta * shares * s0 * Z99 * daily
        s1 = s0 * (1 - Z99 * daily)
        full = (bs_put(s1, k, t - 1 / 365, vol)[0] - price) * shares
        full_vol = (bs_put(s1, k, t - 1 / 365, vol + 0.05)[0] - price) * shares
        crash = (bs_put(s0 * 0.9, k, t - 1 / 365, 2 * vol)[0] - price) * shares
        crash20 = (bs_put(s0 * 0.8, k, t - 1 / 365, 3 * vol)[0] - price) * shares
        print(
            f"  strike {k:.0f}: premium ${price * shares:,.0f}  delta {delta:.3f}  delta-normal 99% VaR ${dn:,.0f}"
            f"  full reval at -{Z99 * daily:.2%} ${full:,.0f}  ...with vol +5 pts ${full_vol:,.0f}"
            f"  -10% day, vol doubled ${crash:,.0f} ({crash / dn:.0f}x delta-normal VaR)"
            f"  -20% day, vol tripled ${crash20:,.0f}"
        )


def drawdown_multiple(dates: np.ndarray, r: np.ndarray) -> None:
    ew = ewma_vol(r)
    years = dates // 10000
    mdd_ratio, worst_ratio, mdds = [], [], []
    for y in range(1930, 2026):
        m = years == y
        wealth = np.cumprod(1 + r[m])
        peak = np.maximum.accumulate(np.concatenate([[1.0], wealth]))[1:]
        mdd = -(wealth / peak - 1).min()
        var95 = Z95 * ew[m].mean()
        mdds.append(mdd)
        mdd_ratio.append(mdd / var95)
        worst_ratio.append(-r[m].min() / var95)
    q = np.quantile(mdd_ratio, [0.1, 0.25, 0.5, 0.75, 0.9])
    print("\nWithin-calendar-year maximum drawdown of the US market as a multiple of that year's average one-day 95% VaR, 1930-2025")
    print(f"  10/25/50/75/90th percentiles: {q[0]:.1f} / {q[1]:.1f} / {q[2]:.1f} / {q[3]:.1f} / {q[4]:.1f};  max {max(mdd_ratio):.1f}")
    print(f"  median drawdown {np.median(mdds):.1%}; worst single day as a multiple of average VaR: median {np.median(worst_ratio):.1f}, 90th pct {np.quantile(worst_ratio, 0.9):.1f}")


def cornish_fisher(r: np.ndarray) -> None:
    z = (r - r.mean()) / r.std(ddof=1)
    skew, exkurt = float(np.mean(z**3)), float(np.mean(z**4) - 3)
    print(f"\nCornish-Fisher multipliers with the full-sample skew {skew:.2f} and excess kurtosis {exkurt:.1f}")
    for level, zq in ((0.95, Z95), (0.99, Z99)):
        q = -zq
        cf = q + (q**2 - 1) * skew / 6 + (q**3 - 3 * q) * exkurt / 24 - (2 * q**3 - 5 * q) * skew**2 / 36
        print(f"  {level:.0%}: Cornish-Fisher {-cf:.2f}   empirical {-np.quantile(z, 1 - level):.2f}   normal {zq:.2f}")


def disclosure(names: list[str], dates: np.ndarray, rows: np.ndarray) -> None:
    cols = [names.index(k) for k in POSITIONS]
    R, pos = rows[:, cols], np.array(list(POSITIONS.values()))
    start = int(np.searchsorted(dates, 20250101))
    S = np.cov(R[:60], rowvar=False)
    single, total = [], []
    for t in range(60, len(R)):
        if t >= start:
            single.append(Z95 * np.abs(pos) * np.sqrt(np.diag(S)))
            total.append(Z95 * math.sqrt(pos @ S @ pos))
        S = LAMBDA * S + (1 - LAMBDA) * np.outer(R[t], R[t])
    single, total = np.array(single), np.array(total)
    print("\nDisclosure-style table for 2025: one-day 95% VaR, EWMA normal, positions held at year-end size")
    print(f"{'':<22}{'average':>9}{'high':>8}{'low':>8}{'year-end':>10}")
    for i, k in enumerate(POSITIONS):
        c = single[:, i]
        print(f"{LABELS[k]:<22}{c.mean():9,.0f}{c.max():8,.0f}{c.min():8,.0f}{c[-1]:10,.0f}")
    div = total - single.sum(axis=1)
    print(f"{'diversification':<22}{div.mean():9,.0f}{'':>8}{'':>8}{div[-1]:10,.0f}")
    print(f"{'total':<22}{total.mean():9,.0f}{total.max():8,.0f}{total.min():8,.0f}{total[-1]:10,.0f}")
    print(f"  total high on {dates[start + int(np.argmax(total))]}, low on {dates[start + int(np.argmin(total))]}")
    pnl = R[start:] @ pos
    var_path = np.array(total)
    hits = pnl < -var_path
    print(f"  2025 exceedances of this 95% VaR: {hits.sum()} of {len(pnl)} (expected {0.05 * len(pnl):.1f}); worst day {pnl.min():,.0f} on {dates[start + int(np.argmin(pnl))]}")

    print("\nScenario matrix: one-day P&L by position under replayed days")
    days = (19871019, 20081015, 20200316, 20250404, 20220913)
    print(f"{'':<22}" + "".join(f"{d:>11}" for d in days))
    for i, k in enumerate(POSITIONS):
        print(f"{LABELS[k]:<22}" + "".join(f"{pos[i] * rows[int(np.where(dates == d)[0][0]), cols[i]]:11,.0f}" for d in days))
    print(f"{'total':<22}" + "".join(f"{R[int(np.where(dates == d)[0][0])] @ pos:11,.0f}" for d in days))


def main() -> None:
    dates, r = load_market()
    unconditional(dates, r)
    backtests(dates, r)
    procyclicality(dates, r)
    cornish_fisher(r)
    root_time(dates, r)
    tail_ratios()
    traffic_light()
    estimation_error()
    option_example()
    drawdown_multiple(dates, r)
    names, idates, rows = load_industries()
    portfolio(names, idates, rows)
    disclosure(names, idates, rows)


if __name__ == "__main__":
    main()

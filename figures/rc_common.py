# Shared data, labels, features and models for the worked examples in
# regime_classification.md (rc_*.py). Run this file directly to print every
# number the chapter quotes from them.
#
# Data, all public and downloaded (then cached in the system temp directory)
# rather than committed, and pinned to end in December 2025 so the printed
# tables are stable:
#   - the daily value-weighted US market return from the Kenneth French data
#     library (1926 onward), the price path every label is computed from;
#   - the Cboe VIX and VIX3M indexes from Cboe's public history files;
#   - BAA10Y (Moody's Baa yield minus the 10-year Treasury yield), T10Y3M
#     (10-year minus 3-month Treasury yield) and USREC (NBER recession months)
#     from FRED's public CSV endpoint.
#
# Run standalone:  uv run --no-project --with matplotlib python <path>

import bisect
import io
import math
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
FAINT = "#DCE4E6"
GOLD = "#B07D1A"

A = 252
END = 20251231
CACHE = Path(tempfile.gettempdir()) / "quant_research_regimes"
FRENCH = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip"
CBOE = "https://cdn.cboe.com/api/global/us_indices/daily_prices/{}_History.csv"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"

H_VOL = 21  # forward realised-volatility label horizon
H_RISK = 63  # forward drawdown and forward return label horizon
VOL_Q = 0.80  # forward-volatility label: above the expanding 80th percentile
DD_LEVEL = 0.10  # forward drawdown label: a 10% drawdown inside the window
MIN_HISTORY = 5 * A  # burn-in before an expanding quantile is used
JM_LAMBDA = 40.0  # jump penalty of the statistical jump model
SEED = 20261012


# ---------------------------------------------------------------------------
# Data


def _fetch(url: str, name: str) -> bytes:
    CACHE.mkdir(exist_ok=True)
    path = CACHE / name
    if not path.exists():
        # FRED rejects browser user agents from scripts; the default one works.
        req = (
            urllib.request.Request(url)
            if "fred" in url
            else urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        )
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    return path.read_bytes()


def load_market() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Dates (yyyymmdd), total market return and risk-free return, daily, in decimals.
    raw = _fetch(FRENCH, "F-F_Research_Data_Factors_daily_CSV.zip")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        text = z.read(z.namelist()[0]).decode("latin-1")
    dates, mkt, rf, started = [], [], [], False
    for line in text.splitlines():
        cells = [c.strip() for c in line.split(",")]
        if not started:
            started = len(cells) > 1 and cells[0] == "" and cells[1] == "Mkt-RF"
            continue
        if not cells[0].isdigit() or len(cells[0]) != 8 or int(cells[0]) > END:
            break
        dates.append(int(cells[0]))
        mkt.append(float(cells[1]) / 100)
        rf.append(float(cells[4]) / 100)
    rf_a = np.array(rf)
    return np.array(dates), np.array(mkt) + rf_a, rf_a


def load_cboe(symbol: str) -> dict[int, float]:
    text = _fetch(CBOE.format(symbol), f"cboe_{symbol}.csv").decode()
    out = {}
    for line in text.splitlines()[1:]:
        cells = line.split(",")
        m, d, y = (int(x) for x in cells[0].split("/"))
        key = y * 10000 + m * 100 + d
        if key <= END:
            out[key] = float(cells[-1])
    return out


def load_fred(series: str) -> dict[int, float]:
    text = _fetch(FRED.format(series), f"fred_{series}.csv").decode()
    out = {}
    for line in text.splitlines()[1:]:
        day, value = line.split(",")
        key = int(day.replace("-", ""))
        if key <= END and value not in (".", ""):
            out[key] = float(value)
    return out


def asof(dates: np.ndarray, series: dict[int, float], lag: int = 0, stale_days: int = 10) -> np.ndarray:
    # The last value on or before each date, shifted by `lag` rows for publication
    # delay.
    keys = np.array(sorted(series))
    vals = np.array([series[k] for k in keys])
    idx = np.searchsorted(keys, dates, side="right") - 1
    out = np.where(idx >= 0, vals[np.clip(idx, 0, None)], np.nan)
    gap = _days(dates) - _days(keys[np.clip(idx, 0, None)])
    out[(idx < 0) | (gap > stale_days)] = np.nan
    if lag:
        out = np.concatenate([np.full(lag, np.nan), out[:-lag]])
    return out


def _days(d: np.ndarray) -> np.ndarray:
    d = np.asarray(d)
    return np.array(
        [np.datetime64(f"{x // 10000:04d}-{x // 100 % 100:02d}-{x % 100:02d}") for x in d], dtype="datetime64[D]"
    ).astype(np.int64)


def to_datetime64(d: np.ndarray) -> np.ndarray:
    return np.array([np.datetime64(f"{x // 10000:04d}-{x // 100 % 100:02d}-{x % 100:02d}") for x in d])


# ---------------------------------------------------------------------------
# Labels


def lt_turning_points(P: np.ndarray, down: float = 0.20, up: float = 0.20) -> tuple[list, int, int]:
    # Peaks and troughs by the threshold rule: a bear market is confirmed when the price
    # falls `down` below its running peak, a bull market when it rises `up` above its
    # running trough. Returns (extreme, kind, confirmed) triples with kind +1 for a peak
    # and -1 for a trough, plus the final phase and running extreme.
    tps = []
    phase, ext = 1, 0
    for t in range(1, len(P)):
        if phase == 1:
            if P[t] >= P[ext]:
                ext = t
            elif P[t] <= P[ext] * (1 - down):
                tps.append((ext, 1, t))
                phase, ext = -1, ext + int(np.argmin(P[ext : t + 1]))
        elif P[t] <= P[ext]:
            ext = t
        elif P[t] >= P[ext] * (1 + up):
            tps.append((ext, -1, t))
            phase, ext = 1, ext + int(np.argmax(P[ext : t + 1]))
    return tps, phase, ext


def lt_labels(P: np.ndarray, down: float = 0.20, up: float = 0.20) -> dict:
    # Ex-post bear label (1 on days after a peak through the next trough), the real-time
    # confirmed state, the mask of days whose label is final at the end of the sample,
    # and the turning points.
    tps, phase, ext = lt_turning_points(P, down, up)
    T = len(P)
    y = np.zeros(T, dtype=int)
    rt = np.zeros(T, dtype=int)
    for i, (e, kind, c) in enumerate(tps):
        end = tps[i + 1][0] if i + 1 < len(tps) else T - 1
        if kind == 1:
            y[e + 1 : end + 1] = 1
        rt[c:] = 1 if kind == 1 else 0
    known = np.ones(T, dtype=bool)
    known[ext + 1 :] = False
    return {"y": y, "rt": rt, "known": known, "tps": tps}


def known_through(P: np.ndarray, t_end: int, down: float = 0.20, up: float = 0.20) -> int:
    # Index of the last day whose bear/bull label is final using prices up to t_end.
    _, _, ext = lt_turning_points(P[: t_end + 1], down, up)
    return ext


def realised_vol(logret: np.ndarray, n: int) -> np.ndarray:
    # Trailing n-day realised volatility, annualised, known at the close of day t.
    c = np.concatenate([[0.0], np.cumsum(logret**2)])
    out = np.full(len(logret), np.nan)
    out[n - 1 :] = np.sqrt(A * (c[n:] - c[:-n]) / n)
    return out


def forward_vol(logret: np.ndarray, h: int) -> np.ndarray:
    # Realised volatility over days t+1..t+h, annualised (NaN where incomplete).
    rv = realised_vol(logret, h)
    out = np.full(len(logret), np.nan)
    out[:-h] = rv[h:]
    return out


def expanding_quantile(x: np.ndarray, q: float, min_n: int) -> np.ndarray:
    # The q-quantile of x[:t+1] for each t (NaN until min_n finite values).
    seen: list[float] = []
    out = np.full(len(x), np.nan)
    for t, v in enumerate(x):
        if np.isfinite(v):
            bisect.insort(seen, v)
        if len(seen) >= min_n:
            out[t] = seen[int(q * (len(seen) - 1))]
    return out


def forward_drawdown(P: np.ndarray, h: int) -> np.ndarray:
    # Largest peak-to-trough fall inside days t..t+h, measured from P[t] and later
    # peaks.
    from numpy.lib.stride_tricks import sliding_window_view

    W = sliding_window_view(P, h + 1)
    dd = (1 - W / np.maximum.accumulate(W, axis=1)).max(axis=1)
    out = np.full(len(P), np.nan)
    out[: len(dd)] = dd
    return out


def forward_return(P: np.ndarray, h: int) -> np.ndarray:
    out = np.full(len(P), np.nan)
    out[:-h] = P[h:] / P[:-h] - 1
    return out


def ewm(x: np.ndarray, halflife: float) -> np.ndarray:
    a = 1 - 0.5 ** (1 / halflife)
    out = np.empty_like(x)
    m = x[0]
    for t, v in enumerate(x):
        m = a * v + (1 - a) * m
        out[t] = m
    return out


def jump_features(r: np.ndarray) -> np.ndarray:
    # Causal features for the jump model: exponentially weighted mean return and log
    # downside deviation at two half-lives.
    cols = []
    for hl in (10, 42):
        cols.append(ewm(r, hl) * A)
        cols.append(0.5 * np.log(ewm(np.minimum(r, 0.0) ** 2, hl) * A + 1e-12))
    return np.column_stack(cols)


def _dp2(d0: list, d1: list, lam: float) -> np.ndarray:
    T = len(d0)
    v0, v1 = d0[0], d1[0]
    b0, b1 = bytearray(T), bytearray(T)
    for t in range(1, T):
        if v0 <= v1 + lam:
            n0 = v0
        else:
            n0, b0[t] = v1 + lam, 1
        if v1 <= v0 + lam:
            n1, b1[t] = v1, 1
        else:
            n1 = v0 + lam
        v0, v1 = n0 + d0[t], n1 + d1[t]
    s = np.empty(T, dtype=int)
    s[-1] = 0 if v0 <= v1 else 1
    for t in range(T - 1, 0, -1):
        s[t - 1] = b0[t] if s[t] == 0 else b1[t]
    return s


def jump_model(X: np.ndarray, lam: float, rng: np.random.Generator, starts: int = 6, iters: int = 30) -> np.ndarray:
    # Two-state statistical jump model (Bemporad et al., 2018; Nystrup et al., 2020):
    # alternate an exact dynamic-programming state assignment, which charges `lam` per
    # switch, with centroid updates. Returns the state path; state 1 is the one with the
    # lower mean return in the first feature.
    mu_x, sd_x = X.mean(0), X.std(0)
    Z = (X - mu_x) / sd_x
    best, best_obj = None, np.inf
    for _ in range(starts):
        mu = Z[rng.choice(len(Z), 2, replace=False)]
        s_old = None
        for _ in range(iters):
            D = ((Z[:, None, :] - mu[None, :, :]) ** 2).sum(-1)
            s = _dp2(D[:, 0].tolist(), D[:, 1].tolist(), lam)
            if s_old is not None and np.array_equal(s, s_old):
                break
            s_old = s
            for k in range(2):
                if (s == k).any():
                    mu[k] = Z[s == k].mean(0)
        obj = D[np.arange(len(Z)), s].sum() + lam * np.count_nonzero(np.diff(s))
        if obj < best_obj:
            best, best_obj = s.copy(), obj
    if X[best == 1, 0].mean() > X[best == 0, 0].mean():
        best = 1 - best
    return best


def nber_daily(dates: np.ndarray) -> np.ndarray:
    rec = load_fred("USREC")
    months = dates // 100
    return np.array([int(rec.get(m * 100 + 1, 0.0)) for m in months])


# ---------------------------------------------------------------------------
# Scores


def runs(y: np.ndarray) -> list[tuple[int, int]]:
    # (start, end-inclusive) of each run of ones.
    e = np.flatnonzero(np.diff(np.concatenate([[0], y.astype(int), [0]])))
    return list(zip(e[::2], e[1::2] - 1, strict=True))


def kappa(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a.astype(int), b.astype(int)
    po = np.mean(a == b)
    pa, pb = a.mean(), b.mean()
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe)


def auc(y: np.ndarray, p: np.ndarray) -> float:
    order = np.argsort(p, kind="mergesort")
    ranks = np.empty(len(p))
    ps = p[order]
    i = 0
    while i < len(ps):  # average ranks over ties
        j = i
        while j + 1 < len(ps) and ps[j + 1] == ps[i]:
            j += 1
        ranks[order[i : j + 1]] = 0.5 * (i + j) + 1
        i = j + 1
    n1 = y.sum()
    n0 = len(y) - n1
    return (ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n0 * n1)


def brier(y: np.ndarray, p: np.ndarray) -> float:
    return float(np.mean((p - y) ** 2))


# ---------------------------------------------------------------------------
# Logistic regression with a ridge penalty, by Newton's method


def fit_logit(X: np.ndarray, y: np.ndarray, alpha: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1.0
    Z = np.column_stack([np.ones(len(X)), (X - mu) / sd])
    beta = np.zeros(Z.shape[1])
    pen = np.full(Z.shape[1], alpha)
    pen[0] = 0.0
    for _ in range(50):
        p = 1 / (1 + np.exp(-np.clip(Z @ beta, -30, 30)))
        g = Z.T @ (p - y) + pen * beta
        H = (Z * (p * (1 - p))[:, None]).T @ Z + np.diag(pen)
        step = np.linalg.solve(H, g)
        beta -= step
        if np.max(np.abs(step)) < 1e-9:
            break
    return beta, mu, sd


def predict_logit(model: tuple, X: np.ndarray) -> np.ndarray:
    beta, mu, sd = model
    Z = np.column_stack([np.ones(len(X)), (X - mu) / sd])
    return 1 / (1 + np.exp(-np.clip(Z @ beta, -30, 30)))


# ---------------------------------------------------------------------------
# The worked examples


_CACHE: dict = {}


def market() -> dict:
    if "market" not in _CACHE:
        dates, r, rf = load_market()
        P = np.cumprod(1 + r)
        _CACHE["market"] = {"dates": dates, "r": r, "rf": rf, "P": P, "lr": np.log1p(r), "years": dates // 10000}
    return _CACHE["market"]


def labels() -> dict:
    # Every label of the century comparison, as float arrays (NaN = undefined).
    if "labels" in _CACHE:
        return _CACHE["labels"]
    m = market()
    P, lr, r = m["P"], m["lr"], m["r"]
    lt20 = lt_labels(P, 0.20, 0.20)
    lt15 = lt_labels(P, 0.15, 0.15)
    rv21 = realised_vol(lr, 21)
    thr = expanding_quantile(rv21, VOL_Q, MIN_HISTORY)
    fv = forward_vol(lr, H_VOL)
    fdd = forward_drawdown(P, H_RISK)
    fret = forward_return(P, H_RISK)
    s0 = np.searchsorted(m["dates"], 19270101)
    jm = np.full(len(P), np.nan)
    jm[s0:] = jump_model(jump_features(r)[s0:], JM_LAMBDA, np.random.default_rng(SEED))
    out = {
        "Bear, ±20% rule, ex post": np.where(lt20["known"], lt20["y"], np.nan),
        "Bear, ±20% rule, as confirmed": lt20["rt"].astype(float),
        "Bear, ±15% rule, ex post": np.where(lt15["known"], lt15["y"], np.nan),
        "10% below the high, now": (1 - P / np.maximum.accumulate(P) >= 0.10).astype(float),
        "Next-month volatility, top fifth": np.where(
            np.isfinite(fv) & np.isfinite(thr), (fv >= thr).astype(float), np.nan
        ),
        "10% drawdown in next quarter": np.where(np.isfinite(fdd), (fdd >= DD_LEVEL).astype(float), np.nan),
        "Negative next-quarter return": np.where(np.isfinite(fret), (fret < 0).astype(float), np.nan),
        "Jump model, high-risk state": jm,
        "NBER recession": nber_daily(m["dates"]).astype(float),
    }
    _CACHE["labels"] = out
    _CACHE["lt20"], _CACHE["lt15"], _CACHE["rv21"], _CACHE["thr"] = lt20, lt15, rv21, thr
    return out


def label_summary() -> None:
    m, labs = market(), labels()
    dates = m["dates"]
    valid = np.ones(len(dates), dtype=bool)
    for y in labs.values():
        valid &= np.isfinite(y)
    print(f"\nLabel comparison, {dates[valid][0]} to {dates[valid][-1]} ({valid.sum()} days)")
    print(f"  {'label':34s} {'share':>6s} {'episodes':>9s} {'median days':>12s}")
    for k, y in labs.items():
        yy = y[valid].astype(int)
        durs = [b - a + 1 for a, b in runs(yy)]
        print(f"  {k:34s} {yy.mean():6.2f} {len(durs):9d} {np.median(durs):12.0f}")
    names = list(labs)
    print("\n  Cohen's kappa between labels (same days)")
    for i, a in enumerate(names):
        cells = " ".join(f"{kappa(labs[a][valid], labs[b][valid]):5.2f}" for b in names[: i + 1])
        print(f"  {i + 1:2d} {cells}")


def lt_summary() -> None:
    m = market()
    dates, P, r, rf = m["dates"], m["P"], m["r"], m["rf"]
    labels()
    s = np.searchsorted(dates, 19270101)
    for name in ("lt20", "lt15"):
        lt = _CACHE[name]
        tps = lt["tps"]
        bear = [c - e for e, k, c in tps if k == 1]
        bull = [c - e for e, k, c in tps if k == -1]
        y, rt, known = lt["y"], lt["rt"], lt["known"]
        mask = np.zeros(len(P), dtype=bool)
        mask[s:] = True
        mask &= known
        print(f"\n{name}: {len(bear)} bear and {len(bull)} bull confirmations since 1926")
        print(
            f"  bear confirmation lag, trading days: median {np.median(bear):.0f}, IQR {np.percentile(bear, 25):.0f}-{np.percentile(bear, 75):.0f}"
        )
        print(
            f"  bull confirmation lag, trading days: median {np.median(bull):.0f}, IQR {np.percentile(bull, 25):.0f}-{np.percentile(bull, 75):.0f}"
        )
        print(
            f"  share of days where the confirmed state differs from the ex-post label: {np.mean(rt[mask] != y[mask]):.3f}"
        )
        print(f"  kappa(confirmed, ex post): {kappa(rt[mask], y[mask]):.2f}")
        print(
            f"  ex-post bear but confirmed bull: {np.mean((y[mask] == 1) & (rt[mask] == 0)):.3f};"
            f" ex-post bull but confirmed bear: {np.mean((y[mask] == 0) & (rt[mask] == 1)):.3f}"
        )
        for label, pos in (
            ("buy and hold", np.ones(len(P))),
            ("timed by the ex-post label", 1.0 - y),
            ("timed by the confirmed state", np.concatenate([[1.0], 1.0 - rt[:-1]])),
        ):
            ret = (pos * r + (1 - pos) * rf)[s:]
            ex = ret - rf[s:]
            w = np.cumprod(1 + ret)
            yrs = len(ret) / A
            print(
                f"  {label:30s} CAGR {w[-1] ** (1 / yrs) - 1:6.1%}  Sharpe {ex.mean() / ex.std() * math.sqrt(A):5.2f}"
                f"  max drawdown {(1 - w / np.maximum.accumulate(w)).max():5.1%}"
            )
    for e, k, c in _CACHE["lt20"]["tps"]:
        if k == 1 and dates[e] >= 20000101:
            print(f"  ±20% bear: peak {dates[e]}, confirmed {dates[c]} ({c - e} trading days, {P[c] / P[e] - 1:+.1%})")


def jm_summary() -> None:
    m, labs = market(), labels()
    s0 = np.searchsorted(m["dates"], 19270101)
    X = jump_features(m["r"])[s0:]
    full = labs["Jump model, high-risk state"][s0:].astype(int)
    Z = (X - X.mean(0)) / X.std(0)
    cent = np.array([Z[full == k].mean(0) for k in (0, 1)])
    D = ((Z[:, None, :] - cent[None]) ** 2).sum(-1)
    V = D[0].copy()
    online = np.empty(len(Z), dtype=int)
    online[0] = V.argmin()
    for t in range(1, len(Z)):
        V = D[t] + np.array([min(V[0], V[1] + JM_LAMBDA), min(V[1], V[0] + JM_LAMBDA)])
        online[t] = V.argmin()
    lags = []
    for a, b in runs(full):
        hit = np.flatnonzero(online[a : b + 1] == 1)
        lags.append(hit[0] if len(hit) else b - a + 1)
    print(
        f"\nJump model (lambda {JM_LAMBDA:g}): {len(runs(full))} high-risk episodes in the two-sided fit, {len(runs(online))} in the forward-only path"
    )
    print(f"  kappa(forward-only, two-sided) {kappa(online, full):.2f}; days that differ {np.mean(online != full):.3f}")
    print(
        f"  entry into the high-risk state recognised after a median {np.median(lags):.0f} trading days (IQR {np.percentile(lags, 25):.0f}-{np.percentile(lags, 75):.0f})"
    )
    for lam in (10.0, 40.0, 100.0):
        s = jump_model(X, lam, np.random.default_rng(SEED))
        durs = [b - a + 1 for a, b in runs(s)]
        print(
            f"  lambda {lam:5g}: {len(durs)} high-risk episodes, median {np.median(durs):.0f} days, {s.mean():.0%} of days"
        )


def features() -> dict:
    if "features" in _CACHE:
        return _CACHE["features"]
    m = market()
    dates, P, lr = m["dates"], m["P"], m["lr"]
    T = len(P)
    vix = asof(dates, load_cboe("VIX"))
    vix3m = asof(dates, load_cboe("VIX3M"))
    baa = asof(dates, load_fred("BAA10Y"), lag=1)
    curve = asof(dates, load_fred("T10Y3M"), lag=1)
    rv5, rv21, rv63 = (realised_vol(lr, n) for n in (5, 21, 63))
    logp = np.log(P)
    hi252 = np.array([P[max(0, t - 251) : t + 1].max() for t in range(T)])
    c = np.concatenate([[0.0], np.cumsum(P)])
    ma200 = np.full(T, np.nan)
    ma200[199:] = (c[200:] - c[:-200]) / 200

    def lagdiff(x: np.ndarray, n: int) -> np.ndarray:
        return np.concatenate([np.full(n, np.nan), x[n:] - x[:-n]])

    price = np.column_stack(
        [
            np.log(rv5 + 1e-4),
            np.log(rv21),
            np.log(rv63),
            1 - P / hi252,
            lagdiff(logp, 252),
            lagdiff(logp, 21),
            np.log(P / ma200),
        ]
    )
    cross = np.column_stack([np.log(vix), np.log(vix / 100) - np.log(rv21), baa, lagdiff(baa, 21), curve])
    _CACHE["features"] = {
        "vol-only": np.log(rv21)[:, None],
        "VIX-only": np.log(vix)[:, None],
        "price": price,
        "price + cross-asset": np.column_stack([price, cross]),
        "term": np.log(vix / vix3m)[:, None],
    }
    return _CACHE["features"]


def targets() -> dict:
    labs = labels()
    return {
        "Next-month volatility, top fifth": (labs["Next-month volatility, top fifth"], H_VOL),
        "10% drawdown in next quarter": (labs["10% drawdown in next quarter"], H_RISK),
        "Negative next-quarter return": (labs["Negative next-quarter return"], H_RISK),
        "Bear, ±20% rule, ex post": (labs["Bear, ±20% rule, ex post"], None),
    }


ALPHA = 0.1  # ridge penalty per training observation


def _train_index(y: np.ndarray, reach: int | None, tau: int, s0: int) -> np.ndarray:
    # Training rows whose label is final before the first day of the test year.
    if reach is None:
        last = min(known_through(market()["P"], tau - 1), tau - 1)
        tr = np.arange(s0, last + 1)
    else:
        tr = np.arange(s0, tau - reach)
    return tr[np.isfinite(y[tr])]


def walk_forward(
    F: np.ndarray | None, y: np.ndarray, reach: int | None, first: int = 2000, since: int = 19900102
) -> np.ndarray:
    # Refit at the start of each year on every row whose label was final by then;
    # predict that year. F None gives the climatology (the training base rate).
    m = market()
    dates, years = m["dates"], m["years"]
    p = np.full(len(dates), np.nan)
    s0 = np.searchsorted(dates, since)
    for Y in range(first, END // 10000 + 1):
        tau = np.searchsorted(dates, Y * 10000 + 101)
        tr = _train_index(y, reach, tau, s0)
        te = np.flatnonzero(years == Y)
        if F is None:
            p[te] = y[tr].mean()
            continue
        tr = tr[np.all(np.isfinite(F[tr]), axis=1)]
        te = te[np.all(np.isfinite(F[te]), axis=1)]
        p[te] = predict_logit(fit_logit(F[tr], y[tr], alpha=ALPHA * len(tr)), F[te])
    return p


def block_bootstrap(
    y: np.ndarray, pa: np.ndarray, pb: np.ndarray, pc: np.ndarray, mask: np.ndarray, B: int = 1000
) -> tuple:
    # 90% intervals for AUC(b) - AUC(a) and for the Brier-skill gain of b over a,
    # resampling one-year blocks of the test period.
    idx = np.flatnonzero(mask & np.isfinite(y) & np.isfinite(pa) & np.isfinite(pb))
    n, block = len(idx), A
    rng = np.random.default_rng(SEED)
    da, db = [], []
    for _ in range(B):
        st = rng.integers(0, n - block, size=n // block + 1)
        s = np.concatenate([idx[i : i + block] for i in st])[:n]
        yy = y[s].astype(int)
        if yy.min() == yy.max():
            continue
        da.append(auc(yy, pb[s]) - auc(yy, pa[s]))
        db.append((brier(y[s], pa[s]) - brier(y[s], pb[s])) / brier(y[s], pc[s]))
    return np.percentile(da, [5, 95]), np.percentile(db, [5, 95])


def classifier_results() -> dict:
    if "clf" in _CACHE:
        return _CACHE["clf"]
    F = features()
    out = {}
    for name, (y, reach) in targets().items():
        preds = {"climatology": walk_forward(None, y, reach)}
        for fname in ("vol-only", "VIX-only", "price", "price + cross-asset"):
            preds[fname] = walk_forward(F[fname], y, reach)
        out[name] = (y, reach, preds)
    _CACHE["clf"] = out
    return out


def classifier_summary() -> None:
    m, F = market(), features()
    years, dates, P = m["years"], m["dates"], m["P"]
    res = classifier_results()
    test = (years >= 2000) & (years <= END // 10000)
    print("\nWalk-forward classifiers, test 2000-2025 (AUC / Brier skill vs climatology)")
    for name, (y, _reach, preds) in res.items():
        mm = test & np.isfinite(y)
        pc = preds["climatology"]
        cells = []
        for k, p in preds.items():
            if k == "climatology":
                continue
            ok = mm & np.isfinite(p)
            cells.append(
                f"{k} {auc(y[ok].astype(int), p[ok]):.2f}/{1 - brier(y[ok], p[ok]) / brier(y[ok], pc[ok]):+.2f}"
            )
        print(f"  {name:32s} base {np.mean(y[mm]):.2f} | " + " | ".join(cells))
        for a, b in (("vol-only", "price + cross-asset"), ("price", "price + cross-asset")):
            ca, cb = block_bootstrap(y, preds[a], preds[b], pc, mm)
            print(f"      {b} minus {a}: dAUC [{ca[0]:+.3f}, {ca[1]:+.3f}], dBSS [{cb[0]:+.3f}, {cb[1]:+.3f}]")
    global ALPHA
    print("\nShrinkage, 10% drawdown label, test 2000-2025: ridge penalty per training row")
    y, reach, preds = res["10% drawdown in next quarter"]
    mm = test & np.isfinite(y)
    keep = ALPHA
    for alpha in (0.001, 0.1):
        ALPHA = alpha
        cells = []
        for key in ("vol-only", "price + cross-asset"):
            p = walk_forward(F[key], y, reach)
            ok = mm & np.isfinite(p)
            cells.append(f"{key} AUC {auc(y[ok].astype(int), p[ok]):.2f}")
        print(f"  alpha {alpha:g}: " + " | ".join(cells))
    ALPHA = keep
    print("\nAdding VIX/VIX3M, test 2015-2025 (both trained from 2009-09-18) vs the 1990-trained model")
    test2 = (years >= 2015) & (years <= END // 10000)
    base = F["price + cross-asset"]
    for name, (y, reach, preds) in res.items():
        if name == "Negative next-quarter return":
            continue
        mm = test2 & np.isfinite(y)
        pc = walk_forward(None, y, reach, first=2015, since=20090918)
        cells = []
        for label, p in (
            ("from 2009", walk_forward(base, y, reach, first=2015, since=20090918)),
            (
                "from 2009 + term",
                walk_forward(np.column_stack([base, F["term"]]), y, reach, first=2015, since=20090918),
            ),
            ("from 1990", preds["price + cross-asset"]),
        ):
            ok = mm & np.isfinite(p)
            cells.append(
                f"{label} {auc(y[ok].astype(int), p[ok]):.2f}/{1 - brier(y[ok], p[ok]) / brier(y[ok], pc[ok]):+.2f}"
            )
        print(f"  {name:32s} " + " | ".join(cells))
    y, _, preds = res["Bear, ±20% rule, ex post"]
    lt = lt_labels(P)
    print("\nBear-market onsets since 2000: trading days from the peak until the rule confirms / P >= 0.5")
    for e, k, c in lt["tps"]:
        if k != 1 or dates[e] < 20000101:
            continue
        end = next((tp[0] for tp in lt["tps"] if tp[0] > e), len(P) - 1)
        cells = []
        for key in ("price", "price + cross-asset"):
            hit = np.flatnonzero(preds[key][e + 1 : end + 1] >= 0.5)
            cells.append(f"{key} {hit[0] + 1 if len(hit) else '-'}")
        print(f"  peak {dates[e]} (bear lasts {end - e:3d} days): rule {c - e:3d} | " + " | ".join(cells))
    rt = lt["rt"].astype(float)
    ok = test & np.isfinite(y)
    print(
        f"  confirmed state: AUC {auc(y[ok].astype(int), rt[ok]):.2f}; on for {np.mean(rt[ok & (y == 1)] == 1):.0%} of ex-post"
        f" bear days and {np.mean(rt[ok & (y == 0)] == 1):.0%} of bull days"
    )
    for key in ("price", "price + cross-asset"):
        p = preds[key]
        ok = test & np.isfinite(y) & np.isfinite(p)
        on = ok & (p >= 0.5)
        fa = [rr for rr in runs((on & (y == 0)).astype(int)) if rr[1] - rr[0] + 1 >= 5]
        print(
            f"  {key}: P >= 0.5 on {np.mean(on[ok & (y == 1)]):.0%} of ex-post bear days and {np.mean(on[ok & (y == 0)]):.0%}"
            f" of bull days; {len(fa)} false alarms of five days or more"
        )


def input_summary() -> None:
    # The input statistics quoted in sections 1.4, 2.3, 2.11, 3.3, 3.5 and 3.13.
    m = market()
    dates, P, lr = m["dates"], m["P"], m["lr"]
    years = m["years"]
    vix = asof(dates, load_cboe("VIX"))
    vix3m = asof(dates, load_cboe("VIX3M"))
    baa = asof(dates, load_fred("BAA10Y"))
    curve = asof(dates, load_fred("T10Y3M"))
    nber = nber_daily(dates)
    s = np.searchsorted(dates, 19900102)
    v = vix[s:]
    print("\nInputs")
    print(
        f"  VIX 1990-2025: median {np.median(v):.1f}; below 15 on {np.mean(v < 15):.1%}, above 30 on"
        f" {np.mean(v > 30):.1%}, above 40 on {np.mean(v > 40):.1%} of days;"
        f" mean {np.nanmean(vix[years == 2002]):.1f} in 2002 and {np.nanmean(vix[years == 2017]):.1f} in 2017"
    )
    lv = np.log(v)
    rho = np.polyfit(lv[:-1], lv[1:], 1)[0]
    print(f"  log VIX daily AR(1) {rho:.4f}, half-life {np.log(0.5) / np.log(rho):.0f} trading days")
    k = np.searchsorted(dates, 19300101)
    x = np.log(realised_vol(lr, 21)[k:])
    x = x[np.isfinite(x)]
    b21 = np.polyfit(x[:-21], x[21:], 1)[0]
    print(
        f"  log 21-day realised vol on its value 21 days earlier, 1930-2025: slope {b21:.2f}, half-life {np.log(0.5) / np.log(b21):.1f} months"
    )
    t0 = np.searchsorted(dates, 20090918)
    inv = (vix > vix3m)[t0:]
    print(f"  VIX above VIX3M on {inv.mean():.1%} of days since 2009-09-18, in {len(runs(inv.astype(int)))} spells")
    neg = (curve < 0) & (dates >= 20220101)
    spells = [(a, b) for a, b in runs(neg.astype(int)) if b - a + 1 > 20]
    for a, b in spells:
        print(f"  10y-3m inverted {dates[a]} to {dates[b]}")
    hi252 = np.array([P[max(0, t - 251) : t + 1].max() for t in range(len(P))])
    rv21 = realised_vol(lr, 21)
    c = np.concatenate([[0.0], np.cumsum(P)])
    ma200 = np.full(len(P), np.nan)
    ma200[199:] = (c[200:] - c[:-200]) / 200
    cols = {
        "log VIX": np.log(vix),
        "log RV21": np.log(rv21),
        "log VIX/VIX3M": np.log(vix / vix3m),
        "Baa spread": asof(dates, load_fred("BAA10Y"), lag=1),
        "10y-3m": asof(dates, load_fred("T10Y3M"), lag=1),
        "drawdown": 1 - P / hi252,
        "trend": np.log(P / ma200),
    }
    X = np.column_stack(list(cols.values()))[t0:]
    X = X[np.all(np.isfinite(X), axis=1)]
    C = np.corrcoef(((X - X.mean(0)) / X.std(0)).T)
    w = np.linalg.eigvalsh(C)[::-1]
    print(f"  seven inputs, 2009-09 to 2025: principal-component shares {np.round(w[:3] / w.sum(), 2)}")
    for i, name in enumerate(cols):
        print(f"    {name:14s} " + " ".join(f"{C[i, j]:5.2f}" for j in range(i + 1)))
    names6 = ["log VIX", "log RV21", "Baa spread", "10y-3m", "drawdown", "trend"]
    X6 = np.column_stack([cols[n] for n in names6])[s:]
    X6 = X6[np.all(np.isfinite(X6), axis=1)]
    w6 = np.linalg.eigvalsh(np.corrcoef(((X6 - X6.mean(0)) / X6.std(0)).T))[::-1]
    print(f"  six inputs, 1990-2025: principal-component shares {np.round(w6[:2] / w6.sum(), 2)}")
    print("  episodes: largest drawdown in the window, VIX mean and high, Baa spread start and high, NBER share")
    for a, b in (
        (19870801, 19871231),
        (20070101, 20070630),
        (20070701, 20071231),
        (20180901, 20181231),
        (20200201, 20200430),
        (20220101, 20221031),
        (20250201, 20250430),
    ):
        i, j = np.searchsorted(dates, a), np.searchsorted(dates, b, side="right")
        seg = P[i:j]
        dd = (1 - seg / np.maximum.accumulate(seg)).max()
        vv = vix[i:j]
        vtxt = f"{np.nanmean(vv):5.1f} {np.nanmax(vv):5.1f}" if np.isfinite(vv).any() else "    -     -"
        print(
            f"    {a}-{b}: {dd:6.1%}  VIX {vtxt}  Baa {baa[i]:.2f} -> {np.nanmax(baa[i:j]):.2f}  NBER {nber[i:j].mean():.2f}"
        )


def main() -> None:
    try:
        features()
    except OSError as e:
        print(f"offline ({e}); no numbers printed")
        return
    m = market()
    print(f"Market data {m['dates'][0]} to {m['dates'][-1]}, {len(m['dates'])} days")
    label_summary()
    input_summary()
    lt_summary()
    jm_summary()
    classifier_summary()


def load_or_exit(out: Path) -> None:
    # Download (or read the cached) data, or leave committed figures in place when
    # offline.
    try:
        labels()
        features()
    except OSError as e:
        if out.with_suffix(".svg").exists():
            print(f"offline ({e}); leaving the committed {out.stem} outputs in place")
            raise SystemExit(0) from None
        raise SystemExit(f"cannot download the data: {e}") from None


if __name__ == "__main__":
    main()

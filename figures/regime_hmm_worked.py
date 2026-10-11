# A hidden Markov model fitted to a century of US daily equity returns, the way
# it would have been fitted in real time: expanding-window refits once a year,
# states identified by volatility inside each fit, and only the predicted state
# probability xi(t|t-1) used for anything. Prints every number quoted in the
# worked example of market_regimes.md and draws the figure.
#
# Data are the daily value-weighted US market return from the Kenneth French
# data library, downloaded (and cached in the system temp directory) rather than
# committed, and pinned to end in December 2025 so the printed tables are stable.
#
# The forward and backward recursions are computed as prefix products of K x K
# matrices with a log-depth scan, which keeps a numpy-only EM fast enough to
# refit two models eighty times over 26,000 days (a few minutes in total).
#
# Run standalone:  uv run --no-project --with matplotlib python <path>

import io
import math
import os
import tempfile
import urllib.request
import zipfile

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "regime-hmm-worked"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"
FAINT = "#DCE4E6"

A = 252
BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
FILE = "F-F_Research_Data_Factors_daily_CSV.zip"
END = 20251231
CACHE = Path(tempfile.gettempdir()) / "quant_research_french"
FIRST_OOS_YEAR = 1946
SEED = 20261010
NU_GRID = np.exp(np.linspace(np.log(2.2), np.log(60.0), 48))
SIGMA_FLOOR = 1e-4
EWMA_LAMBDA = 0.94
TARGET_VOL = 0.15 / math.sqrt(A)
MAX_LEVERAGE = 2.0


def load() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Dates, total market return, and market excess return, daily, in decimals."""
    CACHE.mkdir(exist_ok=True)
    path = CACHE / FILE
    if not path.exists():
        with urllib.request.urlopen(BASE + FILE, timeout=60) as r:
            path.write_bytes(r.read())
    with zipfile.ZipFile(path) as z:
        text = z.read(z.namelist()[0]).decode("latin-1")
    dates, mkt, rf, started = [], [], [], False
    for line in io.StringIO(text).read().splitlines():
        cells = [c.strip() for c in line.split(",")]
        if not started:
            started = len(cells) > 1 and cells[0] == "" and cells[1] == "Mkt-RF"
            continue
        if not cells[0].isdigit() or len(cells[0]) != 8 or int(cells[0]) > END:
            break
        dates.append(int(cells[0]))
        mkt.append(float(cells[1]) / 100)
        rf.append(float(cells[4]) / 100)
    excess = np.array(mkt)
    total = excess + np.array(rf)
    return np.array(dates), total, excess


# ---------------------------------------------------------------------------
# Emissions


LGAMMA = np.frompyfunc(math.lgamma, 1, 1)


def t_const(nu: np.ndarray) -> np.ndarray:
    nu = np.asarray(nu, dtype=float)
    lg = np.asarray(LGAMMA((nu + 1) / 2), dtype=float) - np.asarray(LGAMMA(nu / 2), dtype=float)
    return lg - 0.5 * np.log(nu * np.pi)


def log_emission(r: np.ndarray, mu: np.ndarray, sig: np.ndarray, nu: np.ndarray | None) -> np.ndarray:
    z = (r[:, None] - mu[None, :]) / sig[None, :]
    if nu is None:
        return -0.5 * z * z - np.log(sig)[None, :] - 0.5 * math.log(2 * math.pi)
    return t_const(nu)[None, :] - np.log(sig)[None, :] - 0.5 * (nu[None, :] + 1) * np.log1p(z * z / nu[None, :])


# ---------------------------------------------------------------------------
# Forward-backward by prefix products


def scan(M: np.ndarray) -> np.ndarray:
    """R[t] = M[t] @ M[t-1] @ ... @ M[0], each rescaled to a maximum entry of one."""
    R = M / M.max(axis=(1, 2), keepdims=True)
    d = 1
    while d < len(R):
        new = R.copy()
        new[d:] = R[d:] @ R[:-d]
        new[d:] /= new[d:].max(axis=(1, 2), keepdims=True)
        R = new
        d *= 2
    return R


def forward(logB: np.ndarray, P: np.ndarray, delta: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Filtered xi(t|t), predicted xi(t|t-1), and the log-likelihood."""
    m = logB.max(axis=1, keepdims=True)
    B = np.exp(logB - m)
    M = B[:, :, None] * P.T[None, :, :]
    M[0] = np.diag(B[0])
    alpha = scan(M) @ delta
    alpha /= alpha.sum(axis=1, keepdims=True)
    pred = np.vstack([delta, alpha[:-1] @ P])
    c = (pred * B).sum(axis=1)
    return alpha, pred, float(np.sum(np.log(c) + m[:, 0]))


def backward(logB: np.ndarray, P: np.ndarray) -> np.ndarray:
    B = np.exp(logB - logB.max(axis=1, keepdims=True))
    N = P[None, :, :] * B[1:, None, :]
    beta = (scan(N[::-1]) @ np.ones(len(P)))[::-1]
    beta = np.vstack([beta, np.ones(len(P))])
    return beta / beta.sum(axis=1, keepdims=True)


# ---------------------------------------------------------------------------
# EM


def init_params(r: np.ndarray, K: int, student: bool, rng: np.random.Generator) -> dict:
    q = np.quantile(np.abs(r - r.mean()), np.linspace(0.25, 0.85, K)) * 1.25
    return {
        "mu": rng.normal(r.mean(), r.std() * 0.05, K),
        "sig": np.sort(np.maximum(q * (1 + 0.15 * rng.standard_normal(K)), SIGMA_FLOOR)),
        "nu": np.full(K, 6.0) if student else None,
        "P": np.full((K, K), 0.04 / (K - 1)) + np.eye(K) * (0.96 - 0.04 / (K - 1)),
        "delta": np.full(K, 1.0 / K),
    }


def em(r: np.ndarray, p: dict, max_iter: int = 400, tol: float = 1e-8) -> tuple[dict, float]:
    p = {k: (None if v is None else np.array(v, dtype=float)) for k, v in p.items()}
    student = p["nu"] is not None
    prev = -np.inf
    for _ in range(max_iter):
        logB = log_emission(r, p["mu"], p["sig"], p["nu"])
        alpha, pred, ll = forward(logB, p["P"], p["delta"])
        beta = backward(logB, p["P"])
        gamma = alpha * beta
        gamma /= gamma.sum(axis=1, keepdims=True)
        B = np.exp(logB - logB.max(axis=1, keepdims=True))
        xi = alpha[:-1, :, None] * p["P"][None, :, :] * (B[1:] * beta[1:])[:, None, :]
        xi /= xi.sum(axis=(1, 2), keepdims=True)
        counts = xi.sum(axis=0)
        p["P"] = counts / counts.sum(axis=1, keepdims=True)
        p["delta"] = gamma[0]
        w = gamma.sum(axis=0)
        if student:
            z2 = ((r[:, None] - p["mu"]) / p["sig"]) ** 2
            u = (p["nu"] + 1) / (p["nu"] + z2)
            p["mu"] = (gamma * u * r[:, None]).sum(axis=0) / (gamma * u).sum(axis=0)
            var = (gamma * u * (r[:, None] - p["mu"]) ** 2).sum(axis=0) / w
            p["sig"] = np.maximum(np.sqrt(var), SIGMA_FLOOR)
            z2 = ((r[:, None] - p["mu"]) / p["sig"]) ** 2
            for k in range(len(w)):
                obj = [np.sum(gamma[:, k] * (t_const(nu) - 0.5 * (nu + 1) * np.log1p(z2[:, k] / nu))) for nu in NU_GRID]
                p["nu"][k] = NU_GRID[int(np.argmax(obj))]
        else:
            p["mu"] = (gamma * r[:, None]).sum(axis=0) / w
            var = (gamma * (r[:, None] - p["mu"]) ** 2).sum(axis=0) / w
            p["sig"] = np.maximum(np.sqrt(var), SIGMA_FLOOR)
        if ll - prev < tol * abs(prev):
            break
        prev = ll
    o = np.argsort(p["sig"])  # identify states by volatility, inside every fit
    p = {
        "mu": p["mu"][o],
        "sig": p["sig"][o],
        "nu": None if p["nu"] is None else p["nu"][o],
        "P": p["P"][np.ix_(o, o)],
        "delta": p["delta"][o],
    }
    logB = log_emission(r, p["mu"], p["sig"], p["nu"])
    return p, forward(logB, p["P"], p["delta"])[2]


def fit(r: np.ndarray, K: int, student: bool, rng: np.random.Generator, starts: int = 8, warm: dict | None = None):
    candidates = [init_params(r, K, student, rng) for _ in range(starts)]
    if warm is not None:
        candidates.insert(0, warm)
    best = None
    for c in candidates:
        p, ll = em(r, c)
        if best is None or ll > best[1]:
            best = (p, ll)
    return best


# ---------------------------------------------------------------------------
# Summaries


def n_params(K: int, student: bool) -> int:
    return K * (3 if student else 2) + K * (K - 1)


def stationary(P: np.ndarray) -> np.ndarray:
    w, v = np.linalg.eig(P.T)
    pi = np.real(v[:, np.argmin(np.abs(w - 1))])
    return pi / pi.sum()


def describe(label: str, p: dict, ll: float, T: int, student: bool) -> None:
    K = len(p["sig"])
    ev = np.sort(np.abs(np.linalg.eigvals(p["P"])))[::-1]
    lam2 = ev[1]
    bic = -2 * ll + n_params(K, student) * math.log(T)
    pi = stationary(p["P"])
    print(
        f"\n  {label}: loglik {ll:,.1f}   BIC {bic:,.1f}   |lambda2| {lam2:.4f}   half-life {math.log(2) / -math.log(lam2):.1f} days"
    )
    for k in range(K):
        sd = p["sig"][k] * (math.sqrt(p["nu"][k] / (p["nu"][k] - 2)) if student and p["nu"][k] > 2 else 1.0)
        extra = f"   nu {p['nu'][k]:5.1f}" if student else ""
        print(
            f"    state {k}: ann. vol {100 * sd * math.sqrt(A):5.1f}%   ann. mean {100 * p['mu'][k] * A:+6.1f}%"
            f"   p_kk {p['P'][k, k]:.4f}   expected spell {1 / (1 - p['P'][k, k]):6.1f} days"
            f"   occupancy {100 * pi[k]:4.1f}%{extra}"
        )


def predictive_moments(pred: np.ndarray, p: dict) -> tuple[np.ndarray, np.ndarray]:
    var_k = p["sig"] ** 2 * (p["nu"] / (p["nu"] - 2) if p["nu"] is not None else 1.0)
    mean = pred @ p["mu"]
    var = pred @ var_k + pred @ (p["mu"] ** 2) - mean**2
    return mean, var


def newey_west_se(x: np.ndarray, lags: int = 20) -> float:
    x = x - x.mean()
    n = len(x)
    s = x @ x / n
    for j in range(1, lags + 1):
        s += 2 * (1 - j / (lags + 1)) * (x[j:] @ x[:-j]) / n
    return math.sqrt(s / n)


def strategy(w: np.ndarray, excess: np.ndarray) -> dict:
    pnl = w * excess
    ann = pnl.mean() * A
    vol = pnl.std() * math.sqrt(A)
    wealth = np.cumsum(np.log1p(pnl))
    dd = np.max(np.maximum.accumulate(wealth) - wealth)
    return {
        "ret": ann,
        "vol": vol,
        "sharpe": ann / vol,
        "maxdd": 1 - math.exp(-dd),
        "turnover": np.abs(np.diff(w)).mean() * A,
        "lev": w.mean(),
    }


def switches_per_year(prob: np.ndarray) -> float:
    s = prob > 0.5
    return np.count_nonzero(s[1:] != s[:-1]) / (len(s) / A)


# ---------------------------------------------------------------------------


def walk_forward(r: np.ndarray, years: np.ndarray, student: bool, rng: np.random.Generator):
    """Predicted xi(t|t-1) for every out-of-sample day, from annual expanding-window refits."""
    pred_oos = np.full((len(r), 2), np.nan)
    params = {}
    warm = None
    for y in range(FIRST_OOS_YEAR, int(years.max()) + 1):
        train = years < y
        p, _ = fit(r[train], 2, student, rng, starts=8 if warm is None else 0, warm=warm)
        warm = p
        params[y] = p
        upto = years <= y
        logB = log_emission(r[upto], p["mu"], p["sig"], p["nu"])
        _, pred, _ = forward(logB, p["P"], stationary(p["P"]))
        this = years[upto] == y
        pred_oos[np.flatnonzero(upto)[this]] = pred[this]
    return pred_oos, params


def main() -> None:
    rng = np.random.default_rng(SEED)
    dates, total, excess = load()
    r = np.log1p(total)
    years = dates // 10000
    T = len(r)
    print(f"  {T:,} days, {dates[0]} to {dates[-1]}; sample daily vol {100 * r.std() * math.sqrt(A):.1f}% annualised")

    # Full-sample fits: descriptive only (rung 2 of the filtration ladder).
    full = {}
    for label, K, student in [
        ("Gaussian, K=2", 2, False),
        ("Student-t, K=2", 2, True),
        ("Gaussian, K=3", 3, False),
        ("Student-t, K=3", 3, True),
    ]:
        p, ll = fit(r, K, student, rng)
        full[label] = p
        describe(label, p, ll, T, student)
        logB = log_emission(r, p["mu"], p["sig"], p["nu"])
        alpha, pred, _ = forward(logB, p["P"], p["delta"])
        beta = backward(logB, p["P"])
        sm = alpha * beta
        sm /= sm.sum(axis=1, keepdims=True)
        print(
            f"    smoothed regime switches per year (top-state probability crossing one half): {switches_per_year(sm[:, -1]):.2f}"
        )

    smooth_t = None
    p = full["Student-t, K=2"]
    logB = log_emission(r, p["mu"], p["sig"], p["nu"])
    alpha, _, _ = forward(logB, p["P"], p["delta"])
    smooth_t = alpha * backward(logB, p["P"])
    smooth_t /= smooth_t.sum(axis=1, keepdims=True)

    # Walk-forward: rung 5.
    pred_g, params_g = walk_forward(r, years, False, rng)
    pred_t, params_t = walk_forward(r, years, True, rng)
    oos = years >= FIRST_OOS_YEAR
    n_years = oos.sum() / A
    print(
        f"\n  Walk-forward, {FIRST_OOS_YEAR}-{years.max()}: {oos.sum():,} days ({n_years:.1f} years), annual expanding-window refits"
    )
    last = params_t[int(years.max())]
    print(
        f"    last Student-t refit: calm vol {100 * last['sig'][0] * math.sqrt(A * last['nu'][0] / (last['nu'][0] - 2)):.1f}%,"
        f" turbulent vol {100 * last['sig'][1] * math.sqrt(A * last['nu'][1] / (last['nu'][1] - 2)):.1f}%,"
        f" p11 {last['P'][0, 0]:.4f}, p22 {last['P'][1, 1]:.4f}"
    )
    for label, pr in [("Gaussian", pred_g), ("Student-t", pred_t)]:
        q = pr[oos, 1]
        print(
            f"    {label:<10} predicted P(turbulent) > 0.5 on {100 * np.mean(q > 0.5):4.1f}% of days;"
            f" switches per year {switches_per_year(q):.2f}"
        )

    # One-step predictive log scores, out of sample.
    sig2 = np.empty(T)
    sig2[0] = r[:A].var()
    for t in range(1, T):
        sig2[t] = EWMA_LAMBDA * sig2[t - 1] + (1 - EWMA_LAMBDA) * r[t - 1] ** 2
    burn = years < FIRST_OOS_YEAR
    zb = r[burn] / np.sqrt(sig2[burn])
    grid = NU_GRID[NU_GRID > 2.05]
    nu_ewma = grid[
        int(
            np.argmax(
                [
                    np.sum(0.5 * np.log(nu / (nu - 2)) - 0.5 * (nu + 1) * np.log1p(zb * zb / (nu - 2)))
                    + len(zb) * t_const(nu)
                    for nu in grid
                ]
            )
        )
    ]
    sc_ewma_n = -0.5 * r * r / sig2 - 0.5 * np.log(2 * math.pi * sig2)
    s_t = np.sqrt(sig2 * (nu_ewma - 2) / nu_ewma)
    sc_ewma_t = t_const(nu_ewma) - np.log(s_t) - 0.5 * (nu_ewma + 1) * np.log1p((r / s_t) ** 2 / nu_ewma)

    def hmm_score(pred, params_by_year):
        out = np.full(T, np.nan)
        for y, p in params_by_year.items():
            m = years == y
            le = log_emission(r[m], p["mu"], p["sig"], p["nu"])
            mx = le.max(axis=1)
            out[m] = mx + np.log((pred[m] * np.exp(le - mx[:, None])).sum(axis=1))
        return out

    sc_hmm_g = hmm_score(pred_g, params_g)
    sc_hmm_t = hmm_score(pred_t, params_t)
    print(
        f"\n  Out-of-sample average log score per day (higher is better), EWMA lambda {EWMA_LAMBDA}, EWMA-t nu {nu_ewma:.1f}"
    )
    base = sc_ewma_n[oos]
    for label, sc in [
        ("EWMA normal", sc_ewma_n),
        ("EWMA Student-t", sc_ewma_t),
        ("HMM Gaussian", sc_hmm_g),
        ("HMM Student-t", sc_hmm_t),
    ]:
        d = sc[oos] - base
        print(f"    {label:<15} {sc[oos].mean():.4f}   vs EWMA normal {d.mean():+.4f} (se {newey_west_se(d):.4f})")
    d = sc_hmm_t[oos] - sc_ewma_t[oos]
    print(f"    HMM Student-t minus EWMA Student-t: {d.mean():+.4f} (se {newey_west_se(d):.4f})")

    # What the predicted state separates: realised excess-return moments by predicted state.
    calm = pred_t[oos, 1] < 0.5
    ex_oos = excess[oos]
    print("\n  Realised excess returns by walk-forward predicted state (Student-t)")
    for label, m in [("predicted calm", calm), ("predicted turbulent", ~calm)]:
        x = ex_oos[m]
        print(
            f"    {label:<20} {100 * m.mean():4.1f}% of days   ann. mean {100 * x.mean() * A:+5.1f}%"
            f" (se {100 * A * newey_west_se(x):.1f})   ann. vol {100 * x.std() * math.sqrt(A):5.1f}%"
        )
    dm = np.where(calm, 1 / calm.mean(), -1 / (~calm).mean()) * ex_oos
    print(
        f"    mean difference calm minus turbulent: {100 * A * dm.mean():+.1f}% a year (se {100 * A * newey_west_se(dm):.1f})"
    )

    # Strategies on excess returns, positions set from information through t-1.
    ex = excess[oos]
    var_hmm = np.empty(oos.sum())
    idx = np.flatnonzero(oos)
    for y, p in params_t.items():
        m = years[idx] == y
        _, v = predictive_moments(pred_t[idx[m]], p)
        var_hmm[m] = v
    w_bh = np.ones_like(ex)
    w_ewma = np.minimum(TARGET_VOL / np.sqrt(sig2[oos]), MAX_LEVERAGE)
    w_hmm = np.minimum(TARGET_VOL / np.sqrt(var_hmm), MAX_LEVERAGE)
    w_gate = (pred_t[oos, 1] < 0.5).astype(float)
    print(
        f"\n  Strategies, {FIRST_OOS_YEAR}-{years.max()}, excess returns, target vol {100 * TARGET_VOL * math.sqrt(A):.0f}%, leverage cap {MAX_LEVERAGE}"
    )
    print("    strategy           ann.ret  ann.vol  Sharpe  max DD  turnover  avg lev")
    for label, w in [
        ("buy and hold", w_bh),
        ("HMM gate (t)", w_gate),
        ("EWMA vol target", w_ewma),
        ("HMM vol target (t)", w_hmm),
    ]:
        s = strategy(w, ex)
        print(
            f"    {label:<18} {100 * s['ret']:6.1f}%  {100 * s['vol']:6.1f}%  {s['sharpe']:6.2f}"
            f"  {100 * s['maxdd']:5.1f}%  {s['turnover']:7.1f}  {s['lev']:6.2f}"
        )
    print(f"    Sharpe standard error over {n_years:.0f} years at S=0.5: {math.sqrt((1 + 0.125) / n_years):.2f}")
    corr = np.corrcoef(np.sqrt(var_hmm), np.sqrt(sig2[oos]))[0, 1]
    print(f"    correlation of HMM and EWMA predicted volatility: {corr:.3f}")

    # Detection lag in 2008 and 2020.
    for start, label in [(20080901, "September 2008"), (20200220, "February 2020")]:
        i0 = np.searchsorted(dates, start)
        hit = np.flatnonzero(pred_t[i0:, 1] > 0.5)
        print(
            f"    {label}: predicted P(turbulent) first exceeds one half {hit[0] if len(hit) else -1} trading days after {start}"
        )

    figure(dates, total, pred_t, pred_g, smooth_t, oos)


def figure(dates, total, pred_t, pred_g, smooth_t, oos) -> None:
    t = np.array([np.datetime64(f"{d // 10000:04d}-{d // 100 % 100:02d}-{d % 100:02d}") for d in dates])
    fig, axes = plt.subplots(2, 1, figsize=(7.0, 5.6), gridspec_kw={"height_ratios": [1.35, 1.0], "hspace": 0.42})

    ax = axes[0]
    wealth = np.exp(np.cumsum(np.log1p(total)))
    lo_w, hi_w = wealth.min() * 0.6, wealth.max() * 1.6
    turb = (oos & (pred_t[:, 1] > 0.5)).astype(int)
    edges = np.flatnonzero(np.diff(np.concatenate([[0], turb, [0]])))
    for i0, i1 in zip(edges[::2], edges[1::2], strict=True):
        ax.axvspan(t[i0], t[min(i1, len(t) - 1)], color=RUST, alpha=0.38, linewidth=0)
    ax.plot(t[::5], wealth[::5], color=INK, linewidth=0.9)
    ax.set_yscale("log")
    ax.set_ylim(lo_w, hi_w)
    ax.set_ylabel("growth of one dollar\n(log scale)", fontsize=9.5, color=MUTED)
    ax.axvline(t[np.argmax(oos)], color=GREY, linewidth=0.8, linestyle="--")
    ax.text(t[np.argmax(oos)], hi_w / 1.4, "  walk-forward starts", fontsize=8.8, color=MUTED, va="top")
    ax.set_title(
        "US market, 1926-2025: shaded where the predicted turbulent probability exceeds one half",
        fontsize=10.0,
        color=INK,
        loc="left",
        pad=8,
    )

    ax = axes[1]
    lo, hi = np.searchsorted(dates, 20070601), np.searchsorted(dates, 20091231)
    ax.plot(t[lo:hi], smooth_t[lo:hi, 1], color=GREY, linewidth=1.2, label="smoothed, full sample")
    ax.plot(t[lo:hi], pred_g[lo:hi, 1], color=TEAL, linewidth=0.9, label="predicted, Gaussian")
    ax.plot(t[lo:hi], pred_t[lo:hi, 1], color=RUST, linewidth=1.3, label="predicted, Student-t")
    ax.set_ylim(-0.03, 1.03)
    ax.set_ylabel("P(turbulent)", fontsize=9.5, color=MUTED)
    ax.legend(
        fontsize=8.8,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.13),
        ncol=3,
        frameon=False,
        labelcolor=MUTED,
        handlelength=1.8,
    )
    ax.set_title(
        "2007-2009 in detail: walk-forward predicted versus full-sample smoothed",
        fontsize=10.0,
        color=INK,
        loc="left",
        pad=8,
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

    for ax in axes:
        ax.tick_params(labelsize=9.0, colors=MUTED, length=3)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GREY)

    out = Path(__file__).with_suffix(".svg")
    fig.savefig(out, transparent=True, bbox_inches="tight", metadata={"Date": None})
    print(f"\n  wrote {out.name}")


if __name__ == "__main__":
    main()

# Predictive regressions: the two ways a return-forecasting regression finds
# predictability that is not there.
#
#   Left  — Stambaugh bias. Monthly returns are regressed on last month's value
#           of a persistent predictor (think: the dividend yield), over 40 years.
#           Returns are unpredictable, but the predictor's own innovations are
#           strongly negatively correlated with returns — a price rise lowers the
#           yield in the same month. The autoregressive coefficient of the
#           predictor is estimated with a downward bias, and that bias leaks
#           into the slope. The t-statistic is shifted right: a one-sided 5%
#           test of "higher yield predicts higher returns" rejects far too often.
#   Right — overlapping long-horizon regressions. Now the predictor is
#           exogenous, so the only problem is overlap: h-month returns built from
#           monthly data share h-1 months with their neighbours. Classical
#           standard errors are hopeless; Newey-West with h lags is still badly
#           oversized at long horizons in a 40-year sample; Hodrick (1992)
#           standard errors, which exploit the null of no predictability, hold up.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "em_predictive"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

T = 480
RHO = 0.99
TRIALS = 5000
HORIZONS = [1, 3, 6, 12, 24, 36, 60]


def simulate_paths(corr: float, trials: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Predictor x_0..x_T (AR(1), stationary start) and returns r_1..r_T with corr(r_t, v_t) = corr."""
    v = rng.standard_normal((trials, T + 1))
    u = corr * v + np.sqrt(1 - corr**2) * rng.standard_normal((trials, T + 1))
    x = np.empty((trials, T + 1))
    x[:, 0] = v[:, 0] / np.sqrt(1 - RHO**2)
    for t in range(1, T + 1):
        x[:, t] = RHO * x[:, t - 1] + v[:, t]
    return x, u[:, 1:]


def one_period(x: np.ndarray, r: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Regress r_{t+1} on x_t; also return the predictor's own AR(1) estimate."""
    xl = x[:, :-1]
    xc = xl - xl.mean(axis=1, keepdims=True)
    rc = r - r.mean(axis=1, keepdims=True)
    sxx = (xc * xc).sum(axis=1)
    beta = (xc * rc).sum(axis=1) / sxx
    e = rc - beta[:, None] * xc
    t = beta / np.sqrt((e * e).sum(axis=1) / (T - 3) / sxx)

    xn = x[:, 1:] - x[:, 1:].mean(axis=1, keepdims=True)
    rho_hat = (xc * xn).sum(axis=1) / sxx
    return beta, t, rho_hat


def long_horizon(x: np.ndarray, r: np.ndarray, h: int) -> dict[str, np.ndarray]:
    """Regress R_{t,h} = r_{t+1} + ... + r_{t+h} on x_t, with three standard errors."""
    n_obs = T - h + 1
    csum = np.concatenate([np.zeros((r.shape[0], 1)), r.cumsum(axis=1)], axis=1)
    R = csum[:, h : h + n_obs] - csum[:, 0:n_obs]  # R[:, t] = r_{t+1} + ... + r_{t+h}
    xl = x[:, :n_obs]
    xc = xl - xl.mean(axis=1, keepdims=True)
    Rc = R - R.mean(axis=1, keepdims=True)
    sxx = (xc * xc).sum(axis=1)
    beta = (xc * Rc).sum(axis=1) / sxx
    e = Rc - beta[:, None] * xc

    t_ols = beta / np.sqrt((e * e).sum(axis=1) / (n_obs - 2) / sxx)

    score = xc * e
    meat = (score * score).sum(axis=1)
    for k in range(1, h + 1):
        meat += 2 * (1 - k / (h + 1)) * (score[:, k:] * score[:, :-k]).sum(axis=1)
    t_nw = beta / (np.sqrt(meat) / sxx)

    # Hodrick (1992) 1B: under the null, one-period residuals times the sum of
    # the h most recent predictor values.
    xall = x[:, :T] - x[:, :T].mean(axis=1, keepdims=True)
    cx = np.concatenate([np.zeros((x.shape[0], 1)), xall.cumsum(axis=1)], axis=1)
    s = cx[:, h:T + 1] - cx[:, 0:T - h + 1]  # s[:, j] = x_j + ... + x_{j+h-1}
    eps = r - r.mean(axis=1, keepdims=True)
    eps_next = eps[:, h - 1 : T]  # r_{j+h}, paired with the window ending at x_{j+h-1}
    meat_h = ((eps_next * s) ** 2).sum(axis=1)
    t_hodrick = beta / (np.sqrt(meat_h) / sxx)

    r2 = 1 - (e * e).sum(axis=1) / (Rc * Rc).sum(axis=1)
    return {"ols": t_ols, "nw": t_nw, "hodrick": t_hodrick, "r2": r2}


def main() -> None:
    rng = np.random.default_rng(20260913)

    x0, r0 = simulate_paths(0.0, TRIALS, rng)
    x1, r1 = simulate_paths(-0.95, TRIALS, rng)
    _, t_exo, _ = one_period(x0, r0)
    b_end, t_end, rho_hat = one_period(x1, r1)

    stambaugh = -0.95 * (-(1 + 3 * RHO) / T)
    se_theory = np.sqrt((1 - RHO**2) / T)

    rows = []
    for h in HORIZONS:
        lh = long_horizon(x0, r0, h)
        rows.append(
            (
                h,
                np.mean(np.abs(lh["ols"]) > 1.96),
                np.mean(np.abs(lh["nw"]) > 1.96),
                np.mean(np.abs(lh["hodrick"]) > 1.96),
                np.median(lh["r2"]),
                np.percentile(lh["r2"], 90),
            )
        )
    rows = np.array(rows)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.6, 3.9))

    bins = np.linspace(-4.5, 6.5, 89)
    axL.hist(t_exo, bins=bins, density=True, color=TEAL, alpha=0.8, label="exogenous predictor")
    axL.hist(t_end, bins=bins, density=True, color=RUST, alpha=0.55, label="innovation corr. −0.95")
    axL.axvline(1.645, color=INK, lw=0.9, ls="--")
    axL.text(1.75, 0.50, "one-sided 5%", fontsize=9, color=INK)
    axL.set_ylim(0, 0.56)
    axL.set_xlabel("t-statistic on the predictor (true slope = 0)", fontsize=10, color=MUTED)
    axL.set_ylabel("density", fontsize=10, color=MUTED)
    axL.set_title("Stambaugh bias: ρ = 0.99, 40 years monthly", fontsize=11, color=INK, loc="left", pad=8)
    axL.legend(frameon=False, fontsize=9.5, loc="upper left")

    hs = rows[:, 0]
    axR.axhline(0.05, color=GREY, lw=1.0, ls=":")
    axR.plot(hs, rows[:, 1], "o-", color=RUST, lw=2.0, ms=4.5, label="classical SE")
    axR.plot(hs, rows[:, 2], "s--", color=INK, lw=1.6, ms=4.0, label="Newey–West, h lags")
    axR.plot(hs, rows[:, 3], "o-", color=TEAL, lw=2.0, ms=4.5, label="Hodrick (1992)")
    axR.set_xscale("log")
    axR.set_xticks(HORIZONS)
    axR.set_xticklabels([str(h) for h in HORIZONS])
    axR.set_ylim(0, 1.0)
    axR.text(14, 0.003, "nominal 5%", fontsize=9, color=MUTED, va="bottom")
    axR.set_xlabel("return horizon h (months), overlapping", fontsize=10, color=MUTED)
    axR.set_ylabel("false rejection rate", fontsize=10, color=MUTED)
    axR.set_title("Overlap: exogenous predictor, no predictability", fontsize=11, color=INK, loc="left", pad=8)
    axR.legend(frameon=False, fontsize=9.5, loc="upper left")

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

    print(f"Left panel: T = {T} months, rho = {RHO}, {TRIALS} trials")
    print(f"  mean rho_hat - rho            {np.mean(rho_hat) - RHO:+.4f}   (Kendall approx {-(1 + 3 * RHO) / T:+.4f})")
    print(f"  mean beta_hat (true 0)        {np.mean(b_end):+.5f}   (Stambaugh approx {stambaugh:+.5f})")
    print(f"  approx s.e. of beta_hat       {se_theory:.5f}   -> bias / s.e. = {stambaugh / se_theory:.2f}")
    print(f"  mean t, exogenous             {np.mean(t_exo):+.3f}")
    print(f"  mean t, corr -0.95            {np.mean(t_end):+.3f}")
    print(f"  one-sided rejection (t>1.645) exogenous {np.mean(t_exo > 1.645):.3f}   corr -0.95 {np.mean(t_end > 1.645):.3f}")
    print(f"  two-sided rejection (|t|>1.96) exogenous {np.mean(np.abs(t_exo) > 1.96):.3f}   corr -0.95 {np.mean(np.abs(t_end) > 1.96):.3f}")
    print()
    print("Right panel: exogenous predictor, overlapping h-month returns")
    print(f"{'h':>4} {'classical':>10} {'NW(h)':>7} {'Hodrick':>8} {'median R2':>10} {'90th pct R2':>12}")
    for row in rows:
        print(f"{int(row[0]):4d} {row[1]:10.3f} {row[2]:7.3f} {row[3]:8.3f} {row[4]:10.3f} {row[5]:12.3f}")


main()

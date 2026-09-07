# The identification asymmetry at the heart of regime modelling: fit a correctly
# specified two-state Gaussian HMM to ten years of daily data and the state
# VOLATILITIES come back essentially exact, while the state MEANS come back as
# noise. Sampling distributions from 400 independent simulations.
#
# Run standalone:  uv run --no-project --with matplotlib python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
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

A = 252
YEARS = 10
REPS = 400
# A second, smaller arm at a 30-year span, printed but not plotted: it shows how
# slowly the mean estimates improve relative to the volatility estimates.
YEARS_LONG = 30
REPS_LONG = 150
SEED = 20240101

# Calm state: +10% drift, 12% vol, expected duration 100 days.
# Turbulent state: -15% drift, 32% vol, expected duration 25 days.
MU_ANN = np.array([0.10, -0.15])
SIG_ANN = np.array([0.12, 0.32])
P = np.array([[0.99, 0.01], [0.04, 0.96]])


def simulate(mu, sig, T, rng):
    pi = np.array([(1 - P[1, 1]), (1 - P[0, 0])])
    pi = pi / pi.sum()
    s = np.empty(T, dtype=int)
    s[0] = rng.choice(2, p=pi)
    u = rng.random(T)
    for t in range(1, T):
        s[t] = s[t - 1] if u[t] < P[s[t - 1], s[t - 1]] else 1 - s[t - 1]
    return mu[s] + sig[s] * rng.standard_normal(T)


def em_fit(r, rng, n_iter=200, tol=1e-9):
    T = len(r)
    q = np.quantile(np.abs(r), [0.3, 0.7])
    mu = rng.normal(0.0, r.std() * 0.1, 2)
    sig = np.maximum(q * (1 + 0.1 * rng.standard_normal(2)), 1e-6)
    Ph = np.array([[0.95, 0.05], [0.05, 0.95]])
    pi = np.array([0.5, 0.5])
    prev = -np.inf
    for _ in range(n_iter):
        z = (r[:, None] - mu[None, :]) / sig[None, :]
        B = np.maximum(np.exp(-0.5 * z * z) / (sig[None, :] * np.sqrt(2 * np.pi)), 1e-300)
        alpha = np.zeros((T, 2))
        c = np.zeros(T)
        a = pi * B[0]
        c[0] = a.sum()
        alpha[0] = a / c[0]
        for t in range(1, T):
            a = (alpha[t - 1] @ Ph) * B[t]
            c[t] = a.sum()
            alpha[t] = a / c[t]
        beta = np.ones((T, 2))
        for t in range(T - 2, -1, -1):
            beta[t] = (Ph @ (B[t + 1] * beta[t + 1])) / c[t + 1]
        gamma = alpha * beta
        gamma /= gamma.sum(axis=1, keepdims=True)
        xi = Ph * (alpha[:-1].T @ ((B[1:] * beta[1:]) / c[1:, None]))
        Ph = xi / xi.sum(axis=1, keepdims=True)
        pi = gamma[0]
        w = gamma.sum(axis=0)
        mu = (gamma * r[:, None]).sum(axis=0) / w
        sig = np.sqrt(np.maximum((gamma * (r[:, None] - mu[None, :]) ** 2).sum(axis=0) / w, 1e-14))
        ll = np.log(c).sum()
        if ll - prev < tol * abs(prev):
            break
        prev = ll
    o = np.argsort(sig)  # identify states by volatility, never by mean
    return mu[o], sig[o]


def run(years=YEARS, reps=REPS, seed=SEED):
    rng = np.random.default_rng(seed)
    mu_d = MU_ANN / A
    sig_d = SIG_ANN / np.sqrt(A)
    out = np.zeros((reps, 4))
    for i in range(reps):
        r = simulate(mu_d, sig_d, years * A, rng)
        m, s = em_fit(r, rng)
        out[i] = [m[0] * A, m[1] * A, s[0] * np.sqrt(A), s[1] * np.sqrt(A)]
    return out


def report(est, label):
    """Prints the sampling-distribution table quoted in the document."""
    names = ["calm mean", "turbulent mean", "calm volatility", "turbulent volatility"]
    truth = [MU_ANN[0], MU_ANN[1], SIG_ANN[0], SIG_ANN[1]]
    print(f"\n  {label}: {len(est)} reps")
    for j, n in enumerate(names):
        v = est[:, j]
        print(f"    {n:<22} true {truth[j]:+.3f}   mean {v.mean():+.4f}   sd {v.std():.4f}")
    spread = est[:, 0] - est[:, 1]
    ratio = est[:, 3] / est[:, 2]
    print(
        f"    {'mean spread':<22} true {MU_ANN[0] - MU_ANN[1]:+.3f}   "
        f"mean {spread.mean():+.4f}   sd {spread.std():.4f}   "
        f"wrong sign {np.mean(spread < 0):.3f}   s/n {spread.mean() / spread.std():.2f}"
    )
    print(
        f"    {'volatility ratio':<22} true {SIG_ANN[1] / SIG_ANN[0]:+.3f}   "
        f"mean {ratio.mean():+.4f}   sd {ratio.std():.4f}   "
        f"s/n {(ratio.mean() - 1) / ratio.std():.2f}"
    )


def panel(ax, samples, truths, labels, colors, places, xlabel, xlim):
    """places: (x-offset in points, y in axes fraction, horizontal alignment)."""
    for v, truth, lab, col, (dx, yf, ha) in zip(samples, truths, labels, colors, places):
        ax.hist(v, bins=44, range=xlim, color=col, alpha=0.55, edgecolor="none")
        ax.axvline(truth, color=col, linewidth=1.6, linestyle="--")
        ax.annotate(
            lab,
            xy=(truth, yf),
            xycoords=("data", "axes fraction"),
            xytext=(dx, 0),
            textcoords="offset points",
            fontsize=9.5,
            color=col,
            ha=ha,
            va="top",
        )
    ax.set_xlim(*xlim)
    ax.set_xlabel(xlabel, fontsize=9.5, color=MUTED)
    ax.tick_params(labelsize=9.0, colors=MUTED, length=3)
    ax.set_yticks([])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GREY)


def main():
    est = run()
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.2))

    panel(
        axes[0],
        [est[:, 2], est[:, 3]],
        SIG_ANN,
        ["calm  12%", "turbulent  32%"],
        [TEAL, RUST],
        [(7, 0.99, "left"), (7, 0.99, "left")],
        "estimated annualised volatility per state",
        (0.05, 0.42),
    )
    panel(
        axes[1],
        [est[:, 0], est[:, 1]],
        MU_ANN,
        ["calm  +10%", "turbulent  -15%"],
        [TEAL, RUST],
        [(8, 0.99, "left"), (-8, 0.86, "right")],
        "estimated annualised mean per state",
        (-0.95, 0.75),
    )
    axes[1].axvline(0.0, color=GREY, linewidth=0.8, zorder=0)

    axes[0].set_title("Volatility: recovered almost exactly", fontsize=10.5, color=INK, pad=8, loc="left")
    axes[1].set_title("Mean: indistinguishable from noise", fontsize=10.5, color=INK, pad=8, loc="left")

    spread = est[:, 0] - est[:, 1]
    frac_wrong = float(np.mean(spread < 0))
    fig.text(
        0.5,
        -0.06,
        f"400 simulations, 10 years of daily data, correctly specified $K=2$ Gaussian HMM, "
        f"true parameters known to exist.\n"
        f"Volatility ratio recovered with {100 * est[:, 3].std() / est[:, 3].mean():.1f}% "
        f"relative error; the estimated mean spread has the WRONG SIGN in "
        f"{100 * frac_wrong:.0f}% of samples.",
        fontsize=9.0,
        color=MUTED,
        ha="center",
        va="top",
    )

    fig.tight_layout()
    out = Path(__file__).with_suffix(".svg")
    fig.savefig(out, transparent=True, bbox_inches="tight")
    print(f"  wrote {out.name}  (wrong-sign fraction {frac_wrong:.3f})")
    report(est, f"{YEARS} years daily")
    report(run(YEARS_LONG, REPS_LONG, SEED + 7), f"{YEARS_LONG} years daily")


if __name__ == "__main__":
    main()

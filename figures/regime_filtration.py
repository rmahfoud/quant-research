# The filtration ladder. One simulated path from a two-state Gaussian HMM with
# TRUE parameters known, showing how much of the apparent sharpness of a regime
# plot comes from looking at the future -- and what each rung of the ladder is
# worth in Sharpe terms.
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
SHADE = "#E8D9D2"

A = 252
MU = np.array([0.10, -0.15]) / A
SIG = np.array([0.12, 0.32]) / np.sqrt(A)
P = np.array([[0.99, 0.01], [0.04, 0.96]])
PI0 = np.array([0.8, 0.2])
REPS = 200
YEARS_MC = 15
SEED = 424242
LEAK_REPS = 30
LEAK_YEARS = 20

# Calibrations for the accompanying table: what separates the two states?
CALIBRATIONS = [
    ("vol and mean", (0.10, -0.15), (0.12, 0.32)),
    ("vol only", (0.05, 0.05), (0.12, 0.32)),
    ("mild vol", (0.12, -0.10), (0.15, 0.22)),
    ("mean only", (0.20, -0.20), (0.20, 0.20)),
]


def simulate(T, rng, mu=MU, sig=SIG):
    s = np.empty(T, dtype=int)
    s[0] = rng.choice(2, p=PI0)
    u = rng.random(T)
    for t in range(1, T):
        s[t] = s[t - 1] if u[t] < P[s[t - 1], s[t - 1]] else 1 - s[t - 1]
    return mu[s] + sig[s] * rng.standard_normal(T), s


def beliefs(r, mu=MU, sig=SIG):
    """Predicted, filtered and smoothed P(turbulent) under the TRUE parameters."""
    T = len(r)
    z = (r[:, None] - mu[None, :]) / sig[None, :]
    B = np.maximum(np.exp(-0.5 * z * z) / (sig[None, :] * np.sqrt(2 * np.pi)), 1e-300)
    alpha = np.zeros((T, 2))
    pred = np.zeros((T, 2))
    c = np.zeros(T)
    pred[0] = PI0
    a = PI0 * B[0]
    c[0] = a.sum()
    alpha[0] = a / c[0]
    for t in range(1, T):
        pred[t] = alpha[t - 1] @ P
        a = pred[t] * B[t]
        c[t] = a.sum()
        alpha[t] = a / c[t]
    beta = np.ones((T, 2))
    for t in range(T - 2, -1, -1):
        beta[t] = (P @ (B[t + 1] * beta[t + 1])) / c[t + 1]
    gamma = alpha * beta
    gamma /= gamma.sum(axis=1, keepdims=True)
    return pred, alpha, gamma


def sharpe(x):
    """Annualised Sharpe. A permanently flat position earns nothing, so it scores 0."""
    sd = float(x.std())
    return 0.0 if sd == 0.0 else float(x.mean() / sd * np.sqrt(A))


def ladder(mu_ann=None, sig_ann=None):
    """Sharpe of each rung, plus gating-vs-sizing and detection lag, for one calibration."""
    mu = MU if mu_ann is None else np.array(mu_ann) / A
    sig = SIG if sig_ann is None else np.array(sig_ann) / np.sqrt(A)
    rng = np.random.default_rng(SEED + 1)
    keys = ["bh", "oracle", "smooth", "filt", "pred", "acc", "size", "both", "lag",
            "turn_gate", "turn_size", "vol_gate"]
    acc = {k: [] for k in keys}
    sig_star = float(np.sqrt(PI0 @ (sig**2)))
    for _ in range(REPS):
        r, s = simulate(YEARS_MC * A, rng, mu, sig)
        pred, alpha, gamma = beliefs(r, mu, sig)
        w_gate = (pred[:, 0] > 0.5).astype(float)
        w_size = np.clip(sig_star / np.sqrt(pred @ (sig**2)), 0.0, 3.0)
        acc["bh"].append(sharpe(r))
        acc["oracle"].append(sharpe((s == 0).astype(float) * r))
        acc["smooth"].append(sharpe((gamma[:, 0] > 0.5).astype(float) * r))
        acc["filt"].append(sharpe((alpha[:, 0] > 0.5).astype(float) * r))
        acc["pred"].append(sharpe(w_gate * r))
        acc["size"].append(sharpe(w_size * r))
        acc["both"].append(sharpe(w_gate * w_size * r))
        acc["acc"].append(float(np.mean((pred[:, 1] > 0.5) == (s == 1))))
        acc["turn_gate"].append(float(np.mean(np.abs(np.diff(w_gate)))))
        acc["turn_size"].append(float(np.mean(np.abs(np.diff(w_size)))))
        acc["vol_gate"].append(float((w_gate * r).std() * np.sqrt(A)))
        sw = np.flatnonzero((s[1:] == 1) & (s[:-1] == 0)) + 1
        lags = [np.flatnonzero(alpha[t0 : t0 + 60, 1] > 0.5)[0]
                for t0 in sw if np.any(alpha[t0 : t0 + 60, 1] > 0.5)]
        if lags:
            acc["lag"].append(float(np.median(lags)))
    return {k: float(np.mean(v)) for k, v in acc.items()}


def em_fit(r, rng, n_iter=100, tol=1e-9):
    """Two-state Gaussian HMM by EM. States identified by fitted volatility."""
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
    o = np.argsort(sig)
    return mu[o], sig[o], Ph[np.ix_(o, o)]


def leakage(mu_ann=None, sig_ann=None, reps=LEAK_REPS, years=LEAK_YEARS, burn=5, refit=5):
    """Full-sample parameter fit versus honest expanding-window refit, both predicted."""
    mu = MU if mu_ann is None else np.array(mu_ann) / A
    sig = SIG if sig_ann is None else np.array(sig_ann) / np.sqrt(A)
    rng = np.random.default_rng(SEED + 2)
    T, b = years * A, burn * A
    out = {"bh": [], "full": [], "walk": [], "smooth": []}
    for _ in range(reps):
        r, _ = simulate(T, rng, mu, sig)
        out["bh"].append(sharpe(r[b:]))
        mh, sh, Ph = em_fit(r, rng)                       # fitted on ALL the data
        z = (r[:, None] - mh[None, :]) / sh[None, :]
        B = np.maximum(np.exp(-0.5 * z * z) / (sh[None, :] * np.sqrt(2 * np.pi)), 1e-300)
        al = np.zeros((T, 2))
        pr = np.zeros((T, 2))
        pr[0] = PI0
        a = PI0 * B[0]
        al[0] = a / a.sum()
        for t in range(1, T):
            pr[t] = al[t - 1] @ Ph
            a = pr[t] * B[t]
            al[t] = a / a.sum()
        out["full"].append(sharpe(((pr[:, 0] > 0.5).astype(float) * r)[b:]))
        be = np.ones((T, 2))
        cs = (al[:-1] @ Ph) * B[1:]
        cs = np.concatenate([[float((PI0 * B[0]).sum())], cs.sum(axis=1)])
        for t in range(T - 2, -1, -1):
            be[t] = (Ph @ (B[t + 1] * be[t + 1])) / cs[t + 1]
        gm = al * be
        gm /= gm.sum(axis=1, keepdims=True)
        out["smooth"].append(sharpe(((gm[:, 0] > 0.5).astype(float) * r)[b:]))
        pos = np.zeros(T)
        state = PI0.copy()
        for y in range(burn, years, refit):              # refit on data through t only
            t0, t1 = y * A, min((y + refit) * A, T)
            m2, s2, P2 = em_fit(r[:t0], rng)
            seg = r[t0:t1]
            z2 = (seg[:, None] - m2[None, :]) / s2[None, :]
            B2 = np.maximum(np.exp(-0.5 * z2 * z2) / (s2[None, :] * np.sqrt(2 * np.pi)), 1e-300)
            a2 = state @ P2
            for t in range(len(seg)):
                pos[t0 + t] = 1.0 if a2[0] > 0.5 else 0.0
                f = a2 * B2[t]
                state = f / f.sum()
                a2 = state @ P2
        out["walk"].append(sharpe((pos * r)[b:]))
    return {k: (float(np.mean(v)), float(np.std(v) / np.sqrt(len(v)))) for k, v in out.items()}  # noqa: E501


def main():
    rng = np.random.default_rng(SEED)
    T = 3 * A
    r, s = simulate(T, rng)
    pred, alpha, gamma = beliefs(r)
    x = np.arange(T) / A

    fig, axes = plt.subplots(
        3, 1, figsize=(7.0, 6.6), gridspec_kw={"height_ratios": [1.5, 1.5, 1.25], "hspace": 0.42}
    )

    # --- Panel 1: the path, with true turbulent spells shaded -----------------
    ax = axes[0]
    ax.fill_between(x, 0, 1, where=(s == 1), transform=ax.get_xaxis_transform(),
                    color=SHADE, linewidth=0, zorder=0)
    ax.plot(x, 100 * np.cumsum(r), color=INK, linewidth=1.2, zorder=2)
    ax.set_ylabel("cumulative\nlog return (%)", fontsize=9.5, color=MUTED)
    ax.set_title(
        "A simulated path. Shading marks the TRUE turbulent state — which you never see.",
        fontsize=10.0, color=INK, pad=7, loc="left",
    )

    # --- Panel 2: the three beliefs ------------------------------------------
    ax = axes[1]
    ax.fill_between(x, 0, 1, where=(s == 1), transform=ax.get_xaxis_transform(),
                    color=SHADE, linewidth=0, zorder=0)
    ax.fill_between(x, 0, gamma[:, 1], color=GREY, alpha=0.35, linewidth=0, zorder=1,
                    label="smoothed  $\\xi_{t|T}$   (uses the whole sample)")
    ax.plot(x, alpha[:, 1], color=TEAL, linewidth=1.15, zorder=3,
            label="filtered  $\\xi_{t|t}$   (uses data through $t$)")
    ax.plot(x, pred[:, 1], color=RUST, linewidth=1.0, linestyle=(0, (3, 1.6)), zorder=2,
            label="predicted  $\\xi_{t|t-1}$   (the only tradable one)")
    ax.set_ylim(-0.03, 1.06)
    ax.set_ylabel("P(turbulent)", fontsize=9.5, color=MUTED)
    ax.set_xlabel("years", fontsize=9.5, color=MUTED)
    ax.legend(fontsize=9.0, loc="upper left", frameon=False, ncol=1, labelcolor=MUTED,
              handlelength=1.8, borderaxespad=0.2)
    ax.set_title(
        "Three beliefs about the same state. Even with the true parameters, they differ.",
        fontsize=10.0, color=INK, pad=7, loc="left",
    )

    for a_ in axes[:2]:
        a_.set_xlim(0, 3)
        a_.tick_params(labelsize=9.0, colors=MUTED, length=3)
        for side in ("top", "right"):
            a_.spines[side].set_visible(False)
        for side in ("bottom", "left"):
            a_.spines[side].set_color(GREY)

    # --- Panel 3: what each rung is worth ------------------------------------
    res = ladder()
    ax = axes[2]
    names = ["Buy and hold", "Predicted  $\\xi_{t|t-1}$", "Filtered  $\\xi_{t|t}$",
             "Smoothed  $\\xi_{t|T}$", "Oracle (true state)"]
    vals = [res["bh"], res["pred"], res["filt"], res["smooth"], res["oracle"]]
    cols = [GREY, RUST, TEAL, GREY, INK]
    ypos = np.arange(len(vals))
    ax.barh(ypos, vals, color=cols, alpha=0.75, height=0.62, edgecolor="none")
    for y_, v in zip(ypos, vals):
        ax.text(v + 0.012, y_, f"{v:.2f}", va="center", fontsize=9.3, color=MUTED)
    ax.set_yticks(ypos)
    ax.set_yticklabels(names, fontsize=9.3, color=INK)
    ax.set_xlim(0, max(vals) * 1.18)
    ax.set_xlabel("annualised Sharpe ratio, long in calm and flat in turbulent", fontsize=9.5,
                  color=MUTED)
    ax.tick_params(labelsize=9.0, colors=MUTED, length=3)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GREY)
    ax.set_title(
        f"Cost of honesty: {REPS} runs of {YEARS_MC} years, true parameters known throughout.",
        fontsize=10.0, color=INK, pad=7, loc="left",
    )

    out = Path(__file__).with_suffix(".svg")
    fig.savefig(out, transparent=True, bbox_inches="tight")
    print(f"  wrote {out.name}")
    print(f"\n  {REPS} reps x {YEARS_MC}y daily, true parameters known. Sharpe ratios.")
    head = (f"  {'separated by':<14}{'B&H':>7}{'oracle':>8}{'smooth':>8}{'filt':>7}"
            f"{'pred':>7}{'size':>7}{'both':>7}{'accur':>8}{'lag':>6}")
    print(head)
    print("  " + "-" * (len(head) - 2))
    for label, mu_ann, sig_ann in CALIBRATIONS:
        m = res if label == "vol and mean" else ladder(mu_ann, sig_ann)
        print(f"  {label:<14}{m['bh']:>7.2f}{m['oracle']:>8.2f}{m['smooth']:>8.2f}"
              f"{m['filt']:>7.2f}{m['pred']:>7.2f}{m['size']:>7.2f}{m['both']:>7.2f}"
              f"{m['acc']:>8.3f}{m['lag']:>6.1f}")
    print(f"\n  Turnover and strategy volatility (mild vol calibration, the realistic one):")
    mv = ladder(*CALIBRATIONS[2][1:])
    print(f"    gate: mean |change in position| per day  {mv['turn_gate']:.4f}"
          f"  -> {mv['turn_gate'] * A:.1f} units per year")
    print(f"    size: mean |change in position| per day  {mv['turn_size']:.4f}"
          f"  -> {mv['turn_size'] * A:.1f} units per year")
    print(f"    gated strategy annualised volatility     {mv['vol_gate']:.4f}")
    print(f"    gross benefit over buy and hold          "
          f"{(mv['pred'] - mv['bh']) * mv['vol_gate'] * 1e4:.0f} bp per year")
    print(f"\n  Parameters ESTIMATED by EM, {LEAK_REPS} reps x {LEAK_YEARS}y. States sorted by")
    print("  fitted volatility inside each fit. Sharpe of the resulting strategy.")
    hd = f"  {'calibration':<14}{'B&H':>8}{'full/smooth':>13}{'full/pred':>11}{'walk/pred':>11}"
    print(hd)
    print("  " + "-" * (len(hd) - 2))
    for label, mu_ann, sig_ann in [CALIBRATIONS[0], CALIBRATIONS[3]]:
        lk = leakage(mu_ann, sig_ann)
        print(f"  {label:<14}{lk['bh'][0]:>8.2f}{lk['smooth'][0]:>13.2f}"
              f"{lk['full'][0]:>11.2f}{lk['walk'][0]:>11.2f}"
              f"   (se ~{max(lk['walk'][1], lk['full'][1]):.2f})")


if __name__ == "__main__":
    main()

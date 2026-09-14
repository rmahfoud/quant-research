# Clustered errors: why 5,000 observations can carry the information of a few hundred.
#
#   Left  — 50 clusters of 100 observations. The regressor is set at the cluster
#           level (think: a state law, an industry shock, a trading-day event),
#           and a share rho of the error variance is common within a cluster.
#           The true slope is zero. Classical and heteroskedasticity-robust
#           standard errors both ignore the common component, and their false
#           rejection rate climbs towards 60% at rho = 0.1. Cluster-robust
#           standard errors hold the 5% line.
#   Right — the same design with a binary treatment given to only a few of the
#           50 clusters. Cluster-robust inference is only as good as the number
#           of *treated* clusters: with one or two it rejects a true null far too
#           often. The wild cluster restricted bootstrap (Webb weights) errs the
#           other way — safe, but with little power — until treated clusters
#           number more than a handful.
#
# Normal errors make the within-cluster sum and sum of squares independent, so
# the simulation runs on cluster-level sufficient statistics.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "em_clustering"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

G = 50
T_CRIT_49 = 2.0096  # t(49) two-sided 5% critical value
WEBB = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)])


def draw_clusters(n: int, rho: float, trials: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Per-cluster sum and sum of squares of y = sqrt(rho) a_g + sqrt(1-rho) e_ig."""
    a = rng.standard_normal((trials, G))
    ebar = rng.standard_normal((trials, G)) / np.sqrt(n)
    ss_within = rng.chisquare(n - 1, (trials, G))
    s1 = n * np.sqrt(rho) * a + np.sqrt(1 - rho) * n * ebar
    sum_e2 = n * ebar**2 + ss_within
    s2 = n * rho * a**2 + 2 * np.sqrt(rho * (1 - rho)) * a * n * ebar + (1 - rho) * sum_e2
    return s1, s2


def ols_cluster_level(x: np.ndarray, n: int, s1: np.ndarray, s2: np.ndarray) -> dict[str, np.ndarray]:
    """OLS of y on (1, x_g) using only cluster sums; returns t-statistics under three variance formulas."""
    N = n * G
    xc = x - x.mean(axis=-1, keepdims=True)
    sxx = n * (xc**2).sum(axis=-1)
    ybar = s1.sum(axis=-1) / N
    beta = (xc * s1).sum(axis=-1) / sxx
    fitted = ybar[..., None] + beta[..., None] * xc
    resid_sum = s1 - n * fitted
    resid_ss = s2 - 2 * fitted * s1 + n * fitted**2

    v_classical = resid_ss.sum(axis=-1) / (N - 2) / sxx
    v_hc1 = N / (N - 2) * (xc**2 * resid_ss).sum(axis=-1) / sxx**2
    v_cr1 = G / (G - 1) * (N - 1) / (N - 2) * ((xc * resid_sum) ** 2).sum(axis=-1) / sxx**2
    return {
        "beta": beta,
        "classical": beta / np.sqrt(v_classical),
        "hc1": beta / np.sqrt(v_hc1),
        "cr1": beta / np.sqrt(v_cr1),
    }


def wild_cluster_p(x: np.ndarray, n: int, s1: np.ndarray, t_obs: float, B: int, rng: np.random.Generator) -> float:
    """Wild cluster restricted bootstrap p-value for H0: beta = 0, Webb weights."""
    N = n * G
    xc = x - x.mean()
    sxx = n * (xc**2).sum()
    u = s1 - n * s1.sum() / N  # cluster sums of restricted residuals
    v = WEBB[rng.integers(0, 6, size=(B, G))]
    vu = v * u
    beta_b = (vu * xc).sum(axis=1) / sxx
    resid_b = vu - (n / N) * vu.sum(axis=1, keepdims=True) - n * beta_b[:, None] * xc
    var_b = G / (G - 1) * (N - 1) / (N - 2) * ((xc * resid_b) ** 2).sum(axis=1) / sxx**2
    t_b = beta_b / np.sqrt(var_b)
    return float(np.mean(np.abs(t_b) >= abs(t_obs)))


def main() -> None:
    rng = np.random.default_rng(20260913)

    # Left: rejection rate against the intra-cluster correlation of the error.
    n_left, trials_left = 100, 4000
    rhos = [0.0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2]
    left = []
    for rho in rhos:
        x = rng.standard_normal((trials_left, G))
        s1, s2 = draw_clusters(n_left, rho, trials_left, rng)
        t = ols_cluster_level(x, n_left, s1, s2)
        moulton = 1 + (n_left - 1) * rho
        left.append(
            (
                rho,
                np.mean(np.abs(t["classical"]) > 1.96),
                np.mean(np.abs(t["hc1"]) > 1.96),
                np.mean(np.abs(t["cr1"]) > T_CRIT_49),
                moulton,
                np.sqrt(moulton),
                n_left * G / moulton,
            )
        )
    left = np.array(left)

    # Right: binary treatment in a few of the 50 clusters.
    n_right, rho_right, trials_right, B = 30, 0.05, 2000, 399
    treated = [1, 2, 3, 5, 10, 25]
    right = []
    for g1 in treated:
        x = np.zeros(G)
        x[:g1] = 1.0
        s1, s2 = draw_clusters(n_right, rho_right, trials_right, rng)
        t = ols_cluster_level(np.broadcast_to(x, (trials_right, G)), n_right, s1, s2)
        rej_cr = np.mean(np.abs(t["cr1"]) > T_CRIT_49)
        pvals = np.array([wild_cluster_p(x, n_right, s1[i], t["cr1"][i], B, rng) for i in range(trials_right)])
        right.append((g1, rej_cr, np.mean(pvals < 0.05), np.mean(np.abs(t["classical"]) > 1.96)))
    right = np.array(right)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.6, 3.9))

    axL.axhline(0.05, color=GREY, lw=1.0, ls=":")
    axL.plot(left[:, 0], left[:, 1], "o-", color=RUST, lw=2.0, ms=4.5, label="classical or het.-robust SE (identical)")
    axL.plot(left[:, 0], left[:, 3], "o-", color=TEAL, lw=2.0, ms=4.5, label="cluster-robust SE")
    axL.set_ylim(0, 0.8)
    axL.set_xlabel("share of error variance common to the cluster (ρ)", fontsize=10, color=MUTED)
    axL.set_ylabel("false rejection rate", fontsize=10, color=MUTED)
    axL.set_title("50 clusters × 100 observations", fontsize=11, color=INK, loc="left", pad=8)
    axL.text(0.13, 0.015, "nominal 5%", fontsize=9, color=MUTED)
    axL.legend(frameon=False, fontsize=9.5, loc="upper left")

    axR.axhline(0.05, color=GREY, lw=1.0, ls=":")
    axR.plot(right[:, 0], right[:, 1], "o-", color=RUST, lw=2.0, ms=4.5, label="cluster-robust SE, t(49)")
    axR.plot(right[:, 0], right[:, 2], "s-", color=TEAL, lw=2.0, ms=4.5, label="wild cluster bootstrap (Webb)")
    axR.set_xscale("log")
    axR.set_xticks(treated)
    axR.set_xticklabels([str(g) for g in treated])
    axR.set_ylim(0, 0.8)
    axR.set_xlabel("number of treated clusters (of 50)", fontsize=10, color=MUTED)
    axR.set_ylabel("false rejection rate", fontsize=10, color=MUTED)
    axR.set_title("What counts is treated clusters", fontsize=11, color=INK, loc="left", pad=8)
    axR.text(11, 0.015, "nominal 5%", fontsize=9, color=MUTED)
    axR.legend(frameon=False, fontsize=9.5, loc="upper right")

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

    print("Left panel: G = 50 clusters, n = 100 per cluster, regressor constant within cluster")
    print(f"{'rho':>6} {'classical':>10} {'HC1':>7} {'CR1':>7} {'Moulton':>8} {'SE ratio':>9} {'eff. N':>8}")
    for r in left:
        print(f"{r[0]:6.3f} {r[1]:10.3f} {r[2]:7.3f} {r[3]:7.3f} {r[4]:8.2f} {r[5]:9.2f} {r[6]:8.0f}")
    print()
    print(f"Right panel: G = 50, n = {n_right}, rho = {rho_right}, binary treatment, B = {B} Webb bootstrap draws")
    print(f"{'treated':>8} {'CR1 t(49)':>10} {'WCR boot':>9} {'classical':>10}")
    for r in right:
        print(f"{int(r[0]):8d} {r[1]:10.3f} {r[2]:9.3f} {r[3]:10.3f}")


main()

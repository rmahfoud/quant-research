# Weak instruments: when the first stage is weak, instrumental variables
# reproduces the bias it was meant to remove, and its t-test lies.
#
# y = beta * x + u,  x = pi * z + v,  corr(u, v) = 0.8,  beta = 0,  n = 500.
# The strength of the instrument is set through the concentration parameter
# mu^2 = n pi^2 / var(v), and the expected first-stage F statistic is 1 + mu^2.
#
#   Left  — quantiles of the just-identified 2SLS estimate against instrument
#           strength. As the first stage weakens the median slides toward the
#           OLS estimate and the spread explodes (just-identified 2SLS has no
#           finite mean, so medians and percentiles are the honest summary).
#   Right — false rejection rates of the nominal 5% 2SLS t-test, of the same
#           test in only those samples whose first-stage F clears 10 (what a
#           literature that screens on F reports), and of the Anderson-Rubin
#           test, which is valid at any instrument strength.
#
# Run standalone:  uv run --no-project --with matplotlib,numpy python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "em_weak_iv"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

INK = "#10171B"
MUTED = "#58666E"
TEAL = "#0B6E75"
RUST = "#A8452B"
GREY = "#8A979D"

N = 500
RHO = 0.8
TRIALS = 20000
CHUNK = 1000
EXPECTED_F = [1.5, 2, 3, 5, 10, 20, 50, 100]


def simulate(mu2: float, rng: np.random.Generator) -> dict[str, np.ndarray]:
    pi = np.sqrt(mu2 / N)
    out: dict[str, list[np.ndarray]] = {k: [] for k in ("iv", "ols", "t_iv", "t_ar", "F")}
    for start in range(0, TRIALS, CHUNK):
        m = min(CHUNK, TRIALS - start)
        z = rng.standard_normal((m, N))
        v = rng.standard_normal((m, N))
        u = RHO * v + np.sqrt(1 - RHO**2) * rng.standard_normal((m, N))
        x = pi * z + v
        y = u

        zc = z - z.mean(axis=1, keepdims=True)
        xc = x - x.mean(axis=1, keepdims=True)
        yc = y - y.mean(axis=1, keepdims=True)
        szz = (zc * zc).sum(axis=1)
        szx = (zc * xc).sum(axis=1)
        szy = (zc * yc).sum(axis=1)
        sxx = (xc * xc).sum(axis=1)

        b_iv = szy / szx
        e_iv = yc - b_iv[:, None] * xc
        se_iv = np.sqrt((e_iv * e_iv).sum(axis=1) / (N - 2) * szz / szx**2)

        g = szy / szz  # reduced form: y on z, which is the AR regression at beta0 = 0
        e_rf = yc - g[:, None] * zc
        t_ar = g / np.sqrt((e_rf * e_rf).sum(axis=1) / (N - 2) / szz)

        p = szx / szz
        e_fs = xc - p[:, None] * zc
        F = p**2 / ((e_fs * e_fs).sum(axis=1) / (N - 2) / szz)

        out["iv"].append(b_iv)
        out["ols"].append((xc * yc).sum(axis=1) / sxx)
        out["t_iv"].append(b_iv / se_iv)
        out["t_ar"].append(t_ar)
        out["F"].append(F)
    return {k: np.concatenate(v) for k, v in out.items()}


def main() -> None:
    rng = np.random.default_rng(20260913)

    results = {}
    for ef in EXPECTED_F:
        results[ef] = simulate(ef - 1.0, rng)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.6, 3.9))

    efs = np.array(EXPECTED_F)
    q = np.array([np.percentile(results[ef]["iv"], [10, 25, 50, 75, 90]) for ef in EXPECTED_F])
    ols_med = np.array([np.median(results[ef]["ols"]) for ef in EXPECTED_F])
    axL.fill_between(efs, q[:, 0], q[:, 4], color=TEAL, alpha=0.15, lw=0, label="2SLS, 10th–90th pct")
    axL.fill_between(efs, q[:, 1], q[:, 3], color=TEAL, alpha=0.35, lw=0, label="2SLS, 25th–75th pct")
    axL.plot(efs, q[:, 2], "o-", color=TEAL, lw=2.0, ms=4.5, label="2SLS, median")
    axL.plot(efs, ols_med, "--", color=RUST, lw=1.8, label="OLS, median")
    axL.axhline(0.0, color=GREY, lw=1.0, ls=":")
    axL.set_xscale("log")
    axL.set_xticks(EXPECTED_F)
    axL.set_xticklabels([f"{e:g}" for e in EXPECTED_F])
    axL.set_ylim(-1.6, 1.6)
    axL.set_xlabel("expected first-stage F", fontsize=10, color=MUTED)
    axL.set_ylabel("estimate of β (dotted: true β = 0)", fontsize=10, color=MUTED)
    axL.set_title("A weak first stage drags IV toward OLS", fontsize=11, color=INK, loc="left", pad=8)
    axL.legend(frameon=False, fontsize=9, loc="lower right", ncol=1)

    rej_iv = np.array([np.mean(np.abs(results[ef]["t_iv"]) > 1.96) for ef in EXPECTED_F])
    rej_ar = np.array([np.mean(np.abs(results[ef]["t_ar"]) > 1.96) for ef in EXPECTED_F])
    rej_screened = np.array(
        [np.mean(np.abs(results[ef]["t_iv"][results[ef]["F"] > 10]) > 1.96) for ef in EXPECTED_F]
    )
    axR.axhline(0.05, color=GREY, lw=1.0, ls=":")
    axR.axvline(10, color=GREY, lw=0.8, ls="--")
    axR.plot(efs, rej_screened, "^--", color=INK, lw=1.6, ms=4.5, label="2SLS t-test, reported only if F > 10")
    axR.plot(efs, rej_iv, "o-", color=RUST, lw=2.0, ms=4.5, label="2SLS t-test")
    axR.plot(efs, rej_ar, "s-", color=TEAL, lw=2.0, ms=4.5, label="Anderson–Rubin test")
    axR.set_xscale("log")
    axR.set_xticks(EXPECTED_F)
    axR.set_xticklabels([f"{e:g}" for e in EXPECTED_F])
    axR.set_ylim(0, 1.0)
    axR.text(10.6, 0.93, "F = 10", fontsize=9, color=MUTED)
    axR.text(12, 0.003, "nominal 5%", fontsize=9, color=MUTED, va="bottom")
    axR.set_xlabel("expected first-stage F", fontsize=10, color=MUTED)
    axR.set_ylabel("false rejection rate", fontsize=10, color=MUTED)
    axR.set_title("…and its t-test rejects a true null", fontsize=11, color=INK, loc="left", pad=8)
    axR.legend(frameon=False, fontsize=9, loc="upper right", bbox_to_anchor=(1.0, 0.86))

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

    print(f"n = {N}, corr(u, v) = {RHO}, true beta = 0, {TRIALS} trials per row")
    print(
        f"{'E[F]':>6} {'med F':>7} {'P(F>10)':>8} {'med 2SLS':>9} {'med OLS':>8} {'bias/OLS':>9}"
        f" {'rej t':>7} {'rej AR':>7} {'rej t|F>10':>11}"
    )
    for ef in EXPECTED_F:
        r = results[ef]
        big = r["F"] > 10
        cond = np.mean(np.abs(r["t_iv"][big]) > 1.96) if big.any() else float("nan")
        print(
            f"{ef:6g} {np.median(r['F']):7.2f} {np.mean(big):8.3f} {np.median(r['iv']):9.3f} {np.median(r['ols']):8.3f}"
            f" {np.median(r['iv']) / np.median(r['ols']):9.2f} {np.mean(np.abs(r['t_iv']) > 1.96):7.3f}"
            f" {np.mean(np.abs(r['t_ar']) > 1.96):7.3f} {cond:11.3f}"
        )


main()

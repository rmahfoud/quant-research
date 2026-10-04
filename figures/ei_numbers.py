# Prints the worked numbers in "Edge as Information" that have no figure of their
# own: the IC and Sharpe conversion tables, the information accounting, signal
# combination, effective breadth, the track-record probabilities, the multiple-
# testing evidence bar, the annualisation correction and the noise in Sortino and
# Calmar ratios. Every simulation is seeded.
#
# Run standalone:  uv run --no-project --with matplotlib python <path>

import math
from statistics import NormalDist

import numpy as np

PHI = NormalDist().cdf
Z = NormalDist().inv_cdf
LN2 = math.log(2)


def bits(ic: float) -> float:
    return -0.5 * math.log2(1 - ic * ic)


def ic_table() -> None:
    print("== IC conversions")
    print(
        f"{'IC':>6}{'hit':>8}{'R2':>9}{'SNR':>9}{'bits/bet':>10}{'bets/bit':>10}"
        + "".join(f"{f'IR@{b}':>9}" for b in (12, 52, 250, 1000, 6000))
    )
    for ic in (0.01, 0.02, 0.03, 0.05, 0.10, 0.15, 0.20, 0.30):
        hit = 0.5 + math.asin(ic) / math.pi
        snr = ic * ic / (1 - ic * ic)
        b = bits(ic)
        irs = "".join(f"{ic * math.sqrt(br):9.2f}" for br in (12, 52, 250, 1000, 6000))
        print(f"{ic:6.2f}{hit:8.1%}{ic * ic:9.4f}{snr:9.4f}{b:10.5f}{1 / b:10.0f}{irs}")


def sharpe_table(rng: np.random.Generator) -> None:
    print("== Sharpe conversions (normal iid; 252 days)")
    print(
        f"{'SR':>5}{'lose day':>10}{'lose mo':>9}{'lose yr':>9}{'lose 5y':>9}{'yrs t=2':>9}"
        f"{'nats/yr':>9}{'bits/yr':>9}{'E[MDD10]':>10}{'P(MDD>2s)':>11}"
    )
    days = 252 * 10
    paths = 4000
    shocks = rng.standard_normal((paths, days)) / math.sqrt(252)
    for sr in (0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0):
        logw = np.cumsum(sr / 252 + shocks, axis=1)
        peak = np.maximum.accumulate(np.concatenate([np.zeros((paths, 1)), logw], axis=1), axis=1)[:, 1:]
        mdd = (peak - logw).max(axis=1)
        print(
            f"{sr:5.2f}{PHI(-sr / math.sqrt(252)):10.1%}{PHI(-sr / math.sqrt(12)):9.1%}{PHI(-sr):9.1%}"
            f"{PHI(-sr * math.sqrt(5)):9.1%}{4 / sr**2:9.1f}{sr * sr / 2:9.3f}{sr * sr / (2 * LN2):9.3f}"
            f"{mdd.mean():10.2f}{np.mean(mdd > 2):11.1%}"
        )
    print("  (E[MDD10] = expected maximum drawdown over ten years, in units of annual volatility)")


def kelly_vs_information() -> None:
    print("== Kelly growth from a Gaussian signal vs mutual information (nats per bet)")
    for ic in (0.05, 0.10, 0.20, 0.30, 0.50):
        growth = ic * ic / (2 * (1 - ic * ic))
        info = -0.5 * math.log(1 - ic * ic)
        print(f"  IC {ic:.2f}: growth {growth:.6f}  information {info:.6f}  ratio {growth / info:.4f}")
    p = 0.6
    h = -(p * math.log2(p) + (1 - p) * math.log2(1 - p))
    growth = 1 + p * math.log2(p) + (1 - p) * math.log2(1 - p)
    print(
        f"  Horse race, two horses at fair 2-for-1 odds, tip right 60%: growth {growth:.4f} bits/race,"
        f" information 1 - H(0.6) = {1 - h:.4f} bits; Gaussian formula with IC = 0.2: {bits(0.2):.4f} bits"
    )


def accounting() -> None:
    print("== Information accounting: IR^2/2 = breadth x IC^2/2 (nats a year)")
    for ic, br in ((0.05, 12), (0.05, 600), (0.05, 6000), (0.02, 6000), (0.10, 250)):
        ir = ic * math.sqrt(br)
        print(
            f"  IC {ic:.2f}, breadth {br:5d}: IR {ir:5.2f}  nats/yr {ir * ir / 2:6.3f}"
            f"  bits/yr {ir * ir / (2 * LN2):6.3f}  per-bet nats {ic * ic / 2:.5f}  years to t=2 {4 / ir**2:6.1f}"
        )
    print("  Uncorrelated strategies combine in squares:")
    for srs in ((0.5, 0.5), (0.5, 0.5, 0.5), (1.0, 0.3), (1.0, 0.5)):
        print(f"    {srs} -> {math.sqrt(sum(s * s for s in srs)):.3f}")
    print("  n equal-Sharpe strategies of Sharpe 0.5 with pairwise correlation rho:")
    for n in (2, 5, 10, 50):
        cells = "  ".join(f"rho {r:.1f}: {0.5 * math.sqrt(n / (1 + (n - 1) * r)):.2f}" for r in (0.0, 0.1, 0.3, 0.5))
        print(f"    n={n:3d}  {cells}")
    print("  Campbell-Thompson: timing a market of annual Sharpe 0.4 with monthly predictive R^2:")
    srm = 0.4 / math.sqrt(12)
    for r2 in (0.0, 0.0025, 0.005, 0.01, 0.02):
        srs = math.sqrt((srm**2 + r2) / (1 - r2)) * math.sqrt(12)
        print(f"    R2 {r2:.4f} -> annual Sharpe {srs:.3f}  (IC = {math.sqrt(r2):.3f})")


def combination() -> None:
    print("== Combining two signals: IC_c^2 = (a^2 + b^2 - 2 rho a b) / (1 - rho^2)")
    for a, b, rho in (
        (0.04, 0.04, 0.0),
        (0.04, 0.04, 0.3),
        (0.04, 0.04, 0.5),
        (0.04, 0.04, 0.8),
        (0.04, 0.02, 0.5),
        (0.04, 0.0, 0.5),
        (0.04, 0.0, 0.8),
    ):
        c = math.sqrt((a * a + b * b - 2 * rho * a * b) / (1 - rho * rho))
        if b == 0:
            wa, wb = 1.0, -rho
        else:
            inv = np.linalg.inv(np.array([[1, rho], [rho, 1]]))
            wa, wb = inv @ np.array([a, b])
            wa, wb = 1.0, wb / wa
        print(f"  IC {a:.2f} & {b:.2f}, corr {rho:.1f}: combined IC {c:.4f}  weights 1 : {wb:+.2f}")


def breadth() -> None:
    print("== Effective breadth N / (1 + (N - 1) rho), N = 500")
    for rho in (0.0, 0.002, 0.005, 0.01, 0.02, 0.05, 0.10):
        print(f"  rho {rho:.3f}: N_eff {500 / (1 + 499 * rho):7.1f}")
    print("  IC that varies over time: equivalent per-period breadth 1 / (sd^2 + 1/N), N = 500")
    for sd in (0.0, 0.03, 0.05, 0.08, 0.10, 0.15):
        eq = 1 / (sd * sd + 1 / 500)
        print(
            f"  sd(IC) {sd:.2f}: per-period breadth {eq:6.1f}  annual IR at IC 0.04 {0.04 * math.sqrt(12 * eq):.2f}"
            f"  ceiling {('inf' if sd == 0 else f'{0.04 * math.sqrt(12) / sd:.2f}')}"
        )


def transfer() -> None:
    print("== Transfer coefficient: share of information kept = TC^2")
    for tc in (1.0, 0.9, 0.8, 0.6, 0.5, 0.4, 0.3):
        print(f"  TC {tc:.1f}: kept {tc * tc:5.0%}  IR from 1.5 -> {1.5 * tc:.2f}")


def alpha_rule() -> None:
    print("== alpha = volatility x IC x score (monthly horizon)")
    vol = 0.25 / math.sqrt(12)
    for ic in (0.03, 0.05):
        for z in (1.0, 2.0):
            print(
                f"  residual vol 25%/yr ({vol:.2%}/mo), IC {ic:.2f}, score {z:+.1f}: alpha {vol * ic * z:.3%} a month,"
                f" {vol * ic * z * 12:.2%} annualised"
            )


def track_records() -> None:
    print("== Track records")
    for ir in (0.3, 0.5, 1.0):
        cells = "  ".join(f"{t}y: {PHI(-ir * math.sqrt(t)):5.1%}" for t in (1, 3, 5, 10))
        print(f"  true IR {ir:.1f}, P(negative active return over horizon): {cells}")
    cells = "  ".join(f"{t}y: {1 - PHI(0.5 * math.sqrt(t)):5.1%}" for t in (1, 3, 5, 10))
    print(f"  zero skill, P(measured IR > 0.5): {cells}")
    cells = "  ".join(f"{t}y: {1 - PHI(1.0 * math.sqrt(t)):5.1%}" for t in (1, 3, 5, 10))
    print(f"  zero skill, P(measured IR > 1.0): {cells}")
    for sr, years in ((1.0, 10), (0.5, 10), (1.0, 3)):
        print(
            f"  SR {sr} over {years}y: 95% range {sr - 1.96 / math.sqrt(years):+.2f} to {sr + 1.96 / math.sqrt(years):+.2f}"
        )
    print(
        "  Standard error of annual Sharpe 1.0 over 10 years: from 10 annual returns"
        f" {math.sqrt((1 + 0.5) / 10):.3f}; from monthly {math.sqrt((1 + (1 / math.sqrt(12)) ** 2 / 2) / 120) * math.sqrt(12):.3f};"
        f" from daily {math.sqrt((1 + (1 / math.sqrt(252)) ** 2 / 2) / 2520) * math.sqrt(252):.3f}"
    )


def multiple_testing() -> None:
    print("== Multiple testing: Bonferroni bar and the evidence it demands")
    prev = None
    for k in (1, 2, 4, 10, 100, 1000, 10000):
        t = Z(1 - 0.025 / k)
        ev = t * t / 2
        step = "" if prev is None else f"  (+{ev - prev:.2f} nats from previous)"
        print(f"  K {k:6d}: t {t:.2f}  evidence {ev:.2f} nats = {ev / LN2:.2f} bits{step}")
        prev = ev


def annualisation() -> None:
    print("== Annualising a monthly Sharpe with AR(1) autocorrelation rho (Lo 2002)")
    q = 12
    for rho in (-0.1, 0.0, 0.1, 0.2, 0.3, 0.4):
        eta = q / math.sqrt(q + 2 * sum((q - k) * rho**k for k in range(1, q)))
        print(
            f"  rho {rho:+.1f}: multiplier {eta:5.2f} vs sqrt(12) = {math.sqrt(12):.2f}"
            f"  -> overstatement {math.sqrt(12) / eta - 1:+.0%}"
        )


def zoo_noise(rng: np.random.Generator) -> None:
    print("== Noise in ratios over 3 years of daily data, true Sharpe s, vol 10%")
    days = 252 * 3
    paths = 4000
    for s in (0.5, 1.0):
        mu, sig = s * 0.10, 0.10
        r = mu / 252 + sig / math.sqrt(252) * rng.standard_normal((paths, days))
        sharpe = r.mean(axis=1) / r.std(axis=1, ddof=1) * math.sqrt(252)
        down = np.sqrt(np.mean(np.minimum(r, 0) ** 2, axis=1))
        sortino = r.mean(axis=1) / down * math.sqrt(252)
        logw = np.cumsum(np.log1p(r), axis=1)
        peak = np.maximum.accumulate(np.concatenate([np.zeros((paths, 1)), logw], axis=1), axis=1)[:, 1:]
        mdd = 1 - np.exp(-(peak - logw).max(axis=1))
        calmar = (np.exp(logw[:, -1] / 3) - 1) / mdd
        for name, x in (("Sharpe", sharpe), ("Sortino", sortino), ("Calmar", calmar)):
            q10, q50, q90 = np.quantile(x, [0.1, 0.5, 0.9])
            print(
                f"  s {s:.1f} {name:8s} median {q50:6.2f}  10-90% {q10:6.2f} to {q90:6.2f}"
                f"  relative spread {(q90 - q10) / q50:5.2f}"
            )


def worked_instance() -> None:
    print("== Worked instance (section 1.4)")
    ic, n = 0.04, 500
    print(f"  per-bet information {bits(ic):.5f} bits; hit rate {0.5 + math.asin(ic) / math.pi:.1%}")
    print(f"  promised IR {ic * math.sqrt(12 * n):.2f}")
    a = 0.04 * 0.6 * 0.9
    print(f"  IC after TC 0.6 and delay 0.9 if breadth were real: {ic * 0.6 * 0.9 * math.sqrt(12 * n):.2f}")
    print(f"  effective IC per position after TC and delay {a:.4f}")


def main() -> None:
    rng = np.random.default_rng(20261005)
    ic_table()
    sharpe_table(rng)
    kelly_vs_information()
    accounting()
    combination()
    breadth()
    transfer()
    alpha_rule()
    track_records()
    multiple_testing()
    annualisation()
    zoo_noise(rng)
    worked_instance()


main()

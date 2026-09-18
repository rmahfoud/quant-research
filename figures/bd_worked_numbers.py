# Worked numbers for "Bonds and Bond Markets" that have no figure of their own.
# Each block prints one table quoted in the text, labelled by section. The
# figure scripts (bd_*.py) print the numbers that go with their figures.
#
# Run standalone:  uv run --no-project --with numpy python <path>

import numpy as np

FREQ = 2


def cash_flows(maturity: float, coupon: float) -> tuple[np.ndarray, np.ndarray]:
    """Times (years) and amounts of a semi-annual bullet bond, 100 face."""
    n = int(round(maturity * FREQ))
    t = np.arange(1, n + 1) / FREQ
    cf = np.full(n, 100.0 * coupon / FREQ)
    cf[-1] += 100.0
    return t, cf


def price(y: float, maturity: float, coupon: float) -> float:
    t, cf = cash_flows(maturity, coupon)
    return float((cf * (1.0 + y / FREQ) ** (-t * FREQ)).sum())


def ytm(p: float, maturity: float, coupon: float) -> float:
    lo, hi = -0.05, 0.50
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if price(mid, maturity, coupon) > p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def macaulay(y: float, maturity: float, coupon: float) -> float:
    t, cf = cash_flows(maturity, coupon)
    pv = cf * (1.0 + y / FREQ) ** (-t * FREQ)
    return float((pv * t).sum() / pv.sum())


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def curve_equivalence() -> None:
    section("§6.2 spot, forward and par: one curve, three encodings")
    z = {1: 0.0300, 2: 0.0340, 3: 0.0370}
    disc = {t: (1 + z[t]) ** (-t) for t in z}
    par = {}
    for t in z:
        par[t] = (1 - disc[t]) / sum(disc[k] for k in range(1, t + 1))
    for t in z:
        fwd = (1 + z[t]) ** t / (1 + z[t - 1]) ** (t - 1) - 1 if t > 1 else z[1]
        print(f"  year {t}: spot {z[t] * 100:.3f}%  Z {disc[t]:.5f}  "
              f"forward {fwd * 100:.3f}%  par {par[t] * 100:.3f}%")
    cf = {1: 5.0, 2: 5.0, 3: 105.0}
    p = sum(cf[t] * disc[t] for t in cf)
    lo, hi = 0.0, 0.2
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if sum(cf[t] * (1 + mid) ** (-t) for t in cf) > p:
            lo = mid
        else:
            hi = mid
    print(f"  3-year 5% annual-pay bond off this curve: price {p:.3f}, "
          f"yield to maturity {0.5 * (lo + hi) * 100:.3f}%")


def reinvestment() -> None:
    section("§6.4 realised return depends on the reinvestment rate")
    for mat in (10, 30):
        print(f"  {mat}-year 4% bond bought at par:")
        for r in (0.0, 0.02, 0.04, 0.06, 0.08):
            n, c = mat * FREQ, 100 * 0.04 / FREQ
            fv = c * (((1 + r / FREQ) ** n - 1) / (r / FREQ)) if r > 0 else c * n
            wealth = fv + 100.0
            print(f"    reinvest at {r * 100:3.0f}%: terminal wealth {wealth:7.2f}, "
                  f"realised {((wealth / 100) ** (1 / mat) - 1) * 100:5.2f}% a year")
        n, c = mat * FREQ, 100 * 0.04 / FREQ
        wealth = c * (((1.02) ** n - 1) / 0.02) + 100.0
        coupons = c * n
        ioi = wealth - 100.0 - coupons
        print(f"    at 4%: coupons {coupons:.2f}, interest on interest {ioi:.2f} "
              f"= {ioi / (wealth - 100.0):.0%} of total income")


def duration_table() -> None:
    section("§7.1-7.2 duration, DV01 and convexity, 4% coupon bonds at par")
    for mat in (2, 10, 30):
        d_mac = macaulay(0.04, mat, 0.04)
        d_mod = d_mac / (1 + 0.04 / FREQ)
        h = 1e-5
        p0 = price(0.04, mat, 0.04)
        cvx = (price(0.04 + h, mat, 0.04) - 2 * p0 + price(0.04 - h, mat, 0.04)) / h**2 / p0
        print(f"  {mat:>2}-year: Macaulay {d_mac:6.2f}  modified {d_mod:6.2f}  "
              f"DV01 per $10m ${d_mod * 1e7 * 1e-4:,.0f}  convexity {cvx:6.1f}")


def immunisation() -> None:
    section("§7.3 terminal wealth per 100 at each horizon, yields shocked at once")
    mat = 10.0
    d = macaulay(0.04, mat, 0.04)
    t, cf = cash_flows(mat, 0.04)
    ys = (0.02, 0.03, 0.04, 0.05, 0.06)
    for horizon in (5.0, 7.0, d, 9.0, 10.0):
        row = []
        for y in ys:
            growth = (1 + y / FREQ) ** ((horizon - t) * FREQ)
            row.append(float((cf * growth).sum()))
        tag = " (= Macaulay duration)" if abs(horizon - d) < 1e-9 else ""
        print(f"  {horizon:5.2f}y{tag}: " + "  ".join(f"{v:7.2f}" for v in row)
              + f"   range {max(row) - min(row):5.2f}")


def zspread() -> None:
    section("§8.2 identical Z-spreads, different nominal spreads, steep curve")

    def zero(t: np.ndarray) -> np.ndarray:
        return 0.020 + 0.045 * (1 - np.exp(-np.asarray(t, dtype=float) / 8.0))

    def price_at_spread(mat: float, cpn: float, s: float) -> float:
        t, cf = cash_flows(mat, cpn)
        return float((cf * (1 + (zero(t) + s) / FREQ) ** (-t * FREQ)).sum())

    for mat, cpn in ((30, 0.08), (30, 0.01), (10, 0.08), (10, 0.01)):
        p = price_at_spread(mat, cpn, 0.01)
        t, _ = cash_flows(mat, 0.0)
        disc = (1 + zero(t) / FREQ) ** (-t * FREQ)
        gov_par = (1 - disc[-1]) / disc.sum() * FREQ
        nominal = ytm(p, mat, cpn) - gov_par
        print(f"  {mat}-year {cpn * 100:.0f}% coupon: price {p:7.2f}, Z-spread 100.0bp, "
              f"nominal {nominal * 1e4:6.1f}bp, gap {(nominal - 0.01) * 1e4:+5.1f}bp")


def credit_triangle() -> None:
    section("§9.2 spread = hazard x (1 - recovery)")
    for s, rec in ((0.01, 0.4), (0.01, 0.2), (0.01, 0.7), (0.05, 0.4), (0.05, 0.2)):
        lam = s / (1 - rec)
        print(f"  {s * 1e4:4.0f}bp, recovery {rec:.0%}: hazard {lam * 100:5.2f}%/yr, "
              f"5-year default probability {1 - np.exp(-5 * lam):5.1%}")


def fx_share() -> None:
    section("§15.4 how much of an unhedged foreign bond's risk is currency")
    fx = 0.085
    for label, mat, yvol in (("2-year", 2, 0.008), ("10-year", 10, 0.009), ("30-year", 30, 0.009)):
        d_mod = macaulay(0.04, mat, 0.04) / (1 + 0.04 / FREQ)
        bond = d_mod * yvol
        print(f"  {label:>8}: bond vol {bond * 100:5.2f}%, unhedged {np.hypot(bond, fx) * 100:5.2f}%, "
              f"currency share of variance {fx**2 / (bond**2 + fx**2):.0%}")


def duration_targeting() -> None:
    section("§17.3 constant-duration portfolio: annualised return by horizon")
    mat, y0 = 7.0, 0.04
    d_mac = macaulay(y0, mat, y0)
    print(f"  rolls a {mat:.0f}-year par bond each year: Macaulay duration {d_mac:.2f}, "
          f"2D-1 = {2 * d_mac - 1:.1f} years; starting yield {((1 + y0 / FREQ) ** FREQ - 1) * 100:.2f}% effective")

    def run(path: np.ndarray) -> np.ndarray:
        """path[k] is the yield in force during year k+1; moves happen at the start of a year."""
        wealth, held_coupon, out = 1.0, y0, []
        for y in path:
            wealth *= price(y, mat, held_coupon) / 100.0   # the held bond reprices at once
            wealth *= (1 + y / FREQ) ** FREQ                # then earns the new yield all year
            held_coupon = y                                 # roll into a new par bond
            out.append(wealth)
        return np.array(out)

    horizons = (3, 6, 11, 15)
    h_max = max(horizons)
    paths = {
        "+300bp at once, then flat": np.full(h_max, y0 + 0.03),
        "-200bp at once, then flat": np.full(h_max, y0 - 0.02),
        "rising 25bp every year": y0 + 0.0025 * np.arange(1, h_max + 1),
        "falling 25bp every year": y0 - 0.0025 * np.arange(1, h_max + 1),
    }
    for label, path in paths.items():
        w = run(path)
        cells = "  ".join(f"H={h:>2}: {(w[h - 1] ** (1 / h) - 1) * 100:5.2f}%" for h in horizons)
        print(f"  {label:<28} {cells}")

    rng = np.random.default_rng(20260917)
    n_paths, vol = 20000, 0.008
    shocks = rng.normal(0.0, vol, size=(n_paths, 20))
    ys = np.maximum(y0 + np.cumsum(shocks, axis=1), 0.0)
    ann = np.empty((n_paths, 20))
    for i in range(n_paths):
        w = run(ys[i])
        ann[i] = w ** (1 / np.arange(1, 21)) - 1
    print(f"  random walk, {vol * 1e4:.0f}bp a year, floored at zero, {n_paths} paths:")
    for h in horizons:
        a = ann[:, h - 1]
        print(f"    H={h:>2}: mean {a.mean() * 100:5.2f}%  sd {a.std() * 100:4.2f}%  "
              f"5th-95th {np.percentile(a, 5) * 100:5.2f}% to {np.percentile(a, 95) * 100:5.2f}%")
    sd = ann.std(axis=0)
    best = int(np.argmin(sd)) + 1
    print(f"    dispersion is smallest at H={best} years (sd {sd[best - 1] * 100:.2f}%)")
    print("    sd by horizon: " + " ".join(f"{h + 1}:{sd[h] * 100:.2f}" for h in range(20)))


curve_equivalence()
reinvestment()
duration_table()
immunisation()
zspread()
credit_triangle()
fx_share()
duration_targeting()

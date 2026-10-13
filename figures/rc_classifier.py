# What a walk-forward classifier sees through three bear markets, for
# regime_classification.md: the predicted probability of the ex-post ±20% bear
# label and of next month's volatility landing in the top fifth, against the
# ex-post label and the rule's own real-time confirmation. Models and data are
# built in rc_common.py, which also prints the scores the chapter quotes.
#
# Run standalone:  uv run --no-project --with matplotlib python <path>

import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"
matplotlib.rcParams["svg.hashsalt"] = "rc-classifier"
matplotlib.rcParams["font.family"] = ["Helvetica", "Arial", "DejaVu Sans"]

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from rc_common import (
    GREY,
    INK,
    MUTED,
    RUST,
    TEAL,
    classifier_results,
    labels,
    load_or_exit,
    lt_labels,
    market,
    runs,
    to_datetime64,
)

WINDOWS = [
    (20070101, 20091231, "2007-2009: the slow bear, a bear-market rally, and the second leg"),
    (20190701, 20230630, "2019-2023: the fast bear of 2020 and the slow one of 2022"),
]
MODEL = "price + cross-asset"


def main() -> None:
    load_or_exit(Path(__file__))
    m = market()
    dates = m["dates"]
    res = classifier_results()
    y_bear, _, p_bear = res["Bear, ±20% rule, ex post"]
    _, _, p_vol = res["Next-month volatility, top fifth"]
    confirmed = lt_labels(m["P"])["rt"]
    bear = np.nan_to_num(labels()["Bear, ±20% rule, ex post"]).astype(int)

    fig, axes = plt.subplots(2, 1, figsize=(7.0, 6.2), gridspec_kw={"hspace": 0.48})
    for ax, (a, b, title) in zip(axes, WINDOWS, strict=True):
        i0, i1 = np.searchsorted(dates, a), np.searchsorted(dates, b, side="right")
        t = to_datetime64(dates[i0:i1])
        for s, e in runs(bear[i0:i1]):
            ax.axvspan(t[s], t[min(e + 1, len(t) - 1)], color=RUST, alpha=0.16, linewidth=0)
        ax.step(
            t,
            confirmed[i0:i1],
            where="post",
            color=GREY,
            linewidth=1.1,
            linestyle="--",
            label="±20% rule, as confirmed",
        )
        ax.plot(t, p_vol[MODEL][i0:i1], color=TEAL, linewidth=0.8, label="P(next-month volatility in top fifth)")
        ax.plot(t, p_bear[MODEL][i0:i1], color=INK, linewidth=1.2, label="P(ex-post bear market)")
        ax.axhline(0.5, color=GREY, linewidth=0.6, linestyle=":")
        ax.set_ylim(-0.03, 1.05)
        ax.set_ylabel("probability", fontsize=9.5, color=MUTED)
        ax.set_title(title, fontsize=10.0, color=INK, loc="left", pad=8)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax.tick_params(labelsize=9.0, colors=MUTED, length=3)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GREY)
    axes[1].legend(
        fontsize=8.8,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.14),
        ncol=2,
        frameon=False,
        labelcolor=MUTED,
        handlelength=1.8,
    )

    out = Path(__file__).with_suffix(".svg")
    fig.savefig(out, transparent=True, bbox_inches="tight", metadata={"Date": None})
    print(f"wrote {out.name}")


if __name__ == "__main__":
    main()

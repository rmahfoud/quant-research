#!/usr/bin/env python3
"""
Draws the 1200×630 share card (Open Graph image) for documents, plus a site default.

The card is what Slack, LinkedIn, X and iMessage show when a document's URL is
pasted. Crawlers fetch it as a separate request and ignore data: URIs, so it is a
real file under docs/og/, committed alongside the rendered page, and
inject_seo.py points og:image at it.

The headline is the document's front-matter `pagetitle` and the tagline its
`###` subtitle, so editing either and re-rendering redraws the card. Fonts are
loaded from matplotlib's bundled files rather than the system's, and a card is
only rewritten when its bytes change.

Usage (run by render_docs.sh under `uv run --with matplotlib`):
    og_cards.py <quant-research-dir> --site-url <url> <doc> [<doc> ...]
"""

from __future__ import annotations

import argparse
import hashlib
import io
import pathlib
import random
import re
import sys
from itertools import combinations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_agg import RendererAgg  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402

WIDTH, HEIGHT, DPI = 1200, 630, 100
MARGIN = 88
TEXT_WIDTH = WIDTH - 2 * MARGIN

BG = "#f0f3f8"
INK = "#1a2332"
MUTED = "#5a6578"
LINE = "#d5dbe6"
ACCENT = "#0b6e4f"

SITE_NAME = "Quant Research"
SITE_TAGLINE = "Notes on quantitative finance, with the math and the evidence in one place"

FONT_DIR = pathlib.Path(matplotlib.get_data_path()) / "fonts" / "ttf"
SERIF = FONT_DIR / "STIXGeneral.ttf"
SANS = FONT_DIR / "DejaVuSans.ttf"
SANS_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"

# (pixel size, max lines) in order of preference: the largest size that fits.
HEADLINE_FITS = [(76, 2), (70, 2), (64, 2), (58, 2), (52, 2), (52, 3), (46, 3)]
TAGLINE_FITS = [(32, 2), (30, 2), (28, 2), (28, 3), (26, 3)]

# Line-break scoring: a line may not end on a function word ("…Construction and
# the / Covariance…"), and a break after punctuation reads as intended.
WEAK_ENDINGS = {"a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "with"}
WEAK_ENDING_PENALTY = 0.08 * TEXT_WIDTH
PUNCTUATION_BONUS = 0.08 * TEXT_WIDTH

FRONT_MATTER_KEY_RE = re.compile(r"^([A-Za-z_][\w-]*):\s*(.*)$")


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def read_card_text(md: pathlib.Path) -> tuple[str | None, str | None]:
    """(pagetitle, ### subtitle directly under the # title) of a document."""
    lines = md.read_text(encoding="utf-8").splitlines()
    fields: dict[str, str] = {}
    body_start = 0
    if lines and lines[0].strip() == "---":
        for i, raw in enumerate(lines[1:], start=1):
            if raw.strip() in ("---", "..."):
                body_start = i + 1
                break
            m = FRONT_MATTER_KEY_RE.match(raw)
            if m:
                fields[m.group(1)] = unquote(m.group(2).strip())

    subtitle = None
    seen_title = False
    for raw in lines[body_start:]:
        stripped = raw.strip()
        if not stripped:
            continue
        if not seen_title and stripped.startswith("# "):
            seen_title = True
            continue
        if seen_title and stripped.startswith("### "):
            subtitle = re.sub(r"[*_`]", "", stripped[4:]).strip()
        break
    return fields.get("pagetitle") or None, subtitle


def props(font: pathlib.Path, size_px: float) -> FontProperties:
    return FontProperties(fname=font, size=size_px * 72 / DPI)


def measure(renderer: RendererAgg, text: str, prop: FontProperties) -> float:
    width, _, _ = renderer.get_text_width_height_descent(text, prop, ismath=False)
    return width


def wrap(renderer: RendererAgg, text: str, prop: FontProperties) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if current and measure(renderer, trial, prop) > TEXT_WIDTH:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def balance(renderer: RendererAgg, text: str, prop: FontProperties, n_lines: int) -> list[str]:
    """The same number of lines as a greedy wrap, broken to even out their widths."""
    words = text.split()
    best, best_score = [text], float("inf")
    for cuts in combinations(range(1, len(words)), n_lines - 1):
        bounds = (0, *cuts, len(words))
        lines = [" ".join(words[a:b]) for a, b in zip(bounds, bounds[1:], strict=False)]
        widths = [measure(renderer, line, prop) for line in lines]
        if max(widths) > TEXT_WIDTH:
            continue
        score = max(widths)
        for line in lines[:-1]:
            if line.split()[-1].lower() in WEAK_ENDINGS:
                score += WEAK_ENDING_PENALTY
            elif line[-1] in ",;:—–":
                score -= PUNCTUATION_BONUS
        if score < best_score:
            best, best_score = lines, score
    return best


def fit(
    renderer: RendererAgg, text: str, font: pathlib.Path, attempts: list[tuple[int, int]]
) -> tuple[int, list[str], bool]:
    """Largest size whose wrap fits its line budget; else the last attempt, ellipsized."""
    for size, max_lines in attempts:
        prop = props(font, size)
        lines = wrap(renderer, text, prop)
        if len(lines) <= max_lines:
            return size, balance(renderer, text, prop, len(lines)) if len(lines) > 1 else lines, False

    size, max_lines = attempts[-1]
    prop = props(font, size)
    lines = wrap(renderer, text, prop)[:max_lines]
    words = lines[-1].split()
    while len(words) > 1 and measure(renderer, " ".join(words) + "…", prop) > TEXT_WIDTH:
        words.pop()
    lines[-1] = " ".join(words).rstrip(",;:—–-") + "…"
    return size, lines, True


def sparkline(ax: plt.Axes, seed: str) -> None:
    """A faint random walk in the footer, seeded by the slug so each card differs."""
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16], 16))
    steps = 96
    level, levels = 0.0, []
    for _ in range(steps):
        level += rng.gauss(0.04, 1.0)
        levels.append(level)
    lo, hi = min(levels), max(levels)
    top, bottom, left, right = 553, 603, 720, WIDTH - MARGIN
    xs = [left + (right - left) * i / (steps - 1) for i in range(steps)]
    ys = [bottom - (v - lo) / ((hi - lo) or 1.0) * (bottom - top) for v in levels]
    ax.plot(xs, ys, color=ACCENT, alpha=0.45, linewidth=2.0, solid_joinstyle="round", solid_capstyle="round")


def draw_card(headline: str, tagline: str | None, host: str, seed: str) -> tuple[bytes, bool]:
    fig = plt.figure(figsize=(WIDTH / DPI, HEIGHT / DPI), dpi=DPI)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, WIDTH)
    ax.set_ylim(HEIGHT, 0)
    ax.axis("off")
    renderer = fig.canvas.get_renderer()

    ax.add_patch(plt.Rectangle((0, 0), 14, HEIGHT, color=ACCENT, linewidth=0))
    if headline != SITE_NAME:
        ax.text(MARGIN, 96, SITE_NAME.upper(), fontproperties=props(SANS_BOLD, 21), color=ACCENT, va="baseline")

    head_px, head_lines, head_cut = fit(renderer, headline, SERIF, HEADLINE_FITS)
    tag_px, tag_lines, tag_cut = fit(renderer, tagline, SANS, TAGLINE_FITS) if tagline else (0, [], False)

    head_leading, tag_leading, gap = 1.1 * head_px, 1.4 * tag_px, 30 if tag_lines else 0
    head_height = head_leading * (len(head_lines) - 1) + 0.95 * head_px
    tag_height = tag_leading * (len(tag_lines) - 1) + 0.95 * tag_px if tag_lines else 0
    zone_top, zone_bottom = 140, 500
    y = zone_top + (zone_bottom - zone_top - head_height - gap - tag_height) / 2 + 0.72 * head_px

    for line in head_lines:
        ax.text(MARGIN, y, line, fontproperties=props(SERIF, head_px), color=INK, va="baseline")
        y += head_leading
    y += gap - head_leading + 0.72 * tag_px + 0.23 * head_px
    for line in tag_lines:
        ax.text(MARGIN, y, line, fontproperties=props(SANS, tag_px), color=MUTED, va="baseline")
        y += tag_leading

    ax.plot([MARGIN, WIDTH - MARGIN], [530, 530], color=LINE, linewidth=1.5)
    ax.text(MARGIN, 588, host, fontproperties=props(SANS, 22), color=MUTED, va="baseline")
    sparkline(ax, seed)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI, facecolor=BG, metadata={"Software": None})
    plt.close(fig)
    return buf.getvalue(), head_cut or tag_cut


def write_if_changed(path: pathlib.Path, data: bytes) -> bool:
    if path.exists() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("qr_dir", type=pathlib.Path)
    parser.add_argument("--site-url", required=True)
    parser.add_argument("docs", nargs="*")
    args = parser.parse_args()

    out_dir = args.qr_dir / "docs" / "og"
    host = re.sub(r"^https?://", "", args.site_url).rstrip("/")

    jobs: list[tuple[str, str, str | None]] = [("default", SITE_NAME, SITE_TAGLINE)]
    for doc in args.docs:
        headline, tagline = read_card_text(args.qr_dir / f"{doc}.md")
        if not headline:
            print(f"! {doc}: no `pagetitle:` in front matter, so no share card", file=sys.stderr)
            continue
        jobs.append((doc, headline, tagline))

    changed = 0
    for slug, headline, tagline in jobs:
        data, truncated = draw_card(headline, tagline, host, seed=slug)
        if truncated:
            print(f"! {slug}: title or subtitle too long for the card and was cut with …", file=sys.stderr)
        changed += write_if_changed(out_dir / f"{slug}.png", data)

    print(f"✅ share cards: {len(jobs)} drawn, {changed} changed, docs/og/")
    return 0


if __name__ == "__main__":
    sys.exit(main())

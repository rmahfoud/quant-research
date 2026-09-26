# Quant research notes

Markdown notes on quantitative topics, renderable to HTML and PDF.

## License

These notes are dedicated to the public domain under the [CC0 1.0 Universal Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/). The legal text is in [LICENSE](LICENSE).

They were generated in whole or in part with the help of a large language model.

## Prerequisites

From this directory:

```bash
./scripts/setup_dev.sh
```

That installs pandoc, Node (`mermaid-filter`), librsvg (`rsvg-convert`), BasicTeX / texlive, and `uv` (for figure generators and the share cards every HTML render draws).

On macOS after BasicTeX, ensure `/Library/TeX/texbin` is on your `PATH` (or open a new shell — `scripts/render_docs.sh` also adds it when needed).

## Rendering

```bash
./scripts/render_docs.sh <doc|all> [pdf|html|both] [--figures]
```

Examples:

```bash
./scripts/render_docs.sh stochastic_processes
./scripts/render_docs.sh all --figures
```

Output lands in `docs/` (gitignored).

`--figures` regenerates plots under `figures/` before rendering. Those outputs are committed, so this is only needed after editing a generator.

Each document opens with a YAML front-matter block (`pagetitle`, `description`, `keywords`, `author`, `lang`). Pandoc turns it into the page title, meta description and PDF document properties. `scripts/og_cards.py` then draws the document's share card (`docs/og/<doc>.png`, the image a pasted link previews with) from its title and subtitle, and `scripts/inject_seo.py` adds the canonical URL, Open Graph tags, JSON-LD and `docs/sitemap.xml`.

## Documents

Every document opens with an **ELI5 card** — a plain-language summary of the whole
thing, set apart from the body text and linked first in the table of contents.
Styling is shared across documents in `assets/eli5.html` (web) and
`assets/eli5.tex` (print).

| Source | Notes |
|---|---|
| `log_returns.md` | Mermaid diagrams; LaTeX math; ASCII figures |
| `econometrics_foundations.md` | Mermaid diagrams; LaTeX math; ASCII figures; matplotlib-generated SVG figures (`figures/em_*.py`, which also print the simulated numbers quoted in the text) |
| `bond_markets.md` | Mermaid diagrams; LaTeX math; ASCII figures; matplotlib-generated SVG figures (`figures/bd_*.py`, which also print the worked and simulated numbers quoted in the text; `bd_worked_numbers.py` prints the tables that have no figure) |
| `systematic_strategies.md` | Mermaid diagrams; LaTeX math; matplotlib-generated SVG figures (`figures/st_*.py`, which also print the worked and simulated numbers quoted in the text; `st_factor_history.py` downloads the Kenneth French data library when run, pinned to data ending December 2025, and leaves its committed outputs in place when offline) |
| `momentum_deep_dive.md` | Mermaid diagrams; hand-authored SVG figures (`figures/*.svg`) |
| `intraday_momentum.md` | Follow-up chapter to `momentum_deep_dive.md`. Mermaid diagrams; LaTeX math; matplotlib-generated SVG figures (`figures/im_*.py`, which also print the simulated and worked numbers quoted in §3.4, §3.6, §4.8, §6.2 and §7.7) |
| `stochastic_processes.md` | LaTeX math; HTML gets an interactive canvas figure, PDF a static plot |
| `trend_following.md` | Mermaid diagrams; LaTeX math; matplotlib-generated SVG figures (`figures/trend_*.py`) plus the shared `kernel_weights.svg` |
| `market_regimes.md` | Mermaid diagrams; LaTeX math; ASCII figures; matplotlib-generated SVG figures (`figures/regime_*.py`, which also print the simulated tables quoted in the text) plus the shared `purged_split.svg` |
| `dealer_hedging.md` | Mermaid diagrams; LaTeX math; matplotlib-generated SVG figures (`figures/dh_*.py`, which also print the worked and simulated numbers quoted in the text) |
| `implied_volatility.md` | Mermaid diagrams; LaTeX math; matplotlib-generated SVG figures (`figures/iv_*.py`, which also print the worked and simulated numbers quoted in the text) |
| `portfolio_construction.md` | Mermaid diagrams; LaTeX math; matplotlib-generated SVG figures (`figures/pc_*.py`, which also print the simulated numbers quoted in §2.1, §5.5 and §9.8) |

HTML output is a single self-contained file (offline-usable). PDF and HTML may diverge where a document uses format-specific figures.

Published site: [rmahfoud.github.io/quant-research](https://rmahfoud.github.io/quant-research/)

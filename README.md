# Quant research notes

Markdown notes on quantitative topics, renderable to HTML and PDF.

Published site: [rmahfoud.github.io/quant-research](https://rmahfoud.github.io/quant-research/)

## License

These notes are dedicated to the public domain under the [CC0 1.0 Universal Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/). The legal text is in [LICENSE](LICENSE).

They were generated in whole or in part with the help of a large language model.

## Prerequisites

From this directory:

```bash
./scripts/setup_dev.sh
```

That installs pandoc, Node (`mermaid-filter`), librsvg (`rsvg-convert`), BasicTeX / texlive, and `uv` (for figure generators and the share cards every HTML render draws).

On macOS after BasicTeX, ensure `/Library/TeX/texbin` is on your `PATH` (or open a new shell — [`scripts/render_docs.sh`](https://github.com/rmahfoud/quant-research/blob/master/scripts/render_docs.sh) also adds it when needed).

## Rendering

```bash
./scripts/render_docs.sh <doc|all> [pdf|html|both] [--figures]
```

Examples:

```bash
./scripts/render_docs.sh stochastic_processes
./scripts/render_docs.sh all --figures
```

Output lands in `docs/`.

`--figures` regenerates plots under [`figures/`](https://github.com/rmahfoud/quant-research/tree/master/figures) before rendering. Those outputs are committed, so this is only needed after editing a generator.

The whole collection is also published as one EPUB book for e-readers, in chapter order, and linked from the index:

```bash
python3 scripts/render_epub.py [--force]
```

Output lands in `docs/quant_research.epub`. It is rebuilt only when a chapter, the index, a figure or the e-book build itself is newer than it (`--force` rebuilds anyway), and the build is reproducible, so a rebuild from unchanged sources leaves the file byte-identical. Figures are SVG and mermaid diagrams PNG. Equations avoid MathML, which many e-readers (Google Play Books among them) cannot lay out: simple inline math is set as text, so it follows the reader's font and night theme, and the rest becomes SVG drawn by MathJax, as on the site.

Each document opens with a YAML front-matter block (`pagetitle`, `description`, `keywords`, `author`, `lang`). Pandoc turns it into the page title, meta description and PDF document properties. [`scripts/og_cards.py`](https://github.com/rmahfoud/quant-research/blob/master/scripts/og_cards.py) then draws the document's share card (`docs/og/<doc>.png`, the image a pasted link previews with) from its title and subtitle, and [`scripts/inject_seo.py`](https://github.com/rmahfoud/quant-research/blob/master/scripts/inject_seo.py) adds the canonical URL, Open Graph tags, JSON-LD and `docs/sitemap.xml`.

## Documents

Every document opens with an **ELI5 card** — a plain-language summary of the whole
thing, set apart from the body text and linked first in the table of contents.
Styling is shared across documents in [`assets/eli5.html`](https://github.com/rmahfoud/quant-research/blob/master/assets/eli5.html) (web) and
`assets/eli5.tex` (print).

| Chapter | Source | Notes |
|---|---|---|
| 1 | `stochastic_processes.md` | LaTeX math; HTML gets an interactive canvas figure, PDF a static plot |
| 2 | `econometrics_foundations.md` | Mermaid diagrams; LaTeX math; ASCII figures; matplotlib-generated SVG figures ([`figures/em_*.py`](https://github.com/rmahfoud/quant-research/tree/master/figures), which also print the simulated numbers quoted in the text) |
| 3 | `log_returns.md` | Mermaid diagrams; LaTeX math; ASCII figures |
| 4 | `futures_mechanics.md` | Mermaid diagrams; LaTeX math; matplotlib-generated SVG figures from stylised and simulated markets ([`figures/fm_*.py`](https://github.com/rmahfoud/quant-research/tree/master/figures), which also print the simulation readings quoted in §8.4); a tested Python recipe inline in §13.3 |
| 5 | `edge_as_information.md` | Mermaid diagrams; LaTeX math; matplotlib-generated SVG figures from seeded synthetic data ([`figures/ei_*.py`](https://github.com/rmahfoud/quant-research/tree/master/figures), which also print the simulated numbers quoted in the text; [`figures/ei_numbers.py`](https://github.com/rmahfoud/quant-research/blob/master/figures/ei_numbers.py) prints the tables that have no figure) |
| 6 | `momentum_deep_dive.md` | Mermaid diagrams; hand-authored SVG figures ([`figures/*.svg`](https://github.com/rmahfoud/quant-research/tree/master/figures)) |
| 7 | `trend_following.md` | Mermaid diagrams; LaTeX math; matplotlib-generated SVG figures ([`figures/trend_*.py`](https://github.com/rmahfoud/quant-research/tree/master/figures)) plus the shared [`figures/kernel_weights.svg`](https://github.com/rmahfoud/quant-research/blob/master/figures/kernel_weights.svg) |
| 8 | `market_regimes.md` | Mermaid diagrams; LaTeX math; ASCII figures; matplotlib-generated SVG figures ([`figures/regime_*.py`](https://github.com/rmahfoud/quant-research/tree/master/figures), which also print the simulated tables and the worked-example numbers quoted in the text; `regime_hmm_worked.py` downloads Kenneth French daily market data and takes about three minutes) plus the shared [`figures/purged_split.svg`](https://github.com/rmahfoud/quant-research/blob/master/figures/purged_split.svg) |
| 9 | `dealer_hedging.md` | Mermaid diagrams; LaTeX math; matplotlib-generated SVG figures ([`figures/dh_*.py`](https://github.com/rmahfoud/quant-research/tree/master/figures), which also print the worked and simulated numbers quoted in the text) |
| 10 | `implied_volatility.md` | Mermaid diagrams; LaTeX math; matplotlib-generated SVG figures ([`figures/iv_*.py`](https://github.com/rmahfoud/quant-research/tree/master/figures), which also print the worked and simulated numbers quoted in the text) |
| 11 | `intraday_momentum.md` | Follow-up chapter to `momentum_deep_dive.md`. Mermaid diagrams; LaTeX math; matplotlib-generated SVG figures ([`figures/im_*.py`](https://github.com/rmahfoud/quant-research/tree/master/figures), which also print the simulated and worked numbers quoted in §3.4, §3.6, §4.8, §6.2 and §7.7) |
| 12 | `portfolio_construction.md` | Mermaid diagrams; LaTeX math; matplotlib-generated SVG figures ([`figures/pc_*.py`](https://github.com/rmahfoud/quant-research/tree/master/figures), which also print the simulated numbers quoted in §2.1, §5.5 and §9.8) |
| 13 | `value_at_risk.md` | Mermaid diagrams; LaTeX math; matplotlib-generated SVG figures ([`figures/var_*.py`](https://github.com/rmahfoud/quant-research/tree/master/figures), which download daily data from the Kenneth French data library, pinned to data ending December 2025, and leave their committed outputs in place when offline; [`figures/var_common.py`](https://github.com/rmahfoud/quant-research/blob/master/figures/var_common.py) holds the shared estimators and, run directly, prints every backtest, simulation and worked-account number quoted in the text, including the output of the §14 recipe) |
| 14 | `bond_markets.md` | Mermaid diagrams; LaTeX math; ASCII figures; matplotlib-generated SVG figures ([`figures/bd_*.py`](https://github.com/rmahfoud/quant-research/tree/master/figures), which also print the worked and simulated numbers quoted in the text; [`figures/bd_worked_numbers.py`](https://github.com/rmahfoud/quant-research/blob/master/figures/bd_worked_numbers.py) prints the tables that have no figure) |
| 15 | `systematic_strategies.md` | Mermaid diagrams; LaTeX math; matplotlib-generated SVG figures ([`figures/st_*.py`](https://github.com/rmahfoud/quant-research/tree/master/figures), which also print the worked and simulated numbers quoted in the text; [`figures/st_factor_history.py`](https://github.com/rmahfoud/quant-research/blob/master/figures/st_factor_history.py) downloads the Kenneth French data library when run, pinned to data ending December 2025, and leaves its committed outputs in place when offline) |

HTML output is a single self-contained file (offline-usable). PDF and HTML may diverge where a document uses format-specific figures.

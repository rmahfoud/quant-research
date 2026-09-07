# Quant research notes

Markdown notes on quantitative topics, renderable to HTML and PDF.

## Prerequisites

From this directory (independent of the Phoenix parent project):

```bash
./scripts/setup_dev.sh
```

That installs pandoc, Node (`mermaid-filter`), librsvg (`rsvg-convert`), BasicTeX / texlive, and `uv` (for figure generators).

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

## Documents

| Source | Notes |
|---|---|
| `log_returns.md` | Mermaid diagrams; LaTeX math; ASCII figures |
| `momentum_deep_dive.md` | Mermaid diagrams; hand-authored SVG figures (`figures/*.svg`) |
| `stochastic_processes.md` | LaTeX math; HTML gets an interactive canvas figure, PDF a static plot |
| `trend_following.md` | Mermaid diagrams; LaTeX math; matplotlib-generated SVG figures (`figures/trend_*.py`) plus the shared `kernel_weights.svg` |
| `market_regimes.md` | Mermaid diagrams; LaTeX math; ASCII figures; matplotlib-generated SVG figures (`figures/regime_*.py`, which also print the simulated tables quoted in the text) plus the shared `purged_split.svg` |

HTML output is a single self-contained file (offline-usable). PDF and HTML may diverge where a document uses format-specific figures.

Published site: [rmahfoud.github.io/quant-research](https://rmahfoud.github.io/quant-research/)

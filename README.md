# Quant research notes

Markdown notes on quantitative topics, renderable to HTML and PDF.

## Prerequisites

These are installed by [`scripts/setup_dev.sh`](../scripts/setup_dev.sh). To install just what’s needed for rendering:

```bash
# pandoc
brew install pandoc          # macOS
# or: apt install pandoc     # Debian/Ubuntu

# mermaid diagrams (momentum_deep_dive)
npm install -g mermaid-filter

# PDF / LaTeX
brew install basictex        # macOS
# or: apt install texlive-latex-base texlive-fonts-recommended texlive-latex-extra
```

On macOS after installing BasicTeX, ensure `/Library/TeX/texbin` is on your `PATH` (or open a new shell — `scripts/render_docs.sh` also adds it when needed).

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
| `momentum_deep_dive.md` | Mermaid diagrams |
| `stochastic_processes.md` | LaTeX math; HTML gets an interactive canvas figure, PDF a static plot |

HTML output is a single self-contained file (offline-usable). PDF and HTML may diverge where a document uses format-specific figures.

#!/usr/bin/env bash

set -euo pipefail

# Usage:
#   ./scripts/render_docs.sh <doc|all> [pdf|html|both] [--figures]
#
# Renders <doc>.md to docs/<doc>.{pdf,html}. Format defaults to "both".
# The mermaid filter is applied only to documents that contain mermaid blocks.
#
#   ./scripts/render_docs.sh momentum_deep_dive
#   ./scripts/render_docs.sh stochastic_processes pdf
#   ./scripts/render_docs.sh all --figures
#
# --figures first re-runs every figures/*.py generator. Those outputs are
# committed and deterministic, so this is only needed after editing a generator.
#
# Paths in the markdown (quant-research/figures/..., quant-research/assets/...)
# are resolved from the parent of this directory, so this folder must be named
# quant-research (nested under Phoenix or as ~/src/quant-research).

RED='\033[31m'
GREEN='\033[32m'
RESET='\033[0m'

print_error() {
    echo -e "${RED}❌ $1${RESET}" >&2
}

print_success() {
    echo -e "${GREEN}✅ $1${RESET}"
}

fail() {
    print_error "$1"
    exit 1
}

QR_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REL_PREFIX="$(basename "$QR_DIR")"
RENDER_ROOT="$(cd "$QR_DIR/.." && pwd)"
OUT_DIR="$QR_DIR/docs"

[[ "$REL_PREFIX" == "quant-research" ]] \
    || fail "This directory must be named quant-research (got: $REL_PREFIX)"

PDF_ARGS=(
    --pdf-engine=xelatex
    -V mainfont="Arial Unicode MS"
    # Arial Unicode MS is a single-face font: without these, \textbf and \emph
    # render as plain upright text, so headings, epistemic tags and emphasis all
    # come out flat. Synthesizing them keeps the font's wide glyph coverage.
    -V mainfontoptions="AutoFakeBold=2.2,AutoFakeSlant=0.2"
    -V monofont="Menlo"
    -V monofontoptions="Scale=0.8"
    -V geometry:margin=0.5in
    # Shared LaTeX preamble (packages + the ELI5 card environment). Note this
    # overrides any `header-includes:` a document sets in its YAML front matter,
    # so preamble additions belong in that file, not in the document.
    --include-in-header="$REL_PREFIX/assets/preamble.tex"
)

HTML_ARGS=(
    --standalone
    --embed-resources
    --toc --toc-depth=2
    # Pandoc's own default today, pinned so it stays in step with the extensions
    # in assets/mathjax_extensions.html, which are built against MathJax 4.
    --mathjax=https://cdn.jsdelivr.net/npm/mathjax@4/tex-chtml.js
    --include-in-header="$REL_PREFIX/assets/reading_widget.html"
    --include-in-header="$REL_PREFIX/assets/sidebar.html"
    --include-in-header="$REL_PREFIX/assets/eli5.html"
    --include-after-body="$REL_PREFIX/assets/mathjax_extensions.html"
    --lua-filter="$REL_PREFIX/scripts/drop_toc_section.lua"
    -V maxwidth=64em
    -V margin-left=32px
    -V margin-right=32px
)

# Target of the sidebar's Source link: <doc>.md in the public repo.
SOURCE_URL="https://github.com/rmahfoud/quant-research/blob/master"

# Published site root, used for canonical URLs, Open Graph and the sitemap.
SITE_URL="https://rmahfoud.github.io/quant-research/"

DOC_ARG=""
FORMAT="both"
RUN_FIGURES=0

for arg in "$@"; do
    case "$arg" in
        --figures) RUN_FIGURES=1 ;;
        pdf|html|both) FORMAT="$arg" ;;
        -*) fail "Unknown option: $arg" ;;
        *) DOC_ARG="$arg" ;;
    esac
done

[[ -n "$DOC_ARG" ]] || fail "Usage: $0 <doc|all> [pdf|html|both] [--figures]"
command -v pandoc >/dev/null || fail "pandoc not found. Run ./scripts/setup_dev.sh"

# xelatex ships with MacTeX/BasicTeX and is usually not on PATH.
ensure_xelatex() {
    command -v xelatex >/dev/null && return 0
    if [[ -x /Library/TeX/texbin/xelatex ]]; then
        export PATH="/Library/TeX/texbin:$PATH"
        return 0
    fi
    fail "xelatex not found. Run ./scripts/setup_dev.sh (BasicTeX / texlive)."
}

resolve_docs() {
    local arg="$1"
    if [[ "$arg" == "all" ]]; then
        local f base
        for f in "$QR_DIR"/*.md; do
            base="$(basename "$f" .md)"
            [[ "$base" == "README" || "$base" == "AGENTS" ]] && continue
            echo "$base"
        done
        return
    fi
    arg="${arg%.md}"
    arg="${arg#quant-research/}"
    echo "$arg"
}

render() {
    local doc="$1" fmt="$2"
    local src="$QR_DIR/$doc.md"
    [[ -f "$src" ]] || fail "No such document: $src"

    local args=(pandoc "$REL_PREFIX/$doc.md" -o "$REL_PREFIX/docs/$doc.$fmt")
    local uses_mermaid=0
    grep -q '^```mermaid' "$src" && uses_mermaid=1

    if [[ "$fmt" == "pdf" ]]; then
        ensure_xelatex
        args+=("${PDF_ARGS[@]}")
    else
        args+=(
            "${HTML_ARGS[@]}"
            -V include-before="<qr-sidebar source=\"$SOURCE_URL/$doc.md\"></qr-sidebar>"
        )
    fi

    if (( uses_mermaid )); then
        command -v mermaid-filter >/dev/null \
            || fail "$doc.md uses mermaid but mermaid-filter is not installed (./scripts/setup_dev.sh)"
        args+=(-F mermaid-filter)
        # SVG for HTML, PNG for PDF — xelatex cannot include SVG, and a diagram
        # emitted as SVG into the PDF loses every node label. Set this on every
        # pass: exporting it only for HTML leaks into a following PDF pass when
        # both formats are rendered in one invocation.
        if [[ "$fmt" == "html" ]]; then
            export MERMAID_FILTER_FORMAT=svg
        else
            export MERMAID_FILTER_FORMAT=png
        fi
    fi

    ( cd "$RENDER_ROOT" && "${args[@]}" )
    (( uses_mermaid )) && rm -f "$RENDER_ROOT/mermaid-filter.err"

    print_success "$REL_PREFIX/docs/$doc.$fmt"
}

mkdir -p "$OUT_DIR"

if (( RUN_FIGURES )); then
    shopt -s nullglob
    for gen in "$QR_DIR"/figures/*.py; do
        echo "Generating figures: $(basename "$gen")"
        ( cd "$RENDER_ROOT" && uv run --no-project --with matplotlib python "$REL_PREFIX/figures/$(basename "$gen")" )
    done
    shopt -u nullglob
fi

formats=()
[[ "$FORMAT" == "both" || "$FORMAT" == "html" ]] && formats+=(html)
[[ "$FORMAT" == "both" || "$FORMAT" == "pdf" ]] && formats+=(pdf)

rendered=()

while read -r doc; do
    for fmt in "${formats[@]}"; do
        render "$doc" "$fmt"
    done
    rendered+=(--require "$doc")
done < <(resolve_docs "$DOC_ARG")

# Canonical URL, Open Graph, JSON-LD and the sitemap. Must run after pandoc:
# --embed-resources inlines the target of any <link href> it is handed, which
# strips the href off a canonical added via --include-in-header. Sweeps every
# rendered page so the sitemap stays complete when only one doc was rendered;
# it is idempotent, so untouched pages come out byte-identical. Only the docs
# rendered in this run are required to carry metadata — an older page missing it
# warns rather than failing a partial render.
if [[ " ${formats[*]} " == *" html "* ]]; then
    python3 "$QR_DIR/scripts/inject_seo.py" "$OUT_DIR" \
        --site-url "$SITE_URL" --repo-root "$RENDER_ROOT" "${rendered[@]}"
fi

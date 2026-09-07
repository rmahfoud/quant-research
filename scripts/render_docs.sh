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
    -V monofont="Menlo"
    -V monofontoptions="Scale=0.8"
    -V geometry:margin=0.5in
)

HTML_ARGS=(
    --standalone
    --embed-resources
    --toc --toc-depth=2
    --mathjax
    --include-in-header="$REL_PREFIX/assets/reading_widget.html"
    -V maxwidth=64em
    -V margin-left=32px
    -V margin-right=32px
)

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
        args+=("${HTML_ARGS[@]}")
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

while read -r doc; do
    for fmt in "${formats[@]}"; do
        render "$doc" "$fmt"
    done
done < <(resolve_docs "$DOC_ARG")

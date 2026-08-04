#!/usr/bin/env bash

set -euo pipefail
source "$(dirname "$0")/../../scripts/shell_support.sh"

# Usage:
#   ./quant-research/scripts/render_docs.sh <doc|all> [pdf|html|both] [--figures]
#
# Renders quant-research/<doc>.md to quant-research/docs/<doc>.{pdf,html}.
# Format defaults to "both". The mermaid filter is applied only to documents
# that actually contain mermaid blocks.
#
#   ./quant-research/scripts/render_docs.sh momentum_deep_dive
#   ./quant-research/scripts/render_docs.sh stochastic_processes pdf
#   ./quant-research/scripts/render_docs.sh all --figures
#
# --figures first re-runs every quant-research/figures/*.py generator. Those
# outputs are committed and deterministic, so this is only needed after editing
# a generator.

QR_DIR="$BASE_DIR/quant-research"
OUT_DIR="$QR_DIR/docs"

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
    # Reading widget (theme + text size). HTML only; the PDF is unaffected.
    --include-in-header=quant-research/assets/reading_widget.html
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
command -v pandoc >/dev/null || fail "pandoc not found. Install with: brew install pandoc"

# xelatex ships with MacTeX and is usually not on PATH.
ensure_xelatex() {
    command -v xelatex >/dev/null && return 0
    if [[ -x /Library/TeX/texbin/xelatex ]]; then
        export PATH="/Library/TeX/texbin:$PATH"
        return 0
    fi
    fail "xelatex not found. Install MacTeX, or add its bin directory to PATH."
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

    local args=(pandoc "quant-research/$doc.md" -o "quant-research/docs/$doc.$fmt")
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
            || fail "$doc.md uses mermaid but mermaid-filter is not installed (npm i -g mermaid-filter)"
        args+=(-F mermaid-filter)
        [[ "$fmt" == "html" ]] && export MERMAID_FILTER_FORMAT=svg
    fi

    # Run from the repo root: raw-LaTeX \includegraphics paths are relative to it.
    ( cd "$BASE_DIR" && "${args[@]}" )
    (( uses_mermaid )) && rm -f "$BASE_DIR/mermaid-filter.err"

    print_success "quant-research/docs/$doc.$fmt"
}

mkdir -p "$OUT_DIR"

if (( RUN_FIGURES )); then
    shopt -s nullglob
    for gen in "$QR_DIR"/figures/*.py; do
        echo "Generating figures: $(basename "$gen")"
        ( cd "$BASE_DIR" && uv run --no-project --with matplotlib python "$gen" )
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

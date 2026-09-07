#! /usr/bin/env bash
set -euo pipefail

# Independent of the Phoenix parent project. Installs tools needed to render
# quant-research docs (pandoc, mermaid-filter, rsvg-convert, TeX, uv).

QR_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$QR_DIR"

RED='\033[31m'
GREEN='\033[32m'
RESET='\033[0m'

fail() {
    echo -e "${RED}❌ $1${RESET}" >&2
    exit 1
}

print_success() {
    echo -e "${GREEN}✅ $1${RESET}"
}

is_mac() {
    [[ "$(uname)" == "Darwin" ]]
}

is_debian_linux() {
    [[ -f /etc/debian_version ]]
}

install_pkgs() {
    local pkgs=("$@")
    if is_debian_linux; then
        if [[ -z "${APT_UPDATED:-}" ]]; then
            sudo apt-get update
            APT_UPDATED=1
        fi
        sudo apt-get install -y "${pkgs[@]}"
    elif is_mac; then
        brew install "${pkgs[@]}"
    else
        fail "Unsupported operating system: $(uname)"
    fi
}

if is_debian_linux; then
    install_pkgs pandoc librsvg2-bin \
        texlive-latex-base texlive-fonts-recommended texlive-latex-extra \
        nodejs npm curl
elif is_mac; then
    install_pkgs pandoc librsvg node
    brew install --cask basictex
else
    fail "Unsupported operating system: $(uname)"
fi

if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="${HOME}/.local/bin:${PATH}"
fi

npm install -g mermaid-filter

if is_mac && [[ -d /Library/TeX/texbin ]]; then
    echo "Note: ensure /Library/TeX/texbin is on your PATH (open a new shell if needed)."
fi

print_success "Setup done. Run: make render-docs"

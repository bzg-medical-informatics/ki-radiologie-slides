#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if command -v sudo >/dev/null 2>&1; then
  SUDO="sudo"
else
  SUDO=""
fi

if [[ "$(uname)" == "Linux" ]]; then
  if command -v apt-get >/dev/null 2>&1; then
    echo "[bootstrap] Installing TeX dependencies..."
    if [[ -n "$SUDO" ]]; then
      "$SUDO" apt-get update
      "$SUDO" apt-get install -y \
        latexmk \
        texlive-latex-base \
        texlive-latex-recommended \
        texlive-latex-extra \
        texlive-fonts-extra \
        texlive-science \
        fonts-adf-gillius
    else
      apt-get update
      apt-get install -y \
        latexmk \
        texlive-latex-base \
        texlive-latex-recommended \
        texlive-latex-extra \
        texlive-fonts-extra \
        texlive-science \
        fonts-adf-gillius
    fi
  else
    echo "[bootstrap] Unsupported Linux distribution: only apt-based systems are supported for now." >&2
    exit 1
  fi
else
  echo "[bootstrap] This bootstrap script currently supports Linux with apt-get only." >&2
  exit 1
fi

echo "[bootstrap] Building the presentation PDF..."
latexmk -C >/dev/null 2>&1 || true
latexmk -pdf -interaction=nonstopmode -synctex=1 main.tex

echo "[bootstrap] Done. Output: $ROOT_DIR/main.pdf"

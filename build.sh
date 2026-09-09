#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if ! command -v latexmk >/dev/null 2>&1; then
  echo "[build] latexmk is not installed. Run ./bootstrap.sh first or install TeX packages." >&2
  exit 1
fi

echo "[build] Compiling LaTeX presentation..."
latexmk -C >/dev/null 2>&1 || true
latexmk -pdf -interaction=nonstopmode -synctex=1 main.tex

echo "[build] Done. Output: $ROOT_DIR/main.pdf"

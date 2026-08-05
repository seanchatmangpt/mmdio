#!/usr/bin/env bash
# Build the OPQL language standard PDF using lualatex.
# Runs lualatex twice so that cross-references and the table of contents
# are resolved correctly.
#
# Usage:
#   ./build.sh              # build in-place, output: main.pdf
#   ./build.sh --ci         # same, but exit non-zero on any warning treated as error
#
# In CI, set the working directory to doc/standard/ or call with a full path.
# The script always runs from the directory that contains main.tex.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

CI_MODE=0
for arg in "$@"; do
  case "$arg" in
    --ci) CI_MODE=1 ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done

LUALATEX="lualatex"
if ! command -v "$LUALATEX" &>/dev/null; then
  echo "error: lualatex not found on PATH" >&2
  exit 1
fi

LATEXFLAGS=(
  -interaction=nonstopmode
  -halt-on-error
  -file-line-error
)

echo "==> lualatex pass 1"
"$LUALATEX" "${LATEXFLAGS[@]}" main.tex

echo "==> lualatex pass 2 (resolve cross-references)"
"$LUALATEX" "${LATEXFLAGS[@]}" main.tex

echo "==> built: $SCRIPT_DIR/main.pdf"

if [ "$CI_MODE" -eq 1 ]; then
  # Surface any underfull/overfull box warnings or undefined references so CI
  # can flag them, without failing the build on cosmetic warnings.
  WARNINGS=$(grep -E "^[^ ].*:[0-9]+: |LaTeX Warning:|LaTeX Error:" main.log || true)
  if [ -n "$WARNINGS" ]; then
    echo "==> warnings/errors found in main.log:"
    echo "$WARNINGS"
  fi

  # Fail if there are undefined references or citations.
  if grep -q "undefined references\|Citation .* undefined" main.log; then
    echo "error: undefined references detected" >&2
    exit 1
  fi
fi

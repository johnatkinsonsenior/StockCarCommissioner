#!/usr/bin/env bash
# Cross-compile StockCarCommissioner.exe for 64-bit Windows.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CC="${MINGW_CC:-x86_64-w64-mingw32-gcc}"
OUT="${1:-$ROOT/StockCarCommissioner.exe}"
"$CC" -O2 -s -municode -mconsole \
    -o "$OUT" \
    "$ROOT/windows/office_launcher.c"
echo "Wrote $OUT"
file "$OUT"

#!/bin/bash
# Resume an oversized DVIDS asset ACROSS runs, always OUTSIDE the repo.
#
# The partial must never live inside the clone: reconcile.py matches records by
# filename glob and ignores size, so a partial sitting in the repo would make the
# record look already-mirrored and it would be silently skipped forever.
#
# Usage: resume_oversized.sh <name> <url> <expected-bytes> [max-seconds]
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="${UAP_WATCHER_WORK:-$(dirname "$HERE")/..}"
WORK="$(cd "$WORK" && pwd)"

NAME="$1"; SRC="$2"; EXPECT="$3"; MAXT="${4:-900}"
PARTIAL="$WORK/${NAME}.partial.mp4"

BEFORE=$(stat -f%z "$PARTIAL" 2>/dev/null || echo 0)
curl -sL -C - --max-time "$MAXT" -o "$PARTIAL" "$SRC" || true
SZ=$(stat -f%z "$PARTIAL" 2>/dev/null || echo 0)
echo "$NAME before=$BEFORE after=$SZ expect=$EXPECT delta=$((SZ-BEFORE))"

if [ "$SZ" -ge "$EXPECT" ] && [ "$(xxd -s 4 -l 4 -p "$PARTIAL" 2>/dev/null)" = "66747970" ]; then
  echo "${NAME}_COMPLETE"; exit 0
fi
echo "${NAME}_PARTIAL"; exit 2

#!/bin/bash
# Weekly mirror run. Order matters: the push guard comes FIRST.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(dirname "$HERE")"
cd "$REPO"

# GUARD — must run BEFORE the diff.
# reconcile.py diffs the CSV against the WORKING TREE. If a previous run committed
# but failed to push, those files are already on disk, the diff comes back empty,
# the run takes the "no changes" exit, and the commit is never pushed — every run
# reporting healthy while the remote sits a commit behind. Check refs, not the diff.
git fetch origin main -q 2>/dev/null || true
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git ls-remote origin main 2>/dev/null | cut -f1)
if [ -n "$REMOTE" ] && [ "$LOCAL" != "$REMOTE" ]; then
  echo "PENDING PUSH: local=${LOCAL:0:7} remote=${REMOTE:0:7} — pushing before diff"
  git push origin main || { echo "PUSH FAILED — resolve before continuing"; exit 1; }
fi

python3 "$HERE/fetch_csv.py"     || exit 1
python3 "$HERE/reconcile.py"     || exit 1
python3 "$HERE/fetch_docs.py"    || true
python3 "$HERE/resolve_dvids.py" || true
python3 "$HERE/fetch_media.py"   || true
echo "Downloads staged. Review, move verified files into the repo root, then commit + push."

# war.gov UAP mirror toolchain

Scripts that mirror <https://www.war.gov/UFO/> into this repository.

They live **inside the repo** on purpose. An out-of-tree copy drifted from the
documented method and stranded three documents for two weeks (see the Akamai trap
below). The committed copy is the copy that runs.

## Pipeline

```
tools/run.sh          # push guard, then the whole pipeline
  fetch_csv.py        # record list (uap-data.csv) + DVIDS API key
  reconcile.py        # diff CSV against the mirror -> diff.json
  fetch_docs.py       # documents/images via in-page fetch()
  resolve_dvids.py    # DVIDS video id -> canonical CloudFront MP4
  fetch_media.py      # download + verify (size + ftyp) + stage
  resume_oversized.sh # multi-run resume for assets too big for one session
```

Downloads land in a scratch dir **outside** the repo (`UAP_WATCHER_WORK`, default:
the repo's parent). Only verified, complete files get moved into the repo root.

## Traps

**Akamai.** `www.war.gov` 403s plain `curl` *and* Playwright's `ctx.request.get()`.
The only transport that clears it is an **in-page `fetch()`** inside a real Chrome
context. This is not a per-file ACL: `ctx.request.get()` fails for every document,
including ones already mirrored. Do not conclude a document was withdrawn from a
403 without first running the same request against a file you know is present.
CloudFront and the DVIDS API are not Akamai-protected; plain `curl` works there.

**Chunked base64.** Reading a large response with
`String.fromCharCode(...bigArray)` overflows the call stack and surfaces as
`TypeError: Failed to fetch` — which reads like a network error and is not one.
Convert in 0x8000 chunks. One 126 MB PDF is what exposed this.

**Partials must stay out of the repo.** `reconcile.py` matches records by filename
glob and ignores size, so a partial inside the repo makes the record look mirrored
and it is skipped forever. Stage in the scratch dir; move in only after verifying
byte size against the DVIDS API and an `ftyp` box at offset 4.

**LFS pointers are not missing files.** On a `GIT_LFS_SKIP_SMUDGE` clone the working
tree holds ~130-byte pointer files, not payload. Any "is it already mirrored?" check
based on a size threshold reads the whole corpus as missing and re-downloads it.
`reconcile.py` matches by filename so it is unaffected; `fetch_docs.py` treats a
pointer as present.

**Push before diff.** `reconcile.py` diffs against the working tree. If a run
commits but fails to push, the files are already on disk, the next diff is empty,
and the run exits "no changes" without pushing — healthy-looking output over a
remote that is a commit behind. `run.sh` compares refs before the diff for this
reason.

**Audio is video.** `Type=AUD` records resolve through the DVIDS API as
`id=video:<id>`, exactly like `Type=VID`. There is no working `audio:` form.
Forgetting this is the historical cause of missing audio records.

## Naming

| Record | Mirror filename |
|---|---|
| `DOW-UAP-PR0NN` | `dow-uap-pr<NN>.mp4` (no leading zeros) |
| `NASA-UAP-D0NN` | `nasa-uap-d<NN>-<short-slug>.mp4` |
| documents | URL basename, URL-decoded, verbatim |

Match by **record-id prefix**, not exact filename — slugs vary, ids are stable.

## Requirements

Python 3, `playwright` with the real Chrome channel (`playwright install chrome`),
`curl`, `git-lfs`.

# uap-release-01

A mirror of the war.gov UFO/UAP release — **338 content files, 15.1 GB** in Git LFS, pulled from <https://www.war.gov/UFO/> starting 2026-05-08 and kept in sync by a weekly watcher.

This is a **mirror of public-domain US government documents**, hosted as the canonical example dataset for the [`uap-release-analyzer`](https://github.com/ckpxgfnksd-max/uap-release-analyzer) skill. It lets anyone reproduce the eval scoreboard against the same input the skill was tuned on, without scraping war.gov themselves.

> **Last sync:** 2026-08-02. war.gov currently lists **334 records** (189 PDF · 103 video · 27 image · 15 audio). 333 are mirrored; **NASA-UAP-D024** (Apollo 16 debriefing, 3.2 GB) is mid-transfer and lands next run. The 5 extra local files are documented under [Known gaps](#known-gaps).

## Composition

| Agency | Files | Size | Notes |
|---|---:|---:|---|
| DOW (Dept of War, formerly DoD) | 163 | 8.60 GB | Mission reports and range-fouler debriefs (PDF) plus 99 Unresolved UAP Report videos `dow-uap-prNN.mp4` |
| FBI | 82 | 2.10 GB | 62-HQ-83894 case-file sections, FD-302 reports, sensor photos, 2024 composite sketch |
| NASA | 38 | 3.34 GB | Apollo / Skylab / Gemini / Mercury transcripts and debriefings, image frames, and 14 audio excerpts `nasa-uap-dNN-*.mp4` |
| NARA / other | 26 | 0.95 GB | Numeric record groups (RG 18, 38, 59, 65, 255, 331, 341, 342) — historical, mostly scanned-only |
| CIA | 21 | 0.09 GB | Scientific Advisory Panel report, OXCART/U-2 history, Soviet-sighting reporting |
| DOE | 5 | 0.01 GB | Pantex image, Tuck correspondence, Pajarito astronomers |
| DOS | 2 | 0.00 GB | Embassy cables (Papua New Guinea 1985, Kazakhstan 1994) |
| ODNI | 1 | 0.00 GB | USPER narrative, senior USIC official |
| **Total** | **338** | **15.09 GB** | |

*(Agency buckets are by filename prefix and approximate at the margins.)*

### Format split

- **193 PDFs** — 3.65 GB. Both text-bearing and scanned-only; the latter need OCR for content.
- **118 MP4s** — 11.42 GB. 99 DOW Unresolved UAP Report videos (`dow-uap-prNN.mp4`), 14 NASA audio excerpts (`nasa-uap-dNN-*.mp4`), plus a handful of other agency clips. Audio records are DVIDS *video* assets — audio over a static frame — so they carry an `.mp4` extension.
- **27 images** — 19 JPG + 8 PNG. FBI sensor frames and the 2024 composite sketch. These need vision analysis, not OCR.

Largest files: `dow-uap-pr52.mp4` (514 MB), `dow-uap-pr58.mp4` (440 MB), `nasa-uap-d25-apollo-16-scientific-debriefing.mp4` (426 MB), `nasa-uap-d11-mercury-atlas-9-audio-excerpt-may-15-1963.mp4` (416 MB).

All video and audio is sourced from war.gov's DVIDS/CloudFront pipeline — see [Provenance](#provenance).

## How to use

Clone with LFS:

```bash
git lfs install              # one-time setup if you don't have LFS
git clone https://github.com/ckpxgfnksd-max/uap-release-01.git ~/Documents/UFO/release_01
```

Then run the analyzer:

```bash
git clone https://github.com/ckpxgfnksd-max/uap-release-analyzer.git
python uap-release-analyzer/scripts/run_all.py ~/Documents/UFO/release_01
open ~/Documents/UFO/release_01/REPORT.md
```

To skip downloading 15 GB up front (clone metadata only, fetch on demand):

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/ckpxgfnksd-max/uap-release-01.git
cd uap-release-01

git lfs pull --include "dow-uap-d27*"        # one specific PDF
git lfs pull --include "dow-uap-*.pdf"       # all DOW mission report PDFs
git lfs pull --include "dow-uap-pr*.mp4"     # all 99 DOW Unresolved-Report videos
git lfs pull --include "nasa-uap-d*.mp4"     # the 14 NASA audio excerpts
git lfs pull --include "65_hs1*"             # the heavy FBI scanned sections
```

## Toolchain

The scripts that maintain this mirror live in [`tools/`](tools/), version-controlled alongside the corpus so the committed copy is the copy that runs:

```bash
tools/run.sh     # ref check, then: fetch record list -> diff -> fetch docs -> resolve DVIDS -> fetch media
```

[`tools/README.md`](tools/README.md) documents the non-obvious failure modes — the Akamai transport that only an in-page `fetch()` clears, chunked base64 on large responses, why partial downloads must never sit inside the repo, and why audio records resolve as `id=video:`. Read it before changing the pipeline.

## Provenance

- **Source:** <https://www.war.gov/UFO/>
- **PDFs and images first pulled:** 2026-05-08.
- **Videos (PR19–PR49) added 2026-05-09:** fetched from `d34w7g4gy10iej.cloudfront.net/video/<group>/DOD_<id>/DOD_<id>.mp4` after each record's DVIDS asset id was discovered. war.gov serves these through an inline viewer with client-side HLS-to-MP4 assembly; the direct CloudFront URLs bypass that and return the pre-assembled MP4.
- **2026-05-31:** switched the watcher from DOM scraping to the server-side `uap-data.csv` manifest, which is authoritative and removed the synthetic-click fragility.
- **2026-06-07:** completed the release_02 tranche — DOW PR092–PR099 and the first NASA audio excerpts. Audio has no per-file war.gov URL and resolves through the DVIDS asset API (`https://api.dvidshub.net/asset?api_key=<key>&id=video:<DVIDS_ID>`, sent with a `https://www.war.gov/` Referer), reading `results.files[].src` for the canonical `…/DOD_<id>/DOD_<id>.mp4`.
- **2026-08-02:** added DOW-UAP-D092/D093/D096 and 11 media records. Two earlier runs had reported those three documents as withdrawn from war.gov. That was wrong: the fetcher had drifted onto a transport Akamai rejects for *every* war.gov document, including files already mirrored. All three downloaded normally through the documented path. Nothing had been withdrawn, and the toolchain was moved into this repo so the failure mode cannot recur silently.
- **Verification:** every media file is checked against the size reported by the DVIDS API and for an `ftyp` box before being committed.
- **No re-redactions or transformations** have been applied. Files are as-released by war.gov.

## Known gaps

- **NASA-UAP-D024** (Apollo 16 Scientific Debriefing, 3.2 GB) is mid-transfer across runs and not yet mirrored.
- **5 files present here with no matching current war.gov record.** These are renames, duplicates, or superseded entries retained deliberately — nothing is ever auto-deleted:
  `255_t_763_r1b_excerpt.mp4`, `59_214434_sp_16_7.18.1963.pdf`,
  `dow-uap-d20-mission-report-southern-united-states-2020.pdf` (see issue #3),
  `dow-uap-pr20 (1).pdf`, `nasa-uap-d3-gemini-7-transcript-1965.pdf`.

## License / copyright

US federal government works are not eligible for copyright under [17 U.S.C. § 105](https://www.copyright.gov/title17/92chap1.html#105) and are in the public domain in the United States. Foreign copyright treatment may vary; check your jurisdiction if redistributing outside the US.

This repository carries no additional copyright claim by Chase Wang or contributors.

## Storage notes

The corpus is **15.09 GB across 338 binary files** in Git LFS (193 PDFs · 3.65 GB, 118 MP4s · 11.42 GB, 27 images · 0.02 GB). Several files exceed GitHub's 100 MB single-file cap, which is why LFS is required.

If you don't need the heaviest scanned NARA/FBI files (they have no text layer, and the analyzer flags them as "OCR-required" rather than analyzing them) or the larger videos, the partial-clone form above fetches only the buckets you care about.

## Sync to upstream

Updates are picked up by the `war-gov-uap-watcher` scheduled task (weekly, Sunday 9 AM local). It fetches war.gov's `uap-data.csv` with a headless browser (Akamai 403s plain curl), diffs it against this mirror, resolves video and audio records through the DVIDS API, verifies each download, and commits via Git LFS. Files that vanish from war.gov are flagged in an issue for review, never auto-deleted.

A record is only left as a `*.viewer-only.txt` placeholder when it genuinely cannot be resolved to bytes; that is the rare exception, not the default. If you spot a delta the watcher missed, open an issue.

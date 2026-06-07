# uap-release-01

A mirror of the war.gov "PURSUE" UFO/UAP release — **226 content files** (126 PDFs, 86 MP4 — 79 video + 7 audio, 14 images), **~6.0 GB** in Git LFS. Pulled from <https://www.war.gov/UFO/>, first on 2026-05-08 and kept in sync by a weekly watcher since.

This is a **mirror of public-domain US government documents**, hosted here as the canonical example dataset for the [`uap-release-analyzer`](https://github.com/ckpxgfnksd-max/uap-release-analyzer) skill. It lets anyone reproduce the eval scoreboard against the same input the skill was tuned on, without scraping war.gov themselves.

> **Last sync:** 2026-06-07. war.gov exposes two tranches — the original **release_1** and a **release_02** (dated 05-22-26). Both are fully mirrored: all 136 medialink documents, all videos (incl. the new DOW PR092–PR099), and the 7 NASA audio excerpts. release_02 is complete.

## Composition

| Agency | Files | Notes |
|---|---|---|
| DOW (Dept of War, formerly DoD) | 123 | Mission reports + range-fouler debriefs (PDF) and 78 Unresolved UAP Report videos `dow-uap-prNN.mp4` (PR19–PR99, with gaps) |
| NARA (numeric record groups) | 44 | RG 18, 38, 59, 65, 255, 331, 341, 342 — historical, mostly scanned-only |
| FBI | 32 | 62-HQ-83894 case-file sections, FD-302 reports, sensor photos, 2024 composite sketch |
| NASA | 20 | Apollo / Skylab / Gemini transcripts + debriefings (PDF), 6 image frames, and 7 Apollo/Mercury audio excerpts `nasa-uap-dNN-*.mp4` (incl. the `255_t_763_r1b_excerpt.mp4`) |
| DOE | 3 | Pantex image, Tuck correspondence, Pajarito astronomers |
| DOS | 2 | Embassy cables (Papua New Guinea 1985, Kazakhstan 1994) |
| CIA | 1 | Intelligence Information Report, USSR, 1973 |
| ODNI | 1 | USPER narrative, senior USIC official |
| **Total** | **226** | |

*(Agency buckets are by filename prefix and approximate at the margins.)*

### Format split

- **126 PDFs** (2.48 GB) — text-bearing and scanned-only (the latter need OCR for content)
- **79 video MP4s** — DOW Unresolved UAP Reports (`dow-uap-prNN.mp4`, PR19–PR99) + one NASA excerpt (`255_t_763_r1b_excerpt.mp4`). Largest is 275 MB (`dow-uap-pr42.mp4`)
- **7 audio MP4s** — NASA Apollo/Mercury audio excerpts (`nasa-uap-d8..d14-*.mp4`). DVIDS video assets (audio over a static frame)
- **14 images** (8 PNG + 6 JPG) — FBI sensor frames and the 2024 composite sketch. Need vision analysis, not OCR

All videos and audio are sourced from war.gov's DVIDS/CloudFront pipeline — see [Provenance](#provenance) for the resolution path.

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

To skip downloading the corpus immediately (clone metadata only, fetch files on demand):

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/ckpxgfnksd-max/uap-release-01.git
cd uap-release-01

git lfs pull --include "dow-uap-d27*"        # one specific PDF
git lfs pull --include "dow-uap-*.pdf"       # all DOW mission report PDFs
git lfs pull --include "dow-uap-pr*.mp4"     # all 78 DOW Unresolved-Report videos
git lfs pull --include "nasa-uap-d*.mp4"     # the 7 NASA Apollo/Mercury audio excerpts
git lfs pull --include "65_hs1*"             # the heavy FBI scanned sections
```

## Provenance

- **Source:** <https://www.war.gov/UFO/>
- **PDFs + images first pulled:** 2026-05-08
- **Videos (PR19–PR49) added:** 2026-05-09 — fetched directly from `d34w7g4gy10iej.cloudfront.net/video/<group>/DOD_<id>/DOD_<id>.mp4` after each record's DVIDS asset id was discovered via the war.gov lightbox modal. War.gov serves these via inline viewer + client-side HLS-to-MP4 assembly; the direct CloudFront URLs bypass that and return the pre-assembled MP4 in seconds.
- **Subsequent weekly watcher runs:** extended the DOW videos through PR91 and merged the **release_02** document tranche (`/medialink/ufo/052226/release_02/`).
- **2026-06-07:** completed release_02 — added the 8 new DOW videos (PR092–PR099) and 7 NASA Apollo/Mercury audio excerpts (NASA-UAP-D008–D014) as real MP4s. These are DVIDS-streamed records with no per-file war.gov URL; resolved via the DVIDS asset API (`https://api.dvidshub.net/asset?api_key=<key>&id=video:<DVIDS_ID>`, sent with a `https://www.war.gov/` Referer), reading `results.files[].src` for the canonical `…/DOD_<id>/DOD_<id>.mp4` on CloudFront. All 15 verified by size + MP4 header. Also flagged one document, `dow-uap-d20-mission-report-southern-united-states-2020.pdf`, that no longer resolves on war.gov (likely a rename) for review — see issue #3. Nothing is ever auto-deleted.
- **No re-redactions or transformations** have been applied. Files are as-released by war.gov.

For the scrape mechanics (DOM-only pagination, blob URLs, synthetic-click downloads), see [war_gov_quirks.md](https://github.com/ckpxgfnksd-max/uap-release-analyzer/blob/main/references/war_gov_quirks.md) in the analyzer repo.

## License / copyright

US federal government works are not eligible for copyright under [17 U.S.C. § 105](https://www.copyright.gov/title17/92chap1.html#105) and are in the public domain in the United States. Foreign copyright treatment may vary; check your jurisdiction if redistributing outside the US.

This repository carries no additional copyright claim by Chase Wang or contributors.

## Storage notes

This corpus uses Git LFS — **~6.0 GB across 226 binary files** (126 PDFs · 2.48 GB, 86 videos+audio MP4s · ~3.5 GB, 14 images). Several files exceed GitHub's 100 MB single-file cap — the largest are a 416 MB NASA audio excerpt (`nasa-uap-d11-*.mp4`), a 371 MB FBI scan section (`65_hs1-834228961_62-hq-83894_section_6.pdf`), and a 275 MB DOW UAP video (`dow-uap-pr42.mp4`) — which is why LFS is required.

If you don't need the heaviest scanned NARA/FBI files (they don't have text layers anyway and the skill flags them as "OCR-required" rather than analyzing them) or the larger videos, the partial-clone form above lets you fetch only the buckets you care about.

## Sync to upstream

Updates from war.gov are picked up automatically by the `war-gov-uap-watcher` scheduled task (weekly, Sunday 9 AM local). It crawls war.gov with a headless browser (Akamai 403s plain curl), diffs the live `uap-data.csv` against this mirror, auto-mirrors any new downloadable files via Git LFS, and leaves `*.viewer-only.txt` placeholders for inline-viewer records with no clean URL. Files that vanish from war.gov are flagged in an issue for review, never auto-deleted. If you spot a delta the watcher missed, open an issue here.

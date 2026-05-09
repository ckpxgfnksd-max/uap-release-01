# uap-release-01

The May 2026 war.gov "PURSUE" UFO release — 160 declassified files (118 PDFs, 28 MP4 videos, 8 PNGs, 6 JPGs), totaling ~3.7 GB. Pulled from <https://www.war.gov/UFO/> on 2026-05-08, with the video tranche added on 2026-05-09.

This is a **mirror of public-domain US government documents**, hosted here as the canonical example dataset for the [`uap-release-analyzer`](https://github.com/ckpxgfnksd-max/uap-release-analyzer) skill. It lets anyone reproduce the eval scoreboard against the same input the skill was tuned on, without scraping war.gov themselves.

## Composition

| Agency | Files | Notes |
|---|---|---|
| FBI | 57 | 62-HQ-83894 case-file sections, FD-302 interview reports, sensor photos, 2024 composite sketch |
| DOW (Dept of War, formerly DoD) | 72 | 44 mission reports + range-fouler debriefs (PDF) + 28 Unresolved UAP Report videos (PR19, PR21–23, PR26–29, PR31–49) from CENTCOM AOR, 2020–2026 |
| NASA | 13 | Apollo / Skylab / Gemini transcripts and crew debriefings (one of these is the 255-T-763-R1B-EXCERPT video) |
| NARA | 13 | Record-group boxes (RG 18, 38, 59, 255, 331, 341, 342) — historical, mostly scanned-only |
| DOS | 5 | Embassy cables (Papua New Guinea 1985, Kazakhstan 1994, etc.) |
| **Total** | **160** | |

### Format split

- **118 PDFs** — 54 text-bearing, 64 scanned with no text layer (OCR required for content)
- **28 MP4 videos** — DOW Unresolved UAP Reports (`dow-uap-prNN.mp4`) + one NASA excerpt (`255_t_763_r1b_excerpt.mp4`). Sourced from war.gov's DVIDS/CloudFront pipeline. Range from 0.4 MB to 262 MB; total ~1.27 GB
- **14 images** (PNG/JPG) — FBI sensor frames and the 2024 composite sketch. Need vision analysis, not OCR

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
git lfs pull --include "dow-uap-pr*.mp4"     # all 27 DOW Unresolved-Report videos
git lfs pull --include "65_hs1*"             # the heavy FBI scanned sections
```

## Provenance

- **Source:** <https://www.war.gov/UFO/>
- **PDFs + images pulled:** 2026-05-08 (132 files)
- **Videos added:** 2026-05-09 (28 files, 1.27 GB) — fetched directly from `d34w7g4gy10iej.cloudfront.net/video/<group>/DOD_<id>/DOD_<id>.mp4` after each record's DVIDS asset id was discovered via the war.gov lightbox modal. War.gov serves these via inline viewer + client-side HLS-to-MP4 assembly; the direct CloudFront URLs bypass that and return the pre-assembled MP4 in seconds.
- **No re-redactions or transformations** have been applied. Files are as-released by war.gov.

For the scrape mechanics (DOM-only pagination, blob URLs, synthetic-click downloads), see [war_gov_quirks.md](https://github.com/ckpxgfnksd-max/uap-release-analyzer/blob/main/references/war_gov_quirks.md) in the analyzer repo.

## License / copyright

US federal government works are not eligible for copyright under [17 U.S.C. § 105](https://www.copyright.gov/title17/92chap1.html#105) and are in the public domain in the United States. Foreign copyright treatment may vary; check your jurisdiction if redistributing outside the US.

This repository carries no additional copyright claim by Chase Wang or contributors.

## Storage notes

This corpus uses Git LFS. ~3.7 GB across 160 content files (118 PDFs, 28 videos, 14 images). Several files exceed GitHub's 100 MB single-file cap — the largest are a 353 MB FBI scan section and a 262 MB DOW UAP video — which is why LFS is required.

If you don't need the heaviest scanned NARA/FBI files (they don't have text layers anyway and the skill flags them as "OCR-required" rather than analyzing them) or the larger videos, the partial-clone form above lets you fetch only the buckets you care about.

## Sync to upstream

Updates from war.gov are picked up automatically by the `war-gov-uap-watcher` scheduled task (weekly, Sunday 9 AM local). It crawls war.gov, diffs against this mirror, and auto-mirrors any new files via the same CloudFront direct-URL path that brought the 28 videos in. If you spot a delta the watcher missed, open an issue here.

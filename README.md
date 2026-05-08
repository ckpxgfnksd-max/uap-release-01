# uap-release-01

The May 2026 war.gov "PURSUE" UFO release — 132 declassified files (118 PDFs, 8 PNGs, 6 JPGs), totaling ~2.4 GB / ~4,157 PDF pages. Pulled from <https://www.war.gov/UFO/> on 2026-05-08.

This is a **mirror of public-domain US government documents**, hosted here as the canonical example dataset for the [`uap-release-analyzer`](https://github.com/ckpxgfnksd-max/uap-release-analyzer) skill. It lets anyone reproduce the eval scoreboard against the same input the skill was tuned on, without scraping war.gov themselves.

## Composition

| Agency | Files | Notes |
|---|---|---|
| FBI | 57 | 62-HQ-83894 case-file sections, FD-302 interview reports, sensor photos, 2024 composite sketch |
| DOW (Dept of War, formerly DoD) | 44 | Mission reports + range-fouler debriefs from CENTCOM AOR, 2020–2024 |
| NASA | 13 | Apollo / Skylab / Gemini transcripts and crew debriefings |
| NARA | 13 | Record-group boxes (RG 18, 38, 59, 255, 331, 341, 342) — historical, mostly scanned-only |
| DOS | 5 | Embassy cables (Papua New Guinea 1985, Kazakhstan 1994, etc.) |
| **Total** | **132** | |

**Of the 118 PDFs:** 54 have a text layer; 64 are scanned with no text layer. The 14 image files (PNG/JPG) are FBI sensor-frame photos and the 2024 composite sketch — they need vision analysis, not OCR.

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
git lfs pull --include "dow-uap-d27*"   # fetch just one file
git lfs pull --include "dow-*"          # fetch a whole bucket
```

## Provenance

- **Source:** <https://www.war.gov/UFO/>
- **Pulled:** 2026-05-08
- **Files served via inline viewer (~17% of war.gov records):** present where downloadable; the inline-viewer-only records (DOW-UAP-PR* "Unresolved Report" series) were captured where the URL could be hooked. See [war_gov_quirks.md](https://github.com/ckpxgfnksd-max/uap-release-analyzer/blob/main/references/war_gov_quirks.md) in the analyzer repo for the scrape mechanics.
- **No re-redactions or transformations** have been applied. Files are as-released by war.gov.

## License / copyright

US federal government works are not eligible for copyright under [17 U.S.C. § 105](https://www.copyright.gov/title17/92chap1.html#105) and are in the public domain in the United States. Foreign copyright treatment may vary; check your jurisdiction if redistributing outside the US.

This repository carries no additional copyright claim by Chase Wang or contributors.

## Storage notes

This corpus uses Git LFS. ~2.4 GB across 132 files. 9 files exceed GitHub's 100 MB single-file cap (the largest is 353 MB), which is why LFS is required.

If you don't need the heaviest scanned NARA/FBI files (they don't have text layers anyway and the skill flags them as "OCR-required" rather than analyzing them), the partial-clone form above lets you fetch only the buckets you care about.

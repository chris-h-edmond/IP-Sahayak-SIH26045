# Corpus coverage review

Reviewed 26 November 2026 against the locally available filenames and the official pages linked below. This is a source-presence check, not legal advice or a full amendment-history review.

## Confirmed local coverage

- Trade Marks Rules, 2017: `Trade_Marks_Rules_2017.pdf` is present.
- Designs Rules, 2001 and 2021 amendment: both files are present.
- Copyright Rules, 2013 and 2021 amendment: both files are present.
- GI Rules, 2002 and 2025 amendment: both files are present.
- Patent Rules, 2003 and Patent Amendment Rules, 2025: both files are present. IP India's rules page lists the 2025 amendment with a 6 October 2026 publish date, so confirm the downloaded file is that version before treating it as current.
- FSSAI 25 July 2025 Ayurveda Aahara order: present locally.

## Missing or unresolved source files

| Item | Finding | Official source |
| --- | --- | --- |
| FSSAI KoB order dated 1 September 2025 | Not present by filename in `data/raw`; add the official order. Its subject introduces the Ayurveda Aahara Kind of Business in FoSCoS and sets licensing/registration details. | https://www.fssai.gov.in/upload/advisories/2025/09/68b685259cb03Order%20dated01stSeptember2025-Introduction%20of%20new%20KoB-Ayurveda%20aahara.pdf |
| FSSAI Ayurveda Aahara recipe update, Part 2, 19 June 2026 | Not present by filename in `data/raw`; add alongside Part 1 / the 25 July 2025 order if the assistant covers approved recipe classification. | https://fssai.gov.in/upload/advisories/2026/06/6a34f644db631Annexure%20No_part-2%20Compendium%20of%20Ayurveda%20Aahara%20recipes.pdf |
| Official English Ayurveda Aahara Regulations, 2022 Gazette | The local file is named as Hindi. Keep the official English text as a parallel source for bilingual retrieval and citation review. | https://www.fssai.gov.in/upload/notifications/2022/05/62789a20b54bdGazette_Notification_Ayurveda_Aahara_09_05_2022.pdf |
| Patent Amendment Rules, 2025 identity | Local file exists; compare its contents/version with IP India's listing, which shows a 6 October 2026 publication date. | https://www.ipindia.gov.in/resource/patents-resources-rules |

## Exact duplicate review flags

The SHA-256 report found two exact byte-identical pairs. Preserve all source files until manually reviewed:

- `Biological Diversity (Access to Biological Resources and Knowledge Associated thereto and Fair and Equitable Sharing of Benefits) Regulations, 2025.pdf` and `GNABSREG_2025.pdf`.
- `Geographical Indications Act, 1999.pdf` and `GI_Rules_2002.pdf`.

The second pair has filenames that imply different instruments despite identical bytes. Verify both against their title pages and official downloads; do not rely on names alone.

## Invalid PDF candidate

`WIPO_Treaty_Genetic_Resources_Traditional_Knowledge_2024.pdf` failed `pdfinfo` with syntax errors beginning near byte 45 (the parser reports a non-PDF header). Treat this file as `ERROR` and replace it with a valid official document after checking the source URL. The original is untouched.

## Tool limitation

45 of 46 files opened in bundled Poppler `pdfinfo`, and page counts were recorded for those 45. One file failed as described above. PyMuPDF could not be installed because PyPI was unreachable. Therefore text extraction, OCR need, Devanagari quality, low-text pages, and overlap scores remain pending. Run `python -m pip install pymupdf`, then `python scripts/audit_corpus.py` to complete those fields and reports.

Official reference pages checked:

- https://www.ipindia.gov.in/resource/patents-resources-rules
- https://www.fssai.gov.in/food-law/advisories
- https://stg-old.fssai.gov.in/cms/food-safety-and-standards-regulations.php

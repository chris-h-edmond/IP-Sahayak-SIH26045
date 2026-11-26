"""Audit PDFs in data/raw without changing the originals.

Install PyMuPDF (python -m pip install pymupdf) to enable text extraction,
Devanagari detection, low-text flags, and overlap estimates. If unavailable,
the script falls back to Poppler's pdfinfo for open/page-count checks.
"""
from __future__ import annotations

import csv
import hashlib
import re
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
TEXT_DIR = PROCESSED / "extracted_text"
AUDIT_DIR = PROCESSED / "audit"
METADATA_DIR = ROOT / "data" / "metadata"

try:
    import fitz  # type: ignore
except ImportError:
    fitz = None

for directory in (TEXT_DIR, AUDIT_DIR, METADATA_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pdfinfo(path: Path) -> tuple[int | None, str | None]:
    command = shutil.which("pdfinfo")
    if not command:
        return None, "PyMuPDF and pdfinfo are unavailable"
    result = subprocess.run([command, str(path)], capture_output=True, text=True)
    if result.returncode:
        return None, (result.stderr or result.stdout).strip()[:500]
    match = re.search(r"^Pages:\s+(\d+)", result.stdout, re.M)
    return (int(match.group(1)) if match else None), None


pdfs = sorted(RAW_DIR.glob("*.pdf"), key=lambda p: p.name.casefold())
audit_rows: list[dict[str, object]] = []
hashes: dict[str, list[str]] = defaultdict(list)
texts: dict[str, str] = {}
metadata_rows: list[dict[str, str]] = []

for path in pdfs:
    digest = sha256(path)
    hashes[digest].append(path.name)
    row: dict[str, object] = {
        "file_name": path.name,
        "sha256": digest,
        "file_size_bytes": path.stat().st_size,
        "pages": "",
        "status": "",
        "extractable_characters": "",
        "low_text_pages": "",
        "devanagari_detected": "",
        "error": "",
    }
    if fitz is not None:
        try:
            document = fitz.open(path)
            page_texts = [page.get_text("text") for page in document]
            text = "\n\n".join(page_texts)
            row["pages"] = len(document)
            row["extractable_characters"] = len(text.strip())
            low_pages = [str(i + 1) for i, value in enumerate(page_texts) if len(value.strip()) < 40]
            row["low_text_pages"] = ";".join(low_pages)
            row["devanagari_detected"] = bool(re.search(r"[\u0900-\u097F]", text))
            row["status"] = "OCR_REQUIRED" if not text.strip() else ("CHECK_LOW_TEXT_PAGES" if low_pages else "OK")
            if text.strip():
                texts[path.name] = text
                (TEXT_DIR / f"{path.stem}.txt").write_text(text, encoding="utf-8")
            document.close()
        except Exception as exc:
            row["status"] = "ERROR"
            row["error"] = str(exc)[:500]
    else:
        pages, error = pdfinfo(path)
        row["pages"] = pages if pages is not None else ""
        row["status"] = "CHECK_EXTRACTION_UNAVAILABLE" if not error else "ERROR"
        row["error"] = error or "Install PyMuPDF to inspect text and OCR needs"
    audit_rows.append(row)
    metadata_rows.append({
        "document_id": f"DOC-{len(metadata_rows) + 1:03d}",
        "file_name": path.name,
        "language": "",
        "jurisdiction": "",
        "authority": "",
        "document_type": "",
        "version_date": "",
        "effective_date": "",
        "source_url": "",
        "amendment_status": "",
        "review_status": "PENDING_VERIFICATION",
        "notes": "Populate from title page, Gazette notification, and official source; do not infer dates.",
    })

def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

write_csv(AUDIT_DIR / "audit_report.csv", audit_rows, list(audit_rows[0]) if audit_rows else ["file_name"])
duplicate_rows = [
    {"sha256": digest, "file_names": " | ".join(names), "count": len(names)}
    for digest, names in hashes.items() if len(names) > 1
]
write_csv(AUDIT_DIR / "duplicate_report.csv", duplicate_rows, ["sha256", "file_names", "count"])

def shingles(text: str, n: int = 5) -> set[tuple[str, ...]]:
    words = re.findall(r"\w+", text.casefold())
    return {tuple(words[i:i+n]) for i in range(max(0, len(words) - n + 1))}

overlap_rows: list[dict[str, object]] = []
formulary = [(name, text) for name, text in texts.items() if re.search(r"formulary|pharmacop", name, re.I)]
for i, (name_a, text_a) in enumerate(formulary):
    a = shingles(text_a)
    for name_b, text_b in formulary[i + 1:]:
        b = shingles(text_b)
        union = a | b
        score = (100 * len(a & b) / len(union)) if union else 0.0
        overlap_rows.append({"document_a": name_a, "document_b": name_b, "similarity_percent": round(score, 2)})
overlap_rows.sort(key=lambda row: float(row["similarity_percent"]), reverse=True)
write_csv(AUDIT_DIR / "overlap_report.csv", overlap_rows, ["document_a", "document_b", "similarity_percent"])
write_csv(METADATA_DIR / "metadata.csv", metadata_rows, list(metadata_rows[0]) if metadata_rows else ["document_id", "file_name"])

print(f"PDFs found: {len(pdfs)}")
print(f"Exact duplicate groups: {len(duplicate_rows)}")
print(f"Text extraction: {'enabled' if fitz is not None else 'unavailable (install pymupdf)'}")
print(f"Reports: {AUDIT_DIR}")

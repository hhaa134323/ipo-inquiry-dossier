#!/usr/bin/env python3
"""Extract text from PDFs, cache as .txt with [PAGE n] markers.

Usage:
    python scripts/extract.py
    python scripts/extract.py --input ../my_pdfs

Scans the input directory for all *.pdf files (recursively). For each,
writes a sibling *.txt file where every page begins with "[PAGE n]" on
its own line. Skips if .txt already exists.
"""

import argparse
from pathlib import Path

import fitz  # pymupdf


def extract_all() -> None:
    """Extract all PDFs in INPUT_DIR to .txt cache files."""
    parser = argparse.ArgumentParser(
        description="抽取 PDF 文本缓存（[PAGE n] 标记）"
    )
    parser.add_argument(
        "--input", "-i",
        default="./input",
        help="输入目录（递归扫描 *.pdf），默认 ./input",
    )
    args = parser.parse_args()

    input_dir = Path(args.input).resolve()
    pdfs = sorted(input_dir.rglob("*.pdf"))

    if not pdfs:
        print(f"No PDF files found in {input_dir}.")
        return

    for pdf_path in pdfs:
        txt_path = pdf_path.with_suffix(".txt")
        if txt_path.exists():
            print(f"  SKIP  {txt_path.name}  (cache exists)")
            continue

        print(f"  EXTRACT {txt_path.name}")
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"    ERROR: cannot open — {e}")
            continue

        lines: list[str] = []
        for page_num, page in enumerate(doc, start=1):
            lines.append(f"[PAGE {page_num}]")
            text = page.get_text()
            lines.append(text)

        doc.close()
        txt_path.write_text("\n".join(lines), encoding="utf-8")

    print("Done.")


if __name__ == "__main__":
    extract_all()

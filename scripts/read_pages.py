#!/usr/bin/env python3
"""Read specific pages verbatim from a .txt cache (produced by extract.py).

Usage:
    python scripts/read_pages.py --file ../out/中芯国际.txt --pages 42
    python scripts/read_pages.py -f 中芯国际.txt -p 42-45
    python scripts/read_pages.py -f 中芯国际.pdf -p 3,7,12-14

This is the *mechanical* reader used in precision rerank: 闸一 reads the inquiry
question page(s), 闸二 reads the reply page range. It does NOT score or judge —
it just prints the requested pages verbatim (引用纪律：原文不改写), each prefixed
with its [PAGE n] marker so boundaries stay explicit. A .pdf path is resolved to
its sibling .txt cache.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_pages(spec: str) -> list[int]:
    """Parse a page spec like '42', '42-45', '3,7,12-14' into a sorted list."""
    pages: set[int] = set()
    for part in spec.replace("，", ",").split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, _, b = part.partition("-")
            try:
                start, end = int(a), int(b)
            except ValueError:
                continue
            if start > end:
                start, end = end, start
            pages.update(range(start, end + 1))
        elif part.isdigit():
            pages.add(int(part))
    return sorted(pages)


def read_pages(txt_path: Path, wanted: list[int]) -> str:
    """Return the requested pages (with [PAGE n] headers) verbatim."""
    want = set(wanted)
    out: list[str] = []
    page = 0
    capturing = False
    for line in txt_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("[PAGE ") and stripped.endswith("]"):
            inner = stripped[len("[PAGE "):-1].strip()
            page = int(inner) if inner.isdigit() else page + 1
            capturing = page in want
            if capturing:
                out.append(f"[PAGE {page}]")
            continue
        if capturing:
            out.append(line)
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="按页码从 .txt 缓存逐字读取指定页（供闸一读问询题目 / 闸二精读回复）"
    )
    parser.add_argument(
        "--file", "-f", required=True,
        help="目标 .txt 缓存路径（也接受 .pdf，会自动解析为同名 .txt）",
    )
    parser.add_argument(
        "--pages", "-p", required=True,
        help="页码，如 42 / 42-45 / 3,7,12-14",
    )
    args = parser.parse_args()

    txt_path = Path(args.file).resolve()
    if txt_path.suffix.lower() == ".pdf":
        txt_path = txt_path.with_suffix(".txt")
    if not txt_path.exists():
        print(f"ERROR: cache not found: {txt_path}. Run extract.py first.",
              file=sys.stderr)
        sys.exit(1)

    wanted = parse_pages(args.pages)
    if not wanted:
        print(f"ERROR: could not parse pages spec: {args.pages!r}",
              file=sys.stderr)
        sys.exit(1)

    text = read_pages(txt_path, wanted)
    if not text.strip():
        print(f"[未找到第 {args.pages} 页，或该页为空：{txt_path.name}]")
        return
    print(text)


if __name__ == "__main__":
    main()

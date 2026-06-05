#!/usr/bin/env python3
"""Mechanical recall: grep AI-generated 口径词 across .txt caches.

Usage:
    python scripts/recall.py --input ../my_pdfs --term-map ../out/_work/term_map.jsonl
    python scripts/recall.py -i ./input -t ./output/_work/term_map.jsonl -o ./output/_work/candidates.jsonl

This is the *mechanical* half of step 2 (召回). The *judgment* half — expanding
the question's 限定词 into 口径词 — stays with the AI, which writes term_map.jsonl.
This script only does the deterministic grep: it never decides which terms to
search, it just scans for the ones the AI gave it. Nothing here is industry-specific.

term_map.jsonl schema (one JSON object per line; an optional meta line carrying
only a "问题原文"/"question" key is ignored for term extraction):
    {"原文词": "毛利率", "扩展检索词": ["综合毛利率", "主营业务毛利率", "毛利"]}
English keys are also accepted: {"term": "...", "expansions": ["..."]}.

Output candidates.jsonl: one deduped hit per line:
    {"文件": "中芯国际.txt", "页": 42, "命中词": "毛利率", "上下文": "...命中行..."}
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_terms(term_map_path: Path) -> list[str]:
    """Read term_map.jsonl and flatten into a unique, ordered term list."""
    terms: list[str] = []
    seen: set[str] = set()
    if not term_map_path.exists():
        return terms
    for raw in term_map_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        has_term_key = any(
            k in obj for k in ("原文词", "term", "扩展检索词", "扩展词", "expansions")
        )
        # Skip a pure meta line (carries the source question, not terms)
        if not has_term_key:
            continue
        collected: list[str] = []
        for key in ("原文词", "term"):
            val = obj.get(key)
            if isinstance(val, str):
                collected.append(val)
        for key in ("扩展检索词", "扩展词", "expansions"):
            val = obj.get(key)
            if isinstance(val, list):
                collected.extend(str(v) for v in val)
        for t in collected:
            t = t.strip()
            if t and t not in seen:
                seen.add(t)
                terms.append(t)
    return terms


def scan_file(txt_path: Path, terms: list[str]) -> list[dict]:
    """Grep one .txt cache for every term; track [PAGE n] page numbers."""
    hits: list[dict] = []
    seen: set = set()
    page = 0
    for line in txt_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("[PAGE ") and stripped.endswith("]"):
            inner = stripped[len("[PAGE "):-1].strip()
            if inner.isdigit():
                page = int(inner)
            continue
        if not stripped:
            continue
        low = stripped.lower()
        for term in terms:
            if term.lower() in low:
                key = (page, term, stripped)
                if key in seen:
                    continue
                seen.add(key)
                hits.append({
                    "文件": txt_path.name,
                    "页": page,
                    "命中词": term,
                    "上下文": stripped[:200],
                })
    return hits


def main() -> None:
    parser = argparse.ArgumentParser(
        description="机械召回：按 term_map.jsonl 的口径词 grep 全部 .txt 缓存，产出 candidates.jsonl"
    )
    parser.add_argument(
        "--input", "-i", default="./input",
        help="含 .txt 缓存的目录（递归扫描 *.txt），默认 ./input",
    )
    parser.add_argument(
        "--term-map", "-t", default="./output/_work/term_map.jsonl",
        help="AI 生成的口径词表 term_map.jsonl 路径，默认 ./output/_work/term_map.jsonl",
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="候选清单输出路径，默认 {term-map 同目录}/candidates.jsonl",
    )
    args = parser.parse_args()

    input_dir = Path(args.input).resolve()
    term_map_path = Path(args.term_map).resolve()
    out_path = (Path(args.output).resolve() if args.output
                else term_map_path.parent / "candidates.jsonl")

    terms = load_terms(term_map_path)
    if not terms:
        print(f"ERROR: no terms loaded from {term_map_path}."
              " Write term_map.jsonl first (see METHODOLOGY.md step 2).")
        return

    txts = sorted(input_dir.rglob("*.txt"))
    if not txts:
        print(f"No .txt cache found in {input_dir}. Run extract.py first.")
        return

    all_hits: list[dict] = []
    for txt_path in txts:
        all_hits.extend(scan_file(txt_path, terms))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for hit in all_hits:
            f.write(json.dumps(hit, ensure_ascii=False) + "\n")

    files = len({h["文件"] for h in all_hits})
    print(f"Recall done: {len(all_hits)} hits across {files} files,"
          f" {len(terms)} terms -> {out_path}")


if __name__ == "__main__":
    main()

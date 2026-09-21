#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply L278+ Chinese translations and fix P179/P190 answers."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PART2 = ROOT / "data" / "questions3_part2.json"
Q3 = ROOT / "data" / "questions3.json"
CLEAN = ROOT / "exam bank 3.formatted.txt"
TRANS = ROOT / "data" / "quiz3_l278_translations.json"


def format_clean_txt(questions: list[dict]) -> str:
    chunks = [
        "California Real Estate Practice LV17 + Level 延伸（題庫三合併版）",
        "含原 LV17 100 題與 exam bank 3-2 延伸題。",
        "",
    ]
    for i, q in enumerate(questions, 1):
        chunks.append(f"Question {i}")
        stem = f"{q['stemEn']} {q['stemZh']}" if q.get("stemZh") else q["stemEn"]
        chunks.append(stem)
        for c in q["choices"]:
            line = f"({c['key']}) {c['en']}"
            if c.get("zh"):
                line += f" {c['zh']}"
            chunks.append(line)
        chunks.append(f"【正確答案】 ({q['answer']})")
        chunks.append("【詳細深度解析】")
        chunks.append(q.get("explanation") or "")
        chunks.append("")
    return "\n".join(chunks).rstrip() + "\n"


def apply_patch(q: dict, patch: dict) -> None:
    if patch.get("stemEn"):
        q["stemEn"] = patch["stemEn"]
    q["stemZh"] = patch.get("stemZh") or q.get("stemZh") or ""
    if patch.get("answer"):
        q["answer"] = patch["answer"]
    for c in q["choices"]:
        key = c["key"]
        if key in patch.get("choices", {}):
            pc = patch["choices"][key]
            if pc.get("en"):
                c["en"] = pc["en"]
            c["zh"] = pc.get("zh") or c.get("zh") or ""
    expl_zh = patch.get("explanationZh") or ""
    if expl_zh:
        q["explanation"] = expl_zh


def main() -> None:
    trans = json.loads(TRANS.read_text(encoding="utf-8"))
    part2 = json.loads(PART2.read_text(encoding="utf-8"))
    applied = 0
    missing = []

    for q in part2:
        pid = q.get("id", "")
        if pid not in trans:
            if int(re.sub(r"\D", "", pid) or "0") >= 179:
                missing.append(pid)
            continue
        apply_patch(q, trans[pid])
        applied += 1

    PART2.write_text(json.dumps(part2, ensure_ascii=False, indent=2), encoding="utf-8")

    base = [
        q
        for q in json.loads(Q3.read_text(encoding="utf-8"))
        if re.fullmatch(r"L\d{3}", q.get("id", "")) and int(q["id"][1:]) <= 100
    ]
    merged = base + []
    for i, q in enumerate(part2, 1):
        merged.append(
            {
                "id": f"L{100 + i:03d}",
                "source": q.get("source") or "LV 練習延伸",
                "stemEn": q["stemEn"],
                "stemZh": q.get("stemZh") or "",
                "choices": q["choices"],
                "answer": q["answer"],
                "explanation": q.get("explanation") or "",
            }
        )
    Q3.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    CLEAN.write_text(format_clean_txt(merged), encoding="utf-8")

    for lid in ("L278", "L289", "L332"):
        hit = next((q for q in merged if q["id"] == lid), None)
        if hit:
            print(lid, hit["answer"], hit["stemEn"][:60])
            print("  stemZh", (hit.get("stemZh") or "")[:50])
            print("  A zh", next(c["zh"] for c in hit["choices"] if c["key"] == "A")[:40])

    part = [q for q in merged if int(q["id"][1:]) >= 278]
    no_stem = sum(1 for q in part if not (q.get("stemZh") or "").strip())
    no_choice = sum(1 for q in part if any(not (c.get("zh") or "").strip() for c in q["choices"]))
    print("applied", applied, "missing", missing)
    print("L278+ missing stemZh", no_stem, "missing choice zh", no_choice)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append exam bank 3-2 parsed questions to the end of questions3.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "questions3.json"
PART2 = ROOT / "data" / "questions3_part2.json"
CLEAN = ROOT / "exam bank 3.formatted.txt"


def minimal_expl(q: dict) -> str:
    ans = q["answer"]
    choice = next(c for c in q["choices"] if c["key"] == ans)
    label = choice.get("zh") or choice.get("en") or ans
    stem = q.get("stemZh") or q.get("stemEn") or ""
    return (
        f"正確選項 ({ans})：{label}\n"
        f"題幹重點：{stem[:120]}\n"
        "【考試提示】先對照選項定義與題幹要件；若原文解析缺失，請回查 exam bank 3-2.txt 同題補充。"
    )


def format_clean_txt(questions: list[dict]) -> str:
    chunks = [
        "California Real Estate Practice LV17 + Level 延伸（題庫三合併版）",
        "含原 LV17 100 題與 exam bank 3-2 延伸題。",
        "",
    ]
    for i, q in enumerate(questions, 1):
        chunks.append(f"Question {i}")
        stem = q["stemEn"]
        if q.get("stemZh"):
            stem = f"{q['stemEn']} {q['stemZh']}"
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


def main():
    base = json.loads(BASE.read_text(encoding="utf-8"))
    part2 = json.loads(PART2.read_text(encoding="utf-8"))

    # Keep only original LV17 bank (L001–L100); drop any prior append
    base = [q for q in base if re.fullmatch(r"L\d{3}", q.get("id", "")) and int(q["id"][1:]) <= 100]

    appended = []
    for i, q in enumerate(part2, 1):
        expl = (q.get("explanation") or "").strip()
        if not expl:
            expl = minimal_expl(q)
        new_id = f"L{100 + i:03d}"
        appended.append(
            {
                "id": new_id,
                "source": q.get("source") or "LV 練習延伸",
                "stemEn": q["stemEn"],
                "stemZh": q.get("stemZh") or "",
                "choices": q["choices"],
                "answer": q["answer"],
                "explanation": expl,
            }
        )

    merged = base + appended
    BASE.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    CLEAN.write_text(format_clean_txt(merged), encoding="utf-8")

    print(f"base LV17: {len(base)}")
    print(f"appended from 3-2: {len(appended)}")
    print(f"merged total: {len(merged)} -> {BASE}")
    print(f"ids: {merged[0]['id']} .. {merged[99]['id']} + {merged[100]['id']} .. {merged[-1]['id']}")
    print(f"formatted -> {CLEAN}")


if __name__ == "__main__":
    main()

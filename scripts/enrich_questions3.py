#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge trap-focused enrichments into data/questions3.json."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
OUT = ROOT / "data" / "questions3.json"
CLEAN = ROOT / "exam bank 3.formatted.txt"

from _enrich_pack_1 import PACK as PACK1, CHOICE_ZH_FIX as FIX1  # noqa: E402
from _enrich_pack_2 import PACK as PACK2, CHOICE_ZH_FIX as FIX2  # noqa: E402

PACK = {**PACK1, **PACK2}
CHOICE_ZH_FIX = {**FIX1, **FIX2}


def zh_core(explanation: str) -> str:
    """Keep Chinese analysis; drop trailing English dump."""
    text = (explanation or "").strip()
    # Remove English： blocks
    text = re.split(r"\nEnglish[：:]", text, maxsplit=1)[0].strip()
    text = re.sub(r"^正確選項\s*\([A-D]\)\s*解析[：:]\s*", "", text).strip()
    # Drop old short exam tip lines; packs replace them
    text = re.sub(r"\n考試陷阱[^\n]*", "", text).strip()
    return text


def build_explanation(q: dict, pack: dict) -> str:
    ans = q["answer"]
    core = zh_core(q.get("explanation", ""))
    why = (pack.get("why") or "").strip()
    traps = (pack.get("traps") or "").strip()
    extend = (pack.get("extend") or "").strip()
    wrong = pack.get("wrong") or {}

    parts: list[str] = []
    parts.append(f"正確選項 ({ans}) 深度解析：")
    if core:
        parts.append(core)
    if why:
        parts.append("")
        parts.append("【再講清楚一點】")
        parts.append(why)

    parts.append("")
    parts.append("【干擾選項拆解｜為何不能選】")
    for c in q["choices"]:
        if c["key"] == ans:
            continue
        label = c.get("zh") or c.get("en") or ""
        reason = (wrong.get(c["key"]) or "").strip()
        if not reason:
            reason = "此選項與題幹法律要件或事實條件不符，屬干擾項。"
        parts.append(f"({c['key']}) {label}")
        parts.append(f"→ {reason}")

    if traps:
        parts.append("")
        parts.append("【考試陷阱】")
        parts.append(traps)

    if extend:
        parts.append("")
        parts.append("【延伸考點／對照記憶】")
        parts.append(extend)

    return "\n".join(parts).strip()


def format_clean_txt(questions: list[dict]) -> str:
    chunks = [
        "California Real Estate Practice LV17 Assessment（中英對照＋陷阱強化版）",
        "Topics: Listing Agreements, Disclosures/TDS, Contracts, Agency, CMA/Appraisal, Income Approach, Environmental Hazards, Fair Housing.",
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
    qs = json.loads(OUT.read_text(encoding="utf-8"))
    missing = []
    for q in qs:
        qid = q["id"]
        # Fix bad choice zh
        fixes = CHOICE_ZH_FIX.get(qid) or {}
        for c in q["choices"]:
            if c["key"] in fixes:
                c["zh"] = fixes[c["key"]]

        pack = PACK.get(qid)
        if not pack:
            missing.append(qid)
            continue
        q["explanation"] = build_explanation(q, pack)

    if missing:
        raise SystemExit(f"Missing enrichment packs for: {missing}")

    OUT.write_text(json.dumps(qs, ensure_ascii=False, indent=2), encoding="utf-8")
    CLEAN.write_text(format_clean_txt(qs), encoding="utf-8")

    avg = sum(len(q["explanation"]) for q in qs) / len(qs)
    # sanity: answer zh unique among choices
    dup_bugs = []
    for q in qs:
        ans_zh = next(c["zh"] for c in q["choices"] if c["key"] == q["answer"])
        for c in q["choices"]:
            if c["key"] != q["answer"] and c.get("zh") == ans_zh and ans_zh:
                dup_bugs.append(f"{q['id']}:{c['key']}")

    print(f"Enriched {len(qs)} questions -> {OUT}")
    print(f"Formatted text -> {CLEAN}")
    print(f"avg explanation length: {avg:.0f} chars")
    print(f"remaining duplicate choiceZh bugs: {dup_bugs}")


if __name__ == "__main__":
    main()

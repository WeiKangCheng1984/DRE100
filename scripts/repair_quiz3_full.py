#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix quiz3 part2: sync answers from explanations/source; remove only malformed rows."""
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "exam bank 3-2.txt"
PART2 = ROOT / "data" / "questions3_part2.json"
Q3 = ROOT / "data" / "questions3.json"
CLEAN = ROOT / "exam bank 3.formatted.txt"
REPORT = ROOT / "scripts" / "_quiz3_repair_report.json"

MARK = re.compile(r"\[\s*正確答案\s*\]|【\s*正確答案\s*】", re.I)
LETTERED = re.compile(r"^\s*[\(\[]?([A-D])[\)\].:、]\s*(.+)$", re.I)
NUMBERED = re.compile(r"^\s*(\d{1,3})\.\s*")
OPTION_CORRECT = re.compile(r"選項\s*([A-D])\s*[（(]\s*正確", re.I)
KEYS = "ABCD"


def tidy(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    return re.sub(r"\s+", " ", text.replace("\u200b", "").replace("\ufeff", "")).strip()


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").lower().replace("'", "'")
    s = re.sub(r"[^a-z0-9%$]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def stem_fp(stem: str) -> str:
    s = NUMBERED.sub("", tidy(stem))
    s = re.split(r"[\u3400-\u9fff]", s, maxsplit=1)[0]
    return norm(s)[:100]


def choice_match(a: str, b: str) -> bool:
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    shorter, longer = (na, nb) if len(na) <= len(nb) else (nb, na)
    if len(shorter) < 8:
        return shorter == longer
    if len(shorter) >= 10 and shorter in longer:
        return True
    ta, tb = set(na.split()), set(nb.split())
    if len(ta) < 2 or len(tb) < 2:
        return False
    inter = len(ta & tb)
    return inter == min(len(ta), len(tb)) and inter / max(len(ta), len(tb)) >= 0.85


def map_text(text: str, choices: list[dict]) -> str:
    hits = []
    for c in choices:
        if choice_match(c["en"], text) or (c.get("zh") and choice_match(c["zh"], text)):
            hits.append((len(norm(c["en"])), c["key"]))
    if not hits:
        return ""
    hits.sort(reverse=True)
    keys = {h[1] for h in hits}
    return hits[0][1] if len(keys) == 1 else ""


def is_malformed(q: dict) -> bool:
    stem = q.get("stemEn") or ""
    if len(stem) < 12:
        return True
    if re.match(r"^[BCD][、,，]", stem):
        return True
    if re.match(r"^(?:Architect|Trucker|💡)", stem):
        return True
    for c in q.get("choices", []):
        en = c.get("en") or ""
        if "💡" in en or "觀念金句" in en or "Mechanic's Lien 只保護" in en:
            return True
        if re.search(r"[\u3400-\u9fff]{8,}", en):
            return True
        if en.endswith(")") and en.count("(") == 0 and len(en) < 40:
            return True
    return False


def answer_from_explanation(q: dict) -> tuple[str, str]:
    expl = q.get("explanation") or ""

    # 正確答案: avoid paying property taxes(避免...)
    m = re.search(r"正確答案[：:]\s*(?:\n\s*)?(.+?)(?:[\(（]|$)", expl, re.S)
    if m:
        key = map_text(m.group(1).strip(), q["choices"])
        if key:
            return key, "expl_正確答案_line"

    m = re.search(r"[（(]正解[）)]\s*([^\n]+)", expl)
    if m:
        key = map_text(m.group(1).strip(), q["choices"])
        if key:
            return key, "expl_正解_paren"

    m = re.search(r"正確答案[：:]\s*([A-D])\s*[\(（]", expl)
    if m:
        letter = m.group(1).upper()
        if letter in {c["key"] for c in q["choices"]}:
            return letter, "expl_letter_paren"

    m = OPTION_CORRECT.search(expl)
    if m:
        return m.group(1).upper(), "expl_option_correct"

    for letter in KEYS:
        if re.search(rf"^{letter}[（(]正確", expl, re.M | re.I):
            return letter, f"expl_{letter}_正確"

    return "", ""


def sync_expl_prefix(q: dict) -> None:
    valid = {c["key"] for c in q["choices"]}
    if q.get("answer") not in valid:
        return
    choice = next(c for c in q["choices"] if c["key"] == q["answer"])
    label = choice.get("zh") or choice.get("en") or q["answer"]
    prefix = f"正確選項 ({q['answer']})：{label}"
    expl = re.sub(r"^正確選項\s*\([A-D]\)[^\n]*\n?", "", (q.get("explanation") or "").strip())
    q["explanation"] = prefix if not expl else prefix + "\n" + expl


MECHANIC_LIEN = {
    "source": "LV 練習延伸：Level 4",
    "stemEn": "Which of the following people would NOT qualify to file a mechanic's lien in California?",
    "stemZh": "下列哪一個人「沒有資格」在加州提出施工留置權（Mechanic's Lien）的申請？",
    "choices": [
        {"key": "A", "en": "apartment locator", "zh": "公寓包租/代尋仲介"},
        {"key": "B", "en": "architect", "zh": "建築師"},
        {"key": "C", "en": "trucker", "zh": "工程運力司機 / 廢土與建材運輸者"},
        {"key": "D", "en": "a licensed land surveyor", "zh": "持照土地測量師"},
    ],
    "answer": "A",
    "explanation": (
        "正確選項 (A)：公寓包租/代尋仲介\n"
        "解析\n"
        "加州民法（California Civil Code § 8400）對有資格提出 Mechanic's Lien 的對象有明確的法律界定："
        "必須是對該不動產的「實體改善工程（Work of Improvement）」直接提供勞務、專業設計、施工或建材的人。\n"
        "A（正確 - 無資格）：Apartment Locator（公寓尋屋/租賃仲介）提供的是租貸媒合等行銷/仲介服務，"
        "並未對房屋實體結構或土地進行任何改善或建造工程，因此完全不具備申請 Mechanic's Lien 的法定資格。\n"
        "B、C、D（具備資格）：Architect（建築師）、Trucker（運輸司機）與 Licensed Land Surveyor（測量師）"
        "皆屬依法可申請施工留置權的對象。"
    ),
}


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


def main() -> None:
    part2 = json.loads(PART2.read_text(encoding="utf-8"))
    answer_fixed: list[dict] = []
    removed: list[dict] = []
    rebuilt: list[dict] = []

    # Pass 1: fix answers from explanation for all questions
    for q in part2:
        old = q["answer"]
        new, method = answer_from_explanation(q)
        if new and new != old:
            q["answer"] = new
            answer_fixed.append(
                {"id": q["id"], "old": old, "new": new, "method": method, "stem": q["stemEn"][:70]}
            )
        sync_expl_prefix(q)

    # Pass 2: remove/replace only malformed rows
    fixed_pool: list[dict] = []
    mechanic_fp = stem_fp(MECHANIC_LIEN["stemEn"])
    has_mechanic = any(
        not is_malformed(q) and stem_fp(q["stemEn"]) == mechanic_fp for q in part2
    )

    for q in part2:
        if not is_malformed(q):
            fixed_pool.append(q)
            continue

        if q.get("stemEn") == "B、C、D" or "💡" in json.dumps(q.get("choices", []), ensure_ascii=False):
            if has_mechanic:
                removed.append({"id": q["id"], "reason": "malformed_dup", "stem": q["stemEn"][:70]})
            else:
                q.update(MECHANIC_LIEN)
                sync_expl_prefix(q)
                rebuilt.append({"id": q["id"], "stem": q["stemEn"][:70]})
                has_mechanic = True
                fixed_pool.append(q)
        else:
            removed.append({"id": q["id"], "reason": "malformed", "stem": q["stemEn"][:70]})

    print("answer_fixed", len(answer_fixed))
    print("rebuilt", len(rebuilt))
    print("removed", len(removed))
    print("final", len(fixed_pool))
    print("dist", Counter(q["answer"] for q in fixed_pool))

    for row in answer_fixed[:30]:
        print("FIX", row["id"], row["old"], "->", row["new"], row["method"], row["stem"][:50])

    PART2.write_text(json.dumps(fixed_pool, ensure_ascii=False, indent=2), encoding="utf-8")

    base = [
        q
        for q in json.loads(Q3.read_text(encoding="utf-8"))
        if re.fullmatch(r"L\d{3}", q.get("id", "")) and int(q["id"][1:]) <= 100
    ]
    appended = []
    for i, q in enumerate(fixed_pool, 1):
        appended.append(
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
    merged = base + appended
    Q3.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    CLEAN.write_text(format_clean_txt(merged), encoding="utf-8")

    for lid in ("L169", "L170", "L214"):
        hit = next((q for q in appended if q["id"] == lid), None)
        if hit:
            print("CHECK", lid, hit["answer"], hit["stemEn"][:65])

    REPORT.write_text(
        json.dumps(
            {"answer_fixed": answer_fixed, "rebuilt": rebuilt, "removed": removed, "count": len(appended)},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-parse exam bank 3-2 with improved inference, then apply mark-only answer fixes."""
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

MARK = re.compile(r"\[\s*正確答案\s*\]|【\s*正確答案\s*】", re.I)
LETTERED = re.compile(r"^\s*[\(\[]?([A-D])[\)\].:、]\s*(.+)$", re.I)
NUMBERED = re.compile(r"^\s*(\d{1,3})\.\s*")
OPTION_CORRECT = re.compile(r"選項\s*([A-D])\s*[（(]\s*正確", re.I)


def tidy(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    return re.sub(r"\s+", " ", text.replace("\u200b", "").replace("\ufeff", "")).strip()


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").lower().replace("’", "'")
    s = re.sub(r"[^a-z0-9%$]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def eng_head(text: str) -> str:
    text = MARK.sub("", text or "")
    text = re.sub(r"^\s*[\(\[]?[A-D][\)\].:、]\s*", "", text, flags=re.I)
    text = tidy(text)
    return tidy(re.split(r"[\u3400-\u9fff]|（譯|\(譯", text, maxsplit=1)[0].strip(" -:（("))


def choice_match(a: str, b: str) -> bool:
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    shorter, longer = (na, nb) if len(na) <= len(nb) else (nb, na)
    if len(shorter) < 12:
        return shorter == longer
    return shorter in longer


def map_text(text: str, choices: list[dict]) -> str:
    hits = [c["key"] for c in choices if choice_match(c["en"], text)]
    return hits[0] if len(set(hits)) == 1 else ""


def stem_key(stem: str) -> str:
    s = NUMBERED.sub("", tidy(stem))
    s = re.split(r"[\u3400-\u9fff]", s, maxsplit=1)[0]
    return norm(s)[:120]


def window_for(src_lines: list[str], stem: str, choices: list[dict]) -> list[str] | None:
    key = stem_key(stem)
    if len(key) < 14:
        return None
    best = None
    for i, line in enumerate(src_lines):
        ln = stem_key(line)
        if not ln:
            continue
        if not (ln.startswith(key[:55]) or key.startswith(ln[:55])):
            continue
        end = min(len(src_lines), i + 75)
        for j in range(i + 1, end):
            t = tidy(src_lines[j])
            if re.match(r"(?i)^Level\s*\d+\s+Assessment", t):
                end = j
                break
            if NUMBERED.match(t) and len(re.findall(r"[A-Za-z]+", t)) >= 4:
                end = j
                break
        w = src_lines[i:end]
        blob = norm("\n".join(w))
        hit = sum(1 for c in choices if norm(c["en"])[:12] and norm(c["en"])[:12] in blob)
        if best is None or hit > best[0]:
            best = (hit, w)
    return best[1] if best else None


def mark_or_option_answer(window: list[str], choices: list[dict]) -> tuple[str, str]:
    joined = "\n".join(window)

    for line in window:
        if not MARK.search(line):
            continue
        m = LETTERED.match(tidy(line))
        body = eng_head(m.group(2) if m else line)
        key = map_text(body, choices)
        if key:
            return key, "mark_text"

    m = OPTION_CORRECT.search(joined)
    if m:
        letter = m.group(1).upper()
        labelled = {}
        for line in window:
            lm = LETTERED.match(tidy(line))
            if lm and lm.group(1).upper() not in labelled:
                labelled[lm.group(1).upper()] = eng_head(lm.group(2))
        if letter in labelled:
            key = map_text(labelled[letter], choices)
            if key:
                return key, f"option_labelled:{letter}"
        stored = next((c["en"] for c in choices if c["key"] == letter), "")
        if stored and norm(stored)[:10] in norm(joined):
            return letter, f"option_letter:{letter}"

    m = re.search(r"(?m)^([A-Za-z][A-Za-z'’\-]{2,40})\s*[\(（]\s*Correct\s*[\)）]", joined)
    if m:
        name = norm(m.group(1))
        for c in choices:
            if norm(c["en"]).startswith(name) or re.search(rf"\b{re.escape(name)}\b", norm(c["en"])):
                return c["key"], "name_correct"

    m = re.search(r"答案就是\s*([^\n。．.]{2,80})", joined)
    if m:
        key = map_text(m.group(1), choices)
        if key:
            return key, "答案就是"

    return "", ""


def sync_expl(q: dict) -> None:
    choice = next(c for c in q["choices"] if c["key"] == q["answer"])
    label = choice.get("zh") or choice["en"]
    prefix = f"正確選項 ({q['answer']})：{label}"
    expl = re.sub(r"^正確選項\s*\([A-D]\)[^\n]*\n?", "", (q.get("explanation") or "").strip())
    q["explanation"] = prefix if not expl else prefix + "\n" + expl


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
    import importlib.util

    spec = importlib.util.spec_from_file_location("p32", ROOT / "scripts" / "parse_exam_bank3_2.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    mod.main()

    part2 = json.loads(PART2.read_text(encoding="utf-8"))
    src_lines = SRC.read_text(encoding="utf-8").splitlines()

    changes = []
    confirmed = 0
    for q in part2:
        old = q["answer"]
        window = window_for(src_lines, q["stemEn"], q["choices"])
        if not window:
            sync_expl(q)
            continue
        new, method = mark_or_option_answer(window, q["choices"])
        if new and new != old:
            changes.append(
                {
                    "id": q["id"],
                    "old": old,
                    "new": new,
                    "method": method,
                    "stem": q["stemEn"][:90],
                    "old_en": next(c["en"] for c in q["choices"] if c["key"] == old)[:70],
                    "new_en": next(c["en"] for c in q["choices"] if c["key"] == new)[:70],
                }
            )
            q["answer"] = new
        elif new:
            confirmed += 1
        sync_expl(q)

    print("mark/option confirmed", confirmed)
    print("mark/option changed", len(changes))
    for row in changes:
        print(f"CHG {row['id']} {row['old']}->{row['new']} [{row['method']}] {row['old_en'][:40]} => {row['new_en'][:40]}")

    PART2.write_text(json.dumps(part2, ensure_ascii=False, indent=2), encoding="utf-8")

    base = [
        q
        for q in json.loads(Q3.read_text(encoding="utf-8"))
        if re.fullmatch(r"L\d{3}", q.get("id", "")) and int(q["id"][1:]) <= 100
    ]
    appended = []
    for i, q in enumerate(part2, 1):
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

    # Audit: for every [正確答案] mark in source lettered lines, check matching Q
    mismatch = []
    for q in appended:
        window = window_for(src_lines, q["stemEn"], q["choices"])
        if not window:
            continue
        for line in window:
            if not MARK.search(line):
                continue
            m = LETTERED.match(tidy(line))
            body = eng_head(m.group(2) if m else line)
            key = map_text(body, q["choices"])
            if key and key != q["answer"]:
                mismatch.append((q["id"], q["answer"], key, body[:60], q["stemEn"][:60]))
    print("post-audit mark mismatches", len(mismatch))
    for row in mismatch[:20]:
        print("MIS", row)

    report = {
        "changed": changes,
        "confirmed_marks": confirmed,
        "count": len(appended),
        "dist": dict(Counter(q["answer"] for q in appended)),
        "mark_mismatches": [
            {"id": a, "stored": b, "marked_key": c, "text": d, "stem": e}
            for a, b, c, d, e in mismatch
        ],
    }
    (ROOT / "scripts" / "_quiz3_answer_fix.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("final", len(appended), report["dist"])


if __name__ == "__main__":
    main()

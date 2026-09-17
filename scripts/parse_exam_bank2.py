#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "exam bank 2.txt"
OUT = ROOT / "data" / "questions2.json"

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
SET_HEADER_RE = re.compile(r"^California Real Estate Salesperson Examination: Master Practice Set(?:\s+(\d+))?", re.I)
QUESTION_LABEL_RE = re.compile(r"^Question\s+(\d+)\s*$")
NUMBERED_Q_RE = re.compile(r"^(\d+)\.\s+(\S.*)$")
CHOICE_RE = re.compile(r"^\(([A-D])\)\s*(.*)$")
ANSWER_RE = re.compile(r"^【正確答案】\s*\(([A-D])\)")
EXPLAIN_RE = re.compile(r"^【詳細深度解析】\s*$")

SET_SOURCES = {
    1: "練習集 1：產權、租賃與水權",
    2: "練習集 2：產權、租賃與水權",
    3: "練習集 3：地役權、公權力與代理",
    4: "練習集 4：契約、代理與產權",
    5: "練習集 5：鑑價、契約與投資",
    6: "練習集 6：融資、鑑價與公平住房",
    7: "練習集 7：融資、公平住房與反托拉斯",
    8: "練習集 8：融資、公平住房與反托拉斯",
}


def split_stem(text: str) -> tuple[str, str]:
    text = text.strip()
    if not text:
        return "", ""
    m = CJK_RE.search(text)
    if not m:
        return re.sub(r"\s+", " ", text).strip(), ""
    en = text[: m.start()].strip()
    zh = text[m.start() :].strip()
    return re.sub(r"\s+", " ", en).strip(), re.sub(r"\s+", " ", zh).strip()


def is_question_start(line: str):
    s = line.strip()
    m = QUESTION_LABEL_RE.match(s)
    if m:
        return int(m.group(1)), ""
    m = NUMBERED_Q_RE.match(s)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 40:
            return n, m.group(2).strip()
    return None


def parse_block(block: str, source: str):
    lines = block.splitlines()
    if not lines:
        return None
    start = is_question_start(lines[0])
    if not start:
        return None
    _num, rest = start
    body = []
    if rest:
        body.append(rest)
    body.extend(lines[1:])

    stem_lines = []
    choice_map = {}
    answer = ""
    expl_lines = []
    mode = "stem"
    for ln in body:
        s = ln.strip()
        if mode == "stem":
            if CHOICE_RE.match(s):
                mode = "choices"
            elif ANSWER_RE.match(s):
                mode = "answer"
            elif EXPLAIN_RE.match(s):
                mode = "expl"
            else:
                if s:
                    stem_lines.append(s)
                continue
        if mode == "choices":
            cm = CHOICE_RE.match(s)
            if cm:
                choice_map[cm.group(1)] = cm.group(2).strip()
                continue
            if ANSWER_RE.match(s):
                mode = "answer"
            elif EXPLAIN_RE.match(s):
                mode = "expl"
                continue
            elif s:
                last = ["A", "B", "C", "D"]
                for key in reversed(last):
                    if key in choice_map:
                        choice_map[key] = (choice_map[key] + " " + s).strip()
                        break
                continue
        if mode == "answer":
            am = ANSWER_RE.match(s)
            if am:
                answer = am.group(1)
            if EXPLAIN_RE.match(s):
                mode = "expl"
            continue
        if mode == "expl":
            if EXPLAIN_RE.match(s):
                continue
            if s:
                expl_lines.append(s)

    stem_en, stem_zh = split_stem(" ".join(stem_lines))
    choices = []
    for key in ("A", "B", "C", "D"):
        raw_choice = choice_map.get(key, "").strip()
        if not raw_choice:
            return {
                "_error": True,
                "source": source,
                "stemEn": stem_en,
                "missing": key,
            }
        en, zh = split_stem(raw_choice)
        choices.append({"key": key, "en": en, "zh": zh})
    explanation = "\n".join(expl_lines).strip()
    if not stem_en or not answer:
        return {
            "_error": True,
            "source": source,
            "stemEn": stem_en,
            "answer": answer,
            "n_choices": len(choices),
        }
    return {
        "source": source,
        "stemEn": stem_en,
        "stemZh": stem_zh,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
    }


def main():
    lines = SRC.read_text(encoding="utf-8").splitlines()
    starts = []
    current_set = 1
    last_qnum = 0
    for i, line in enumerate(lines):
        hm = SET_HEADER_RE.match(line.strip())
        if hm:
            current_set = int(hm.group(1) or 1)
            last_qnum = 0
            continue
        q = is_question_start(line)
        if not q:
            continue
        qnum, _rest = q
        if qnum == 1 and last_qnum > 1:
            current_set += 1
        last_qnum = qnum
        starts.append((i, current_set, qnum))

    questions = []
    errors = []
    for idx, (start, set_no, qnum) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        block = "\n".join(lines[start:end])
        source = SET_SOURCES.get(set_no, f"練習集 {set_no}")
        q = parse_block(block, source)
        if not q or q.get("_error"):
            errors.append(q or {"_error": True, "set": set_no, "q": qnum, "preview": block[:180]})
            continue
        questions.append(q)

    out = []
    for i, q in enumerate(questions, 1):
        out.append(
            {
                "id": f"H{i:03d}",
                "source": q["source"],
                "stemEn": q["stemEn"],
                "stemZh": q["stemZh"],
                "choices": q["choices"],
                "answer": q["answer"],
                "explanation": q["explanation"],
            }
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(out)} questions -> {OUT}")
    print(f"Starts detected: {len(starts)}")
    print(f"Errors: {len(errors)}")
    from collections import Counter

    print("sources:", Counter(q["source"] for q in out))
    no_zh = [q["id"] for q in out if not q["stemZh"]]
    print("missing stemZh:", no_zh)
    no_choice_zh = [
        q["id"] for q in out if any(not (c.get("zh") or "").strip() for c in q["choices"])
    ]
    print("missing choiceZh:", no_choice_zh)
    if errors:
        for e in errors[:20]:
            print("---", e)


if __name__ == "__main__":
    main()

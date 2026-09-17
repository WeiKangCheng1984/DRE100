#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse plus.txt into data/notes.json for the study-notes module."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "plus.txt"
OUT = ROOT / "data" / "notes.json"

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
PDF_RE = re.compile(r"^PDF(?:\+\s*\d+)?$", re.I)
CHAPTER_NUM_RE = re.compile(r"^([一二三四五六七八九十]+)、\s*(.+)$")
NUMBERED_RE = re.compile(r"^(\d+)\.\s+(\S.*)$")
PIPE_TITLE_RE = re.compile(r"^(.+?)｜(.+)$")
EN_PREFIX_RE = re.compile(r"^(EN|ZH)\s*[:：]\s*(.*)$", re.I)
LATEX_ARROW_RE = re.compile(r"\$\\rightarrow\$")

CHAPTERS = [
    {"id": "intro", "title": "導論與基礎", "titleEn": "Introduction"},
    {"id": "ownership", "title": "所有權、產權與租賃", "titleEn": "Ownership & Estates"},
    {"id": "easement", "title": "地役權、公權力與土地管制", "titleEn": "Easements & Public Power"},
    {"id": "agency", "title": "代理、詐欺與揭露", "titleEn": "Agency & Disclosure"},
    {"id": "contract", "title": "契約、委託與訂金", "titleEn": "Contracts & Listings"},
    {"id": "appraisal", "title": "估價、折舊與投資原則", "titleEn": "Appraisal & Investment"},
    {"id": "finance", "title": "融資、貸款與抵押", "titleEn": "Financing & Mortgages"},
    {"id": "fairhousing", "title": "公平住房與反托拉斯", "titleEn": "Fair Housing & Antitrust"},
    {"id": "grammar", "title": "長難句文法要點", "titleEn": "Exam Sentence Grammar"},
]


def clean_line(s: str) -> str:
    s = s.strip()
    s = LATEX_ARROW_RE.sub("→", s)
    s = s.replace("$$", "")
    s = re.sub(r"\s+", " ", s)
    return s


def is_junk(s: str) -> bool:
    if not s:
        return True
    if PDF_RE.match(s):
        return True
    if s in {"PDF+", "PDF + 1", "PDF+ 1", "PDF+ 2", "PDF+ 3", "PDF+ 4"}:
        return True
    return False


def chapter_from_header(title: str) -> str | None:
    t = title.upper()
    if "PROPERTY OWNERSHIP" in t or t.startswith("ESTATES") or "LESS THAN FREEHOLD" in t:
        return "ownership"
    if (
        "EASEMENT" in t
        or "GOVERNMENT POWER" in t
        or "ZONING" in t
        or "EMINENT DOMAIN" in t
        or "CONDEMNATION" in t
    ):
        return "easement"
    if (
        "AGENCY" in t
        or "REALTOR" in t
        or "ACOLD" in t
        or "DUAL AGENCY" in t
        or "UNIVERSAL" in t
        or "PRINCIPAL" in t
        or "FRAUD" in t
        or "NEGLIGENCE" in t
        or "STIGMATIZED" in t
    ):
        return "agency"
    if (
        "CONTRACT" in t
        or "LISTING" in t
        or "EARNEST" in t
        or "MLS" in t
        or "OPTION" in t
        or "FOUR ESSENTIAL" in t
        or "VALIDITY" in t
        or "EXECUTED" in t
    ):
        return "contract"
    if (
        "DEPRECIATION" in t
        or "EFFECTIVE AGE" in t
        or "VALUE" in t
        or "ASSEMBLAGE" in t
        or "GROSS RENT" in t
        or "COST APPROACH" in t
        or "CAPITALIZATION" in t
        or "MARKET DATA" in t
        or "PROGRESSION" in t
        or "CONTRIBUTION" in t
        or "CONFORMITY" in t
        or "SUBSTITUTION" in t
        or "HIGHEST AND BEST" in t
        or "INVESTING" in t
        or "CO-OWNERSHIP" in t
    ):
        return "appraisal"
    if (
        "FINANCING" in t
        or "LOAN" in t
        or "TRUTH IN LENDING" in t
        or "AMORTIZATION" in t
        or "MORTGAGE MARKET" in t
        or "FHA" in t
        or "TRUST DEED" in t
        or "FORECLOSURE" in t
    ):
        return "finance"
    if (
        "FAIR HOUSING" in t
        or "AMERICANS WITH DISABILITIES" in t
        or "BLOCKBUSTING" in t
        or "SHERMAN" in t
        or "ANTITRUST" in t
        or "ANTI-TRUST" in t
    ):
        return "fairhousing"
    if "長難句" in title or "GRAMMAR" in t or "文法" in title:
        return "grammar"
    return None


def split_title(raw: str) -> tuple[str, str, str]:
    raw = raw.strip()
    m = PIPE_TITLE_RE.match(raw)
    if m:
        en, zh = m.group(1).strip(), m.group(2).strip()
        return raw, en, zh
    m = re.match(r"^(.+?)[（(]([^)）]+)[)）]\s*$", raw)
    if m and CJK_RE.search(m.group(2)):
        return raw, m.group(1).strip(), m.group(2).strip()
    if CJK_RE.search(raw) and re.search(r"[A-Za-z]", raw):
        return raw, raw, ""
    return raw, raw, ""


GRAMMAR_SUB_PREFIXES = (
    "Main Clause",
    "Participle",
    "Concession",
    "Contrast Clause",
    "Relative Clause",
    "Prepositional",
    "Core Legal",
    "Temporal",
    "Object Clause",
    "Modifier",
    "Conditional Clause",
    "Condition &",
    "Time Clause",
    "Adverbial",
    "Noun Clause",
    "Compound Predicate",
    "Non-restrictive",
    "Parallel",
    "Subject +",
    "Introductory",
)


def is_grammar_header(s: str) -> bool:
    return "Sentence Structure" in s or "文法解析" in s or "句型與文法" in s


def is_grammar_subsection(s: str) -> bool:
    m = NUMBERED_RE.match(s)
    if not m:
        return False
    rest = m.group(2).strip()
    if not rest:
        return False
    if rest.lower().find(" vs.") >= 0:
        return False
    if CJK_RE.match(rest[0]):
        return False
    return any(rest.startswith(k) for k in GRAMMAR_SUB_PREFIXES)


def is_major_intro_title(s: str) -> bool:
    keys = (
        "INTRODUCTION & DISCLAIMER",
        "WHAT IS A LICENSE?",
        "THE -OR AND -EE RULE",
        "PROPERTY OWNERSHIP｜",
        "Mortgagor vs. Mortgagee",
    )
    return any(s.startswith(k) for k in keys)


def is_topic_start(s: str, in_grammar: bool) -> bool:
    if is_grammar_header(s):
        return False
    if CHAPTER_NUM_RE.match(s):
        return True
    if NUMBERED_RE.match(s):
        if is_grammar_subsection(s):
            return False
        return True
    if in_grammar:
        return False
    if is_major_intro_title(s):
        return True
    return False


def flush_note(notes, current):
    if not current:
        return
    body = "\n".join(current["body"]).strip()
    grammar = "\n".join(current["grammar"]).strip()
    points = current["points"]
    if not body and not grammar and not current["sentenceEn"] and not points:
        return
    notes.append(current)


def attach_en_zh_points(current, lines_iter_unused=None):
    pass


def parse():
    raw_lines = SRC.read_text(encoding="utf-8").splitlines()
    lines = []
    for ln in raw_lines:
        s = clean_line(ln)
        if is_junk(s):
            continue
        lines.append(s)

    notes = []
    chapter_id = "intro"
    current = None
    mode = "body"  # body | sentence | grammar
    pending_en = ""

    def new_note(title_raw: str, ch_id: str):
        full, en, zh = split_title(title_raw)
        return {
            "chapterId": ch_id,
            "title": full,
            "titleEn": en,
            "titleZh": zh,
            "body": [],
            "points": [],
            "sentenceEn": "",
            "grammar": [],
            "examFocus": "",
        }

    def push_point(note, en, zh):
        en, zh = (en or "").strip(), (zh or "").strip()
        if not en and not zh:
            return
        note["points"].append({"en": en, "zh": zh})

    i = 0
    while i < len(lines):
        s = lines[i]

        if is_topic_start(s, mode == "grammar"):
            cm = CHAPTER_NUM_RE.match(s)
            mapped = chapter_from_header(cm.group(2) if cm else s)
            if mapped:
                chapter_id = mapped

            flush_note(notes, current)
            current = new_note(s, chapter_id)
            mode = "body"
            pending_en = ""
            i += 1
            continue

        if current is None:
            current = new_note("導論", chapter_id)
            mode = "body"

        if s.startswith("知識點整理"):
            mode = "body"
            i += 1
            continue

        if s.startswith("考試長難句"):
            mode = "sentence"
            i += 1
            continue

        if is_grammar_header(s):
            mode = "grammar"
            i += 1
            continue

        if s.startswith("重點考向") or s.startswith("解析重點") or s.startswith("(解析重點"):
            current["examFocus"] = (current["examFocus"] + " " + s).strip() if current["examFocus"] else s
            i += 1
            continue

        em = EN_PREFIX_RE.match(s)
        if em:
            kind, rest = em.group(1).upper(), em.group(2).strip()
            if kind == "EN":
                pending_en = rest
                if mode == "sentence" and rest.startswith('"'):
                    current["sentenceEn"] = rest.strip('"')
                    pending_en = ""
                    mode = "body"
                elif mode != "sentence":
                    current["body"].append("EN: " + rest)
            else:
                if pending_en:
                    push_point(current, pending_en, rest)
                    pending_en = ""
                else:
                    current["body"].append("ZH: " + rest)
                    if current["points"]:
                        last = current["points"][-1]
                        if last["en"] and not last["zh"]:
                            last["zh"] = rest
            i += 1
            continue

        if mode == "sentence":
            if s.startswith('"') or (s.startswith("“") or (len(s) > 40 and s[0].isalpha() and '"' in s)):
                q = s.strip().strip('"“”')
                if not current["sentenceEn"]:
                    current["sentenceEn"] = q
                else:
                    current["sentenceEn"] += " " + q
                i += 1
                continue
            mode = "body"

        if mode == "grammar":
            current["grammar"].append(s)
            i += 1
            continue

        # Term: English（中文） pattern or Term（中文）: English
        current["body"].append(s)
        i += 1

    flush_note(notes, current)

    # Post-process: pull EN/ZH pairs from body, trim sentence quotes, ids
    out_notes = []
    for idx, n in enumerate(notes, 1):
        body_lines = n["body"]
        points = list(n["points"])
        leftover = []
        pending = ""
        for ln in body_lines:
            em = EN_PREFIX_RE.match(ln)
            if em and em.group(1).upper() == "EN":
                pending = em.group(2).strip()
                continue
            if em and em.group(1).upper() == "ZH":
                zh = em.group(2).strip()
                if pending:
                    points.append({"en": pending, "zh": zh})
                    pending = ""
                else:
                    leftover.append(ln)
                continue
            leftover.append(ln)
        if pending:
            leftover.insert(0, "EN: " + pending)

        point_ens = {p["en"] for p in points if p.get("en")}
        cleaned_leftover = []
        for ln in leftover:
            em = EN_PREFIX_RE.match(ln)
            if em and em.group(1).upper() == "EN" and em.group(2).strip() in point_ens:
                continue
            cleaned_leftover.append(ln)
        body = "\n".join(cleaned_leftover).strip()
        sentence = n["sentenceEn"].strip().strip('"“”')
        grammar = "\n".join(n["grammar"]).strip()
        # Drop grammar lines that accidentally captured the next topic title
        grammar_lines = []
        for gl in grammar.split("\n") if grammar else []:
            if is_topic_start(gl, False):
                break
            grammar_lines.append(gl)
        grammar = "\n".join(grammar_lines).strip()
        # Skip empty shells
        if not body and not points and not sentence and not grammar:
            continue
        seen_en = set()
        uniq_points = []
        for p in points:
            key = (p.get("en") or "") + "||" + (p.get("zh") or "")
            if key in seen_en:
                continue
            seen_en.add(key)
            uniq_points.append(p)
        ch = next((c for c in CHAPTERS if c["id"] == n["chapterId"]), CHAPTERS[0])
        title = n["title"].rstrip("：:")
        title_en = n["titleEn"].rstrip("：:")
        title_zh = n["titleZh"].rstrip("：:")
        out_notes.append(
            {
                "id": f"N{idx:03d}",
                "chapterId": n["chapterId"],
                "chapter": ch["title"],
                "title": title,
                "titleEn": title_en,
                "titleZh": title_zh,
                "points": uniq_points,
                "body": body,
                "sentenceEn": sentence,
                "grammar": grammar,
                "examFocus": n["examFocus"].strip(),
            }
        )

    sentences = []
    for n in out_notes:
        if not n["sentenceEn"]:
            continue
        hint = ""
        if n["points"]:
            hint = n["points"][0].get("zh") or n["points"][0].get("en") or ""
        sentences.append(
            {
                "id": f"S{len(sentences) + 1:03d}",
                "noteId": n["id"],
                "chapterId": n["chapterId"],
                "chapter": n["chapter"],
                "title": n["title"],
                "titleEn": n["titleEn"],
                "titleZh": n["titleZh"],
                "en": n["sentenceEn"],
                "grammar": n["grammar"],
                "examFocus": n["examFocus"],
                "hintZh": hint,
            }
        )

    payload = {"chapters": CHAPTERS, "notes": out_notes, "sentences": sentences}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    from collections import Counter

    print(f"Wrote {len(out_notes)} notes -> {OUT}")
    print("by chapter:", Counter(n["chapterId"] for n in out_notes))
    print("with sentence:", sum(1 for n in out_notes if n["sentenceEn"]))
    print("sentence trainer items:", len(sentences))
    print("with grammar:", sum(1 for n in out_notes if n["grammar"]))
    print("with points:", sum(1 for n in out_notes if n["points"]))
    print("sample titles:")
    for n in out_notes[:8]:
        print(" ", n["id"], n["chapterId"], n["title"][:80])
    print("...")
    for n in out_notes[-5:]:
        print(" ", n["id"], n["chapterId"], n["title"][:80])


if __name__ == "__main__":
    parse()

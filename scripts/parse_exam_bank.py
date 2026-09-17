#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "exam bank.txt"
OUT = ROOT / "data" / "questions.json"

SECTION_HEADERS = [
    ("綜合題75題", "綜合題"),
    ("Contracts", "Contracts"),
    ("Financing", "Financing"),
    ("Laws of Agency", "Laws of Agency"),
    ("Practice and Disclosures", "Practice and Disclosures"),
    ("Property Ownership", "Property Ownership"),
    ("Transfer of Property", "Transfer of Property"),
    ("Valuation & Market Analysis", "Valuation & Market Analysis"),
    ("Vocabulary", "Vocabulary"),
]
NARRATION_RE = re.compile(r"^(風靜靜地吹過|老樹根|順著時光|我們順著|我們繼續|求學與探索)")
ANSWER_RE = re.compile(r"正確答案(?:是|：|:)\s*(.+)")
CHOICE_LETTER_RE = re.compile(r"^([a-dA-D])[\.\)]\s*(.*)$")
META_SKIP_RE = re.compile(r"^(Questions per attempt|題目與選項翻譯|題目與選項|選項：|答案解析|選項解析：?)\s*$", re.I)
KEYS = ["A", "B", "C", "D"]

def split_en_zh(text: str):
    text = text.strip()
    if not text:
        return "", ""
    idx = text.find("（")
    if idx >= 1:
        en = text[:idx].strip()
        zh = text[idx:].strip()
        if zh.startswith("（") and zh.endswith("）"):
            zh = zh[1:-1].strip()
        return en, zh
    idx = text.find("(")
    if idx >= 1 and re.search("[一-鿿]", text[idx:]):
        en = text[:idx].strip()
        zh = text[idx:].strip("() ").strip()
        return en, zh
    return text, ""

def normalize_match(s: str) -> str:
    s = s.lower().replace("…", "").replace("...", "")
    s = re.sub(r"[“”\"'`\.。，,；;：:\s]+", " ", s)
    parts = s.split()
    out = []
    for w in parts:
        if not out or out[-1] != w:
            out.append(w)
    return " ".join(out)

def is_question_start(line: str):
    s = line.strip()
    if not s:
        return None
    m = re.match(r"^第\s*([0-9一二三四五六七八九十]+)\s*題\s*(.*)$", s)
    if m:
        return m
    m = re.match(r"^(\d+)\.\s*(.*)$", s)
    if m and 1 <= int(m.group(1)) <= 80:
        return m
    return None

def cleanup_explanation(text: str) -> str:
    lines = []
    for ln in text.split("\n"):
        s = ln.strip()
        if not s or NARRATION_RE.match(s) or META_SKIP_RE.match(s):
            continue
        s = re.sub(r"\$\$?", "", s)
        s = s.replace(r"\text{", "").replace("}", "").replace(r"\frac{", "").replace("{", "")
        lines.append(s)
    return "\n".join(lines).strip()

def parse_choices_and_rest(lines):
    merged = []
    for line in lines:
        s = line.strip()
        if not s:
            if merged and merged[-1] != "":
                merged.append("")
            continue
        if s.startswith("（") and merged:
            i = len(merged) - 1
            while i >= 0 and merged[i] == "":
                i -= 1
            if i >= 0:
                merged[i] = merged[i].rstrip() + s
                continue
        merged.append(s)
    text = "\n".join(merged)
    ans_m = ANSWER_RE.search(text)
    answer_raw, explanation, body = "", "", text
    if ans_m:
        answer_raw = ans_m.group(1).strip()
        explanation = text[ans_m.end():].strip()
        parts = re.split(r"。\s+", answer_raw, maxsplit=1)
        if len(parts) == 2 and (parts[1].startswith(("概念","選擇","合法","代理","契約","金融","法規","估價")) or len(parts[1]) > 40):
            answer_raw = parts[0].strip() + "。"
            explanation = (parts[1] + "\n" + explanation).strip()
        body = text[:ans_m.start()]
    choice_src = body
    if "選項：" in body:
        choice_src = body.split("選項：", 1)[1]
    else:
        m = re.search(r"^[aA][\.\)]\s", body, re.M)
        if m:
            choice_src = body[m.start():]
    choice_lines = []
    for ln in choice_src.split("\n"):
        s = ln.strip()
        if not s or META_SKIP_RE.match(s) or s.startswith("題目"):
            continue
        choice_lines.append(s)
    lettered = []
    for s in choice_lines:
        m = CHOICE_LETTER_RE.match(s)
        if m:
            lettered.append((m.group(1).upper(), m.group(2).strip()))
    choices = []
    if len(lettered) >= 4:
        for key, val in lettered[:4]:
            en, zh = split_en_zh(val)
            choices.append({"key": key, "en": en, "zh": zh})
    else:
        for i, val in enumerate(choice_lines[:4]):
            en, zh = split_en_zh(val)
            choices.append({"key": KEYS[i], "en": en, "zh": zh})
    return choices, answer_raw.strip().rstrip("。").strip(), cleanup_explanation(explanation)

def extract_stem(block_lines):
    buf = []
    for ln in block_lines:
        s = ln.strip()
        if not s:
            if buf:
                break
            continue
        if s in ("選項：", "題目與選項翻譯", "題目與選項", "答案解析") or s.startswith("選項："):
            break
        if CHOICE_LETTER_RE.match(s) and buf:
            break
        if s.startswith("題目：") or s.startswith("題目:"):
            buf = [s]
            continue
        buf.append(s)
    stem = " ".join(buf)
    return re.sub(r"^題目[：:]\s*", "", stem).strip()

def match_answer(choices, answer_raw: str) -> str:
    if not answer_raw or not choices:
        return ""
    raw = answer_raw.strip()
    if re.match(r"^[a-dA-D]([\.\):：]|$)", raw):
        return raw[0].upper()
    norm = normalize_match(raw)
    for ch in choices:
        for c in [normalize_match(ch["en"]), normalize_match(ch["zh"]), normalize_match(ch["en"] + " " + ch["zh"])]:
            if c and norm == c:
                return ch["key"]
    best, best_score = "", 0
    for ch in choices:
        for c in [normalize_match(ch["en"]), normalize_match(ch["zh"]), normalize_match(ch["en"] + " " + ch["zh"])]:
            if not c:
                continue
            if norm == c or norm in c or c in norm:
                score = min(len(norm), len(c))
                if score > best_score:
                    best_score, best = score, ch["key"]
            prefix = norm[:24]
            if prefix and prefix in c and len(prefix) > best_score:
                best_score, best = len(prefix), ch["key"]
            at, ct = set(norm.split()), set(c.split())
            if at and len(at & ct) / max(len(at), 1) >= 0.7:
                score = len(at & ct) * 3
                if score > best_score:
                    best_score, best = score, ch["key"]
    return best

def split_sections(raw: str):
    lines = raw.splitlines()
    markers = []
    for i, line in enumerate(lines):
        s = line.strip()
        for header, source in SECTION_HEADERS:
            if s == header or s.startswith(header + ":") or s == header + ":":
                markers.append((i, source))
                break
    sections = []
    for idx, (start, source) in enumerate(markers):
        end = markers[idx+1][0] if idx+1 < len(markers) else len(lines)
        sections.append((source, "\n".join(lines[start+1:end])))
    return sections

def split_questions(section_text: str):
    lines = section_text.splitlines()
    starts = [i for i, line in enumerate(lines) if (not NARRATION_RE.match(line.strip()) and is_question_start(line))]
    blocks = []
    for idx, start in enumerate(starts):
        end = starts[idx+1] if idx+1 < len(starts) else len(lines)
        block = "\n".join(lines[start:end]).strip()
        if block:
            blocks.append(block)
    return blocks

def parse_block(block: str, source: str):
    lines = block.splitlines()
    if not lines:
        return None
    first = lines[0].strip()
    m = is_question_start(first)
    rest_first = (m.group(2) or "").strip() if m else ""
    body_lines = lines[1:]
    if rest_first and rest_first not in ("題目與選項", "題目與選項翻譯"):
        body_lines = [rest_first] + body_lines
    stem = extract_stem(body_lines)
    full = "\n".join(body_lines)
    tm = re.search(r"題目[：:]\s*(.+?)(?=\n選項：|\na[\.\)]\s|\n選項)", full, re.S)
    if tm:
        stem = " ".join(tm.group(1).split())
    stem_en, stem_zh = split_en_zh(stem)
    if not stem_zh:
        parts = [p.strip() for p in stem.split() if p.strip()]
    choices, answer_raw, explanation = parse_choices_and_rest(body_lines)
    answer = match_answer(choices, answer_raw)
    if len(choices) < 4 or not stem_en:
        return {"_error": True, "source": source, "stem": stem, "stemEn": stem_en, "n_choices": len(choices), "answer_raw": answer_raw, "preview": block[:240]}
    return {"source": source, "stemEn": stem_en, "stemZh": stem_zh, "choices": choices, "answer": answer, "answerRaw": answer_raw, "explanation": explanation}

def main():
    raw = SRC.read_text(encoding="utf-8")
    questions, errors = [], []
    for source, body in split_sections(raw):
        blocks = split_questions(body)
        print(f"[section] {source}: {len(blocks)} blocks")
        for block in blocks:
            q = parse_block(block, source)
            if not q:
                continue
            if q.get("_error") or not q.get("answer"):
                errors.append(q if q.get("_error") else {"_error": True, "source": source, "stemEn": q.get("stemEn"), "answer_raw": q.get("answerRaw"), "choices": [c.get("en","")[:70] for c in q.get("choices", [])], "preview": block[:200]})
                if q.get("_error"):
                    continue
            questions.append(q)
    out = []
    for i, q in enumerate(questions, 1):
        out.append({"id": f"Q{i:03d}", "source": q["source"], "stemEn": q["stemEn"], "stemZh": q["stemZh"], "choices": q["choices"], "answer": q["answer"], "explanation": q["explanation"]})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(out)} questions -> {OUT}")
    print(f"Errors / unmatched answers: {len(errors)}")
    for e in errors[:60]:
        print("---")
        print(e.get("source"), "| ans:", e.get("answer_raw") or e.get("answer"), "| n", e.get("n_choices"))
        print((e.get("stemEn") or e.get("stem") or "")[:140])
        if e.get("choices"):
            print("CHOICES", e["choices"])
        print((e.get("preview") or "")[:200])

if __name__ == "__main__":
    main()

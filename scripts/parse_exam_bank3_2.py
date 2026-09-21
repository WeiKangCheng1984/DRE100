#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse ``exam bank 3-2.txt`` into complete, conservative MCQ records.

The source is a hand-edited mixture of labelled and unlabelled assessments.
This parser deliberately rejects ambiguous questions instead of guessing.
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "exam bank 3-2.txt"
OUTPUT = ROOT / "data" / "questions3_part2.json"

CJK_RE = re.compile(r"[\u3400-\u9fff]")
LEVEL_RE = re.compile(r"(?im)^\s*Level\s*(\d+)\s+Assessment\s*$")
NUMBERED_RE = re.compile(r"^\s*(\d{1,3})\.\s*(\S.*)$")
LETTERED_RE = re.compile(r"^\s*[\(\[]?([A-D])[\)\].:、]\s*(.+)$", re.I)
ANSWER_LETTER_RE = re.compile(
    r"(?:正確答案|correct\s+answer)\s*(?:是|為)?\s*[：:=]?\s*[\(\[]?([A-D])[\)\]]?",
    re.I,
)
ANSWER_MARK_RE = re.compile(r"\[\s*正確答案\s*\]|【\s*正確答案\s*】", re.I)
EXPLANATION_RE = re.compile(
    r"^(?:解析|【?詳細解析】?|解析與|解析及|正確原因|核心考點|"
    r"correct\b|yes\b|yup\b|an?\s+.+?\s+is\b)",
    re.I,
)
KEYS = "ABCD"


def tidy(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = text.replace("\u200b", " ").replace("\ufeff", "")
    return re.sub(r"\s+", " ", text).strip()


def split_en_zh(text: str) -> tuple[str, str]:
    """Split an English-first line at （譯：） or its first CJK character."""
    text = tidy(text)
    text = re.sub(r"\s*(?:\[\s*正確答案\s*\]|【\s*正確答案\s*】)\s*", " ", text)
    text = tidy(text)
    if not text:
        return "", ""

    translated = re.search(r"[\(（]\s*譯\s*[：:]\s*(.*?)\s*[\)）]\s*$", text)
    if translated:
        return tidy(text[: translated.start()]).strip(" -:："), tidy(translated.group(1))

    cjk = CJK_RE.search(text)
    if not cjk:
        return text, ""

    en = text[: cjk.start()].rstrip(" (（-:：")
    zh = text[cjk.start() :].strip()
    if zh.endswith((")", "）")) and ("(" in text[: cjk.start()] or "（" in text[: cjk.start()]):
        zh = zh[:-1].strip()
    return tidy(en), tidy(zh)


def normalized(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").lower()
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"[\(\（].*?[\)\）]", " ", text)
    text = re.sub(r"[^a-z0-9%$]+", " ", text)
    return tidy(text)


def fingerprint(stem: str) -> str:
    tokens = normalized(stem).split()
    stop = {"a", "an", "the", "of", "to", "in", "on", "for", "and", "or", "is", "are"}
    return " ".join(token for token in tokens if token not in stop)[:240]


def useful_tokens(text: str) -> set[str]:
    stop = {
        "a", "an", "the", "of", "to", "in", "on", "for", "and", "or", "is",
        "are", "it", "this", "that", "with", "as", "be", "by", "from", "will",
        "at", "once", "up", "their",
    }
    return {word for word in normalized(text).split() if word not in stop and len(word) > 1}


def infer_answer(choice_lines: list[str], explanation: str) -> str:
    """Infer only when the source provides a strong textual signal."""
    joined = "\n".join(choice_lines) + "\n" + explanation
    marked = [
        KEYS[i]
        for i, line in enumerate(choice_lines)
        if ANSWER_MARK_RE.search(line)
    ]
    if len(marked) == 1:
        return marked[0]

    explicit = ANSWER_LETTER_RE.search(joined)
    if explicit:
        return explicit.group(1).upper()

    exp = tidy(explanation)
    exp_norm = normalized(exp)
    if not exp_norm:
        return ""

    # Common edited forms: "選項 C（正確）" or "Gretta (Correct): ...".
    correct_letter = re.search(
        r"(?:選項\s*)?[\(\[]?([A-D])[\)\]]?\s*[\(（]?\s*正確",
        exp,
        re.I,
    )
    if correct_letter:
        return correct_letter.group(1).upper()
    named_correct: list[str] = []
    for key, raw in zip(KEYS, choice_lines):
        en, _ = split_en_zh(raw)
        choice = normalized(en or raw)
        if not choice:
            continue
        leading_word = choice.split()[0]
        if len(leading_word) >= 3 and re.search(
            rf"\b{re.escape(leading_word)}\b.{{0,20}}[\(（]\s*correct\s*[\)）]",
            exp,
            re.I,
        ):
            named_correct.append(key)
    if len(named_correct) == 1:
        return named_correct[0]
    # Prefixes are feedback boilerplate, not part of the answer wording.
    lead = re.sub(
        r"^(?:correct(?:!|\.)?|yes(?:,|\.)?|yup(?:,|\.)?|"
        r"the correct (?:answer|choice) is)\s*",
        "",
        exp,
        flags=re.I,
    )
    first = re.split(r"(?<=[.!?。！？])\s+", lead, maxsplit=1)[0]
    first_norm = normalized(first)
    early_norm = normalized(lead[:600])
    exact_mentions: list[str] = []
    for key, raw in zip(KEYS, choice_lines):
        en, _ = split_en_zh(raw)
        choice = normalized(en or raw)
        if len(choice) >= 4 and re.search(rf"\b{re.escape(choice)}\b", early_norm):
            exact_mentions.append(key)
    if len(set(exact_mentions)) > 1:
        return ""

    scores: list[tuple[float, str]] = []
    for key, raw in zip(KEYS, choice_lines):
        en, _ = split_en_zh(raw)
        choice = normalized(en or raw)
        if not choice:
            continue
        score = 0.0
        if len(choice) >= 4 and (first_norm.startswith(choice) or choice.startswith(first_norm)):
            score = 1.0
        elif len(choice) >= 5 and re.search(rf"\b{re.escape(choice)}\b", first_norm):
            score = 0.92
        else:
            ct = useful_tokens(choice)
            ft = useful_tokens(first_norm)
            if ct:
                overlap = len(ct & ft) / len(ct)
                if overlap >= 0.75 and len(ct & ft) >= min(2, len(ct)):
                    score = 0.75 + overlap / 10
        scores.append((score, key))

    scores.sort(reverse=True)
    if not scores or scores[0][0] < 0.75:
        return ""
    if len(scores) > 1 and scores[0][0] - scores[1][0] < 0.08:
        return ""
    return scores[0][1]


def looks_like_choice(text: str) -> bool:
    s = tidy(text)
    if not s or len(s) > 420:
        return False
    if NUMBERED_RE.match(s) or LEVEL_RE.match(s):
        return False
    if re.match(r"^(?:解析|【詳細解析|正確答案|選項\s*[A-D]|English:)", s, re.I):
        return False
    if s.endswith(("?", "？")) or re.match(
        r"^(?:What|Which|Why|How|When|Can|Do)\b", s, re.I
    ):
        return False
    return True


def make_question(
    level: int,
    stem_lines: list[str],
    choice_lines: list[str],
    answer: str,
    explanation_lines: list[str],
) -> dict | None:
    stem_raw = tidy(" ".join(stem_lines))
    stem_en, stem_zh = split_en_zh(stem_raw)
    stem_en = re.sub(r"^\d{1,3}\.\s*", "", stem_en).strip()
    if (
        len(re.findall(r"[A-Za-z]+", stem_en)) < 3
        or len(choice_lines) != 4
        or answer not in set(KEYS)
    ):
        return None

    choices = []
    for key, raw in zip(KEYS, choice_lines):
        raw = ANSWER_MARK_RE.sub("", raw)
        raw = re.sub(r"^\s*[\(\[]?[A-D][\)\].:、]\s*", "", raw, flags=re.I)
        en, zh = split_en_zh(raw)
        if not en:
            return None
        choices.append({"key": key, "en": en, "zh": zh})

    explanation = "\n".join(tidy(line) for line in explanation_lines if tidy(line)).strip()
    if explanation and not CJK_RE.search(explanation):
        bilingual_notes = [
            split_en_zh(line)[1]
            for line in [*stem_lines, *choice_lines]
            if split_en_zh(line)[1]
        ]
        if bilingual_notes:
            explanation += "\n中文摘要：" + "；".join(bilingual_notes[:2])

    return {
        "source": f"LV 練習延伸：Level {level}",
        "stemEn": stem_en,
        "stemZh": stem_zh,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
    }


def nonempty(lines: list[str]) -> list[str]:
    return [tidy(line) for line in lines if tidy(line) and tidy(line) not in {"—", "–"}]


def parse_lettered(level: int, lines: list[str]) -> list[dict]:
    """First pass: parse explicit A-D blocks, which are the best-quality rows."""
    starts = []
    for i, line in enumerate(lines):
        match = NUMBERED_RE.match(tidy(line))
        if match and len(re.findall(r"[A-Za-z]+", match.group(2))) >= 3:
            starts.append(i)
    starts.append(len(lines))
    found: list[dict] = []
    for pos, end in zip(starts, starts[1:]):
        block = nonempty(lines[pos:end])
        if not block:
            continue
        labelled: dict[str, tuple[int, str]] = {}
        for i, line in enumerate(block[1:], 1):
            match = LETTERED_RE.match(line)
            if match and match.group(1).upper() not in labelled:
                labelled[match.group(1).upper()] = (i, match.group(2))
        if set(labelled) != set(KEYS):
            continue
        indices = [labelled[key][0] for key in KEYS]
        if indices != sorted(indices) or indices[-1] - indices[0] > 8:
            continue
        choice_lines = [labelled[key][1] for key in KEYS]
        stem_end = indices[0]
        # Some blocks first list four unlabelled options and then repeat them as
        # labelled bilingual options.  Do not leak the first list into stemZh.
        if stem_end >= 5:
            preceding = block[stem_end - 4 : stem_end]
            comparable = 0
            for old, labelled_choice in zip(preceding, choice_lines):
                old_en, _ = split_en_zh(old)
                new_en, _ = split_en_zh(labelled_choice)
                old_norm, new_norm = normalized(old_en), normalized(new_en)
                if old_norm and new_norm and (
                    old_norm == new_norm
                    or old_norm in new_norm
                    or new_norm in old_norm
                ):
                    comparable += 1
            if comparable >= 3:
                stem_end -= 4
        explanation = block[indices[-1] + 1 :]
        answer = infer_answer(choice_lines, "\n".join(explanation))
        question = make_question(level, block[:stem_end], choice_lines, answer, explanation)
        if question:
            found.append(question)
    return found


def parse_numbered_unlabelled(level: int, lines: list[str]) -> list[dict]:
    starts = []
    for i, line in enumerate(lines):
        match = NUMBERED_RE.match(tidy(line))
        if match and len(re.findall(r"[A-Za-z]+", match.group(2))) >= 3:
            starts.append(i)
    starts.append(len(lines))
    found: list[dict] = []
    for pos, end in zip(starts, starts[1:]):
        block = nonempty(lines[pos:end])
        if len(block) < 6:
            continue
        # Try plausible four-line windows near the start.  The textual answer
        # signal determines the window; earliest wins only on equal confidence.
        candidates: list[tuple[int, dict]] = []
        max_start = min(8, len(block) - 4)
        for choice_at in range(1, max_start + 1):
            raw_choices = block[choice_at : choice_at + 4]
            if not all(looks_like_choice(line) for line in raw_choices):
                continue
            explanation = block[choice_at + 4 :]
            answer = infer_answer(raw_choices, "\n".join(explanation))
            question = make_question(
                level, block[:choice_at], raw_choices, answer, explanation
            )
            if question:
                candidates.append((choice_at, question))
        if candidates:
            found.append(min(candidates, key=lambda item: item[0])[1])
    return found


def parse_unnumbered(level: int, lines: list[str]) -> list[dict]:
    """Parse later assessments: question-ending line + four choices + feedback."""
    found: list[dict] = []
    clean = [(i, tidy(line)) for i, line in enumerate(lines) if tidy(line)]
    for p, (original_i, line) in enumerate(clean):
        if not line.endswith(("?", "？", ":")):
            continue
        if p + 5 >= len(clean):
            continue
        choices = [clean[p + offset][1] for offset in range(1, 5)]
        if not all(looks_like_choice(choice) for choice in choices):
            continue
        # Feedback is normally one line, but allow a few lines for calculations.
        explanation_lines = [row[1] for row in clean[p + 5 : p + 9]]
        explanation = "\n".join(explanation_lines)
        answer = infer_answer(choices, explanation)
        if not answer:
            continue

        question = make_question(level, [line], choices, answer, explanation_lines[:1])
        if question:
            found.append(question)
    return found


def split_levels(raw: str) -> list[tuple[int, list[str]]]:
    matches = list(LEVEL_RE.finditer(raw))
    sections: list[tuple[int, list[str]]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        sections.append((int(match.group(1)), raw[match.end() : end].splitlines()))
    return sections


def main() -> None:
    raw = SOURCE.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    sections = split_levels(raw)
    if not sections or sections[0][0] != 1:
        raise SystemExit("Could not locate the Level1 Assessment header")

    # Lettered rows are deliberately collected first so their richer records
    # win when the source repeats a stem in another format.
    ordered: list[dict] = []
    for level, lines in sections:
        ordered.extend(parse_lettered(level, lines))
    for level, lines in sections:
        ordered.extend(parse_numbered_unlabelled(level, lines))
        ordered.extend(parse_unnumbered(level, lines))

    unique: list[dict] = []
    seen: set[str] = set()
    for question in ordered:
        fp = fingerprint(question["stemEn"])
        if not fp or fp in seen:
            continue
        seen.add(fp)
        unique.append(question)

    # Restore source order after quality-first deduplication.
    level_order = {level: i for i, (level, _) in enumerate(sections)}
    unique.sort(key=lambda q: level_order.get(int(q["source"].rsplit(" ", 1)[-1]), 999))
    for number, question in enumerate(unique, 1):
        question["id"] = f"P{number:03d}"
        question_order = {
            "id": question.pop("id"),
            "source": question["source"],
            "stemEn": question["stemEn"],
            "stemZh": question["stemZh"],
            "choices": question["choices"],
            "answer": question["answer"],
            "explanation": question["explanation"],
        }
        question.clear()
        question.update(question_order)

    invalid = [
        q for q in unique
        if len(q["choices"]) != 4 or q["answer"] not in set(KEYS) or not q["stemEn"]
    ]
    if invalid:
        raise SystemExit(f"Internal validation failed for {len(invalid)} questions")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(unique, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    counts = Counter(int(q["source"].rsplit(" ", 1)[-1]) for q in unique)
    print(f"Wrote: {OUTPUT}")
    for level, _ in sections:
        print(f"Level {level}: {counts[level]}")
    print(f"Total: {len(unique)}")
    print("Missing answer count: 0")
    if unique:
        print(f"Sample first/last id: {unique[0]['id']} / {unique[-1]['id']}")
    else:
        print("Sample first/last id: n/a")


if __name__ == "__main__":
    main()

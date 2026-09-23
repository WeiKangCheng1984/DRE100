# -*- coding: utf-8 -*-
"""Parse 業務員英語會話_40單元教材.md → data/speak40.json"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "業務員英語會話_40單元教材.md"
OUT = ROOT / "data" / "speak40.json"

GLOBAL_SLOTS = {
    "agent_name": ["Alex", "Jordan", "Sam", "Mia", "Chris"],
    "client_name": ["Mr. Chen", "Ms. Lopez", "the Lees", "David", "Priya"],
    "brokerage": ["Summit Realty", "Harbor Homes", "Pacific Group"],
    "city": ["Irvine", "San Jose", "Torrance", "Sacramento", "Fresno"],
    "neighborhood": ["Woodbridge", "Downtown", "the Hills", "near the park", "this subdivision"],
    "property_type": ["single-family home", "condo", "townhouse", "duplex", "investment property"],
    "beds": ["2", "3", "4", "5"],
    "baths": ["1", "1.5", "2", "2.5", "3"],
    "sqft": ["1,200", "1,650", "2,100", "2,800"],
    "list_price": ["$699,000", "$850,000", "$1.2 million", "$1.45 million"],
    "offer_price": ["$680,000", "$825,000", "$1.15 million"],
    "loan_type": ["conventional", "FHA", "VA", "cash"],
    "time": ["this Saturday at 10 a.m.", "tomorrow at 3 p.m.", "weekday evenings"],
    "feature": ["updated kitchen", "private backyard", "two-car garage", "open floor plan", "mountain view"],
    "issue": ["roof leak", "foundation crack", "outdated HVAC", "water heater", "mold concern"],
    "address": ["123 Oak Street", "88 Maple Ave", "Unit 4B", "450 Palm Court"],
    "budget": ["$700K–$800K", "under $1M", "around $1.2M"],
    "must_have": ["yard", "home office", "single story", "good light"],
    "year_built": ["1985", "2004", "2018"],
    "price_range": ["$820K–$860K", "$1.1M–$1.2M", "$690K–$720K"],
    "garage_spaces": ["1", "2", "3"],
    "parking_note": ["limited", "available", "permit-only"],
    "amenity": ["pool", "gym", "clubhouse"],
    "rent": ["$2,400/mo", "$3,100/mo"],
    "lease_term": ["12 months", "month-to-month"],
    "cap_rate": ["4.5%", "5%", "6%"],
    "closing_date": ["in 30 days", "April 15"],
    "inspector": ["licensed home inspector"],
}

ROLE_LABELS = {
    "A": "Agent",
    "B": "Buyer / Client",
    "S": "Seller",
    "C": "Client",
}


def parse_list_values(raw: str) -> list[str]:
    raw = raw.strip().strip("[]").strip()
    if not raw:
        return []
    parts = re.split(r",\s*", raw)
    return [p.strip().strip("`\"'") for p in parts if p.strip()]


def extract_unit_slots(block: str) -> dict[str, list[str]]:
    slots: dict[str, list[str]] = {}
    # {{key}}：[a, b] or {{key}}: [a, b] or {{key}}：[a, b]
    for m in re.finditer(
        r"\{\{(\w+)\}\}(?:：|:)\s*\[([^\]]+)\]",
        block,
    ):
        slots[m.group(1)] = parse_list_values(m.group(2))
    # Inline like {{parking_note}}：[limited, available]
    # Also: There's a {{garage_spaces}}-car garage. `[1, 2, 3]`
    for m in re.finditer(
        r"\{\{(\w+)\}\}[^\n`]{0,40}`\[([^\]]+)\]`",
        block,
    ):
        slots.setdefault(m.group(1), parse_list_values(m.group(2)))
    # Bare {{key}} references still get global defaults later
    for key in re.findall(r"\{\{(\w+)\}\}", block):
        slots.setdefault(key, [])
    return slots


def merge_slots(local: dict[str, list[str]]) -> dict[str, list[str]]:
    out = {}
    for key, vals in local.items():
        if vals:
            out[key] = vals
        elif key in GLOBAL_SLOTS:
            out[key] = GLOBAL_SLOTS[key][:]
        else:
            out[key] = [f"[{key}]"]
    # Always ensure globals that appear frequently are available if referenced
    return out


def parse_key_phrases(block: str) -> list[dict]:
    phrases = []
    skip_heads = {
        "英文", "發音", "發音提示", "中文", "中文意思", "不說", "改說",
        "危險說法", "安全改寫", "類型", "一句話",
    }

    # 3-column tables
    for en, ipa, zh in re.findall(
        r"^\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|$",
        block,
        flags=re.M,
    ):
        en = re.sub(r"\*+", "", en).strip()
        if not en or en.startswith(":") or en in skip_heads:
            continue
        phrases.append(
            {
                "en": en,
                "ipa": ipa.strip() if ipa.strip() not in skip_heads and ipa.strip() != "—" else "",
                "zh": zh.strip() if zh.strip() not in skip_heads else "",
            }
        )

    # 2-column tables (英文 | 中文) — skip long English/English rewrite pairs
    for en, zh in re.findall(
        r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|$",
        block,
        flags=re.M,
    ):
        en = re.sub(r"\*+", "", en).strip()
        zh = zh.strip()
        if not en or en.startswith(":") or en in skip_heads:
            continue
        if any(p["en"] == en for p in phrases):
            continue
        # long EN | EN rows belong to rewrite tables
        if re.search(r"[A-Za-z]", zh) and len(en.split()) >= 5 and len(zh.split()) >= 5:
            continue
        phrases.append({"en": en, "ipa": "", "zh": zh if zh not in skip_heads else ""})

    # Bullet key phrases: - ★ text. `/ipa/`
    for m in re.finditer(
        r"^[-–]\s*★?\s*(.+?)(?:\s+`(/[^`]+/)`)?\s*$",
        block,
        flags=re.M,
    ):
        line = m.group(1).strip()
        if line.startswith("*"):
            continue
        en = re.sub(r"\*+", "", line)
        en = re.sub(r"：\s*\[.*$", "", en).strip()
        en = re.sub(r":\s*\[.*$", "", en).strip()
        if not re.match(r"^[A-Za-z\"“]", en):
            continue
        if any(en == p["en"] for p in phrases):
            continue
        phrases.append({"en": en, "ipa": (m.group(2) or "").strip(), "zh": ""})

    seen = set()
    uniq = []
    for p in phrases:
        key = p["en"]
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)
    return uniq[:12]


def parse_dialogue(block: str) -> list[dict]:
    lines = []
    # Prefer fenced code blocks after ### 對話
    m = re.search(r"###\s*對話\s*\n+```([\s\S]*?)```", block)
    chunks = []
    if m:
        chunks.append(m.group(1))
    # Also voicemail / text templates
    for label, pat in (
        ("A", r"###\s*語音留言[^\n]*\n+```([\s\S]*?)```"),
        ("A", r"###\s*簡訊\s*\n+```([\s\S]*?)```"),
    ):
        vm = re.search(pat, block)
        if vm and not m:
            chunks.append(vm.group(1))

    # Capstone task cards as pseudo dialogue intro
    task = re.search(r"###\s*任務卡[^\n]*\n+```([\s\S]*?)```", block)
    if task and not chunks:
        # no dialogue — synthesize from key phrases later handled elsewhere
        pass

    text = "\n".join(chunks) if chunks else ""
    if not text:
        # fallback: any A:/B: lines in block
        text = block

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        mm = re.match(r"^([ABSC])\s*:\s*(.+)$", line)
        if mm:
            role = mm.group(1)
            lines.append(
                {
                    "role": role,
                    "roleLabel": ROLE_LABELS.get(role, role),
                    "en": mm.group(2).strip(),
                }
            )
            continue
        # Multi-line voicemail without role prefix → Agent
        if chunks and not re.match(r"^[ABSC]\s*:", line) and re.search(r"[A-Za-z]", line):
            if "任務卡" in block and "Buyer:" in text:
                continue
            lines.append({"role": "A", "roleLabel": "Agent", "en": line})

    # Capstone: build practice script from task yaml-ish
    if not lines and task:
        body = task.group(1).strip()
        lines.append(
            {
                "role": "A",
                "roleLabel": "Coach",
                "en": "Use this task card for a 12–15 minute role-play. Swap the slots, then practice the full path.",
            }
        )
        for raw in body.splitlines():
            raw = raw.strip()
            if not raw or raw.startswith("#"):
                continue
            lines.append({"role": "C", "roleLabel": "Task", "en": raw.lstrip("- ").strip()})

    return lines


def parse_drills(block: str) -> list[str]:
    drills = []
    for sec in ("口語練習", "抽換練習", "抽換"):
        m = re.search(rf"###\s*{sec}\s*\n([\s\S]*?)(?=\n### |\n---|\Z)", block)
        if not m:
            continue
        chunk = m.group(1).strip()
        for line in chunk.splitlines():
            line = line.strip()
            if not line:
                continue
            line = re.sub(r"^\d+\.\s*", "", line)
            line = line.strip("*- ").strip()
            if line:
                drills.append(line)
    # unique
    out = []
    seen = set()
    for d in drills:
        if d not in seen:
            seen.add(d)
            out.append(d)
    return out


def parse_rewrites(block: str) -> list[dict]:
    rows = []
    # | 不說 | 改說 | or | 危險說法 | 安全改寫 |
    for m in re.finditer(
        r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|$",
        block,
        flags=re.M,
    ):
        a, b = m.group(1).strip(), m.group(2).strip()
        if a in ("不說", "危險說法", ":---") or a.startswith(":"):
            continue
        if b in ("改說", "安全改寫"):
            continue
        if re.search(r"[A-Za-z]", a) and re.search(r"[A-Za-z]", b):
            rows.append({"unsafe": a, "safe": b})
    return rows


def parse_units(md: str) -> list[dict]:
    parts = re.split(r"\n## Unit ", md)
    units = []
    for part in parts[1:]:
        header, _, body = part.partition("\n")
        hm = re.match(r"(\d+)\s*｜\s*(.+)", header.strip())
        if not hm:
            continue
        num = int(hm.group(1))
        title_zh = hm.group(2).strip()
        block = body

        title_en_m = re.search(r"^\*\*([^*]+)\*\*\s*$", block, flags=re.M)
        title_en = title_en_m.group(1).strip() if title_en_m else ""

        scenario_m = re.search(r"\*\*情境\*\*[：:]\s*(.+)", block)
        scenario = scenario_m.group(1).strip() if scenario_m else ""

        cram_m = re.search(r"\*\*對應(?:知識點)?\*\*[：:]\s*(.+)", block)
        cram = cram_m.group(1).strip() if cram_m else ""

        fair = "⚠" in block or "Fair Housing" in block or "公平住房" in title_zh

        note_m = re.search(r"###\s*⚠[^\n]*\n([\s\S]*?)(?=\n### |\n---|\Z)", block)
        fair_note = ""
        if note_m:
            fair_note = " ".join(
                ln.strip() for ln in note_m.group(1).splitlines() if ln.strip() and not ln.strip().startswith("|")
            )

        local_slots = extract_unit_slots(block)
        # Collect slot keys from dialogue too
        dialogue = parse_dialogue(block)
        for line in dialogue:
            for key in re.findall(r"\{\{(\w+)\}\}", line["en"]):
                local_slots.setdefault(key, [])
        phrases = parse_key_phrases(block)
        for p in phrases:
            for key in re.findall(r"\{\{(\w+)\}\}", p["en"]):
                local_slots.setdefault(key, [])

        slots = merge_slots(local_slots)
        drills = parse_drills(block)
        rewrites = parse_rewrites(block)

        # If no dialogue but has phrases, make mini dialogue from phrases
        if not dialogue and phrases:
            for p in phrases[:4]:
                dialogue.append({"role": "A", "roleLabel": "Agent", "en": p["en"]})

        # Rewrite gym units: practice unsafe → safe as dialogue pairs
        if not dialogue and rewrites:
            for pair in rewrites[:4]:
                dialogue.append({"role": "C", "roleLabel": "Avoid", "en": pair["unsafe"]})
                dialogue.append({"role": "A", "roleLabel": "Say instead", "en": pair["safe"]})

        units.append(
            {
                "id": f"speak-{num:02d}",
                "num": num,
                "titleZh": title_zh,
                "titleEn": title_en,
                "scenario": scenario,
                "cramRef": cram,
                "fairHousing": fair,
                "fairHousingNote": fair_note,
                "slots": slots,
                "phrases": phrases,
                "dialogue": dialogue,
                "drills": drills,
                "rewrites": rewrites,
            }
        )
    units.sort(key=lambda u: u["num"])
    return units


def main() -> None:
    md = SRC.read_text(encoding="utf-8")
    units = parse_units(md)
    if len(units) < 40:
        raise SystemExit(f"Expected 40 units, got {len(units)}")

    payload = {
        "titleZh": "業務員英語會話練習",
        "titleEn": "Real Estate Agent English Conversation — 40 Units",
        "subtitleZh": "看對話 → 聽發音 → 跟讀／角色扮演 → 抽換名詞舉一反三",
        "subtitleEn": "Dialogues, pronunciation, role-play, and swappable slots for practice.",
        "disclaimerZh": "對話僅供溝通練習；正式交易請依現行加州法規、合約與公司政策。",
        "globalSlots": GLOBAL_SLOTS,
        "units": units,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} with {len(units)} units")
    empty_dlg = [u["num"] for u in units if not u["dialogue"]]
    if empty_dlg:
        print("Units missing dialogue:", empty_dlg)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse exam bank 3.txt into data/questions3.json.

Source layout:
1) English MCQs: 「第 N 題」 + A)/B)/C)/D) + 正確答案 + 解析
2) Bilingual enrichment: 「NN. topic」 + Question/Correct Answer + 詳細解析
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "exam bank 3.txt"
OUT = ROOT / "data" / "questions3.json"
CLEAN = ROOT / "exam bank 3.formatted.txt"

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
Q_LABEL_RE = re.compile(r"^第\s*(\d+)\s*題\s*$")
CHOICE_RE = re.compile(r"^\*?([A-D])\)\s*(.*)$")
ANSWER_RE = re.compile(r"^正確答案[：:]\s*([A-D])\s*$")
EXPLAIN_RE = re.compile(r"^解析[：:]\s*(.*)$")
BI_HEADER_RE = re.compile(r"^(\d{1,3})\.\s+(.+)$")
BI_QUESTION_RE = re.compile(r"^Question:\s*(.*)$", re.I)
BI_CORRECT_RE = re.compile(r"^\[Correct Answer\]\s*(.*)$", re.I)
STAGE2_RE = re.compile(r"第二階段")


def split_en_zh(text: str) -> tuple[str, str]:
    text = (text or "").strip()
    if not text:
        return "", ""
    # Trailing parenthetical Chinese, allowing Latin names inside: "(Tom 和 Becky...)"
    m = re.search(r"[\(（]([^\)）]*[\u4e00-\u9fff][^\)）]*)[\)）]\s*$", text)
    if m:
        en = re.sub(r"\s+", " ", text[: m.start()].strip()).strip(" :：-")
        zh = re.sub(r"\s+", " ", m.group(1).strip())
        return en, zh
    m = CJK_RE.search(text)
    if not m:
        return re.sub(r"\s+", " ", text).strip(), ""
    en = text[: m.start()].strip().rstrip(" (（")
    zh = text[m.start() :].strip().strip(")）")
    if zh.startswith("（") and zh.endswith("）"):
        zh = zh[1:-1].strip()
    elif zh.startswith("(") and zh.endswith(")"):
        zh = zh[1:-1].strip()
    return re.sub(r"\s+", " ", en).strip(), re.sub(r"\s+", " ", zh).strip()


def stem_fingerprint(text: str) -> str:
    """Normalize English stem for cross-section matching."""
    en, _zh = split_en_zh(text)
    s = (en or text).lower()
    s = s.replace("“", '"').replace("”", '"').replace("’", "'").replace("®", "")
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"[^\w\s]", " ", s)
    tokens = [t for t in s.split() if t and t not in {"a", "an", "the", "of", "to", "in", "on", "for", "and", "or"}]
    return " ".join(tokens[:18])


def clean_choice_noise(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s*錯誤點[：:].*$", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def source_for(n: int) -> str:
    if n <= 35:
        return "LV17 實務情境題"
    return "LV17 觀念法規題"


def parse_english_section(lines: list[str]) -> dict[int, dict]:
    starts: list[tuple[int, int]] = []
    for i, line in enumerate(lines):
        m = Q_LABEL_RE.match(line.strip())
        if m:
            starts.append((i, int(m.group(1))))

    out: dict[int, dict] = {}
    for idx, (start, qnum) in enumerate(starts):
        # Stop before bilingual orphan block / stage narrative after Q100
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        # Truncate trailing bilingual dump if attached after Q100
        block_lines = lines[start:end]
        # If this is the last English Q and bilingual section begins inside, cut it
        for j, ln in enumerate(block_lines):
            if j > 0 and (BI_HEADER_RE.match(ln.strip()) or ln.strip().startswith("正確答案是：")):
                block_lines = block_lines[:j]
                break

        body = block_lines[1:]
        stem_lines: list[str] = []
        choices: dict[str, str] = {}
        answer = ""
        expl_lines: list[str] = []
        mode = "stem"
        for ln in body:
            s = ln.strip()
            if not s:
                continue
            if mode == "stem":
                cm = CHOICE_RE.match(s)
                if cm:
                    mode = "choices"
                elif ANSWER_RE.match(s):
                    mode = "answer"
                elif EXPLAIN_RE.match(s):
                    mode = "expl"
                else:
                    stem_lines.append(s)
                    continue
            if mode == "choices":
                cm = CHOICE_RE.match(s)
                if cm:
                    choices[cm.group(1)] = cm.group(2).strip()
                    continue
                if ANSWER_RE.match(s):
                    mode = "answer"
                elif EXPLAIN_RE.match(s):
                    mode = "expl"
                else:
                    # continuation of previous choice
                    for key in reversed(["A", "B", "C", "D"]):
                        if key in choices:
                            choices[key] = (choices[key] + " " + s).strip()
                            break
                    continue
            if mode == "answer":
                am = ANSWER_RE.match(s)
                if am:
                    answer = am.group(1)
                em = EXPLAIN_RE.match(s)
                if em:
                    mode = "expl"
                    if em.group(1):
                        expl_lines.append(em.group(1).strip())
                continue
            if mode == "expl":
                em = EXPLAIN_RE.match(s)
                if em:
                    if em.group(1):
                        expl_lines.append(em.group(1).strip())
                    continue
                expl_lines.append(s)

        if len(choices) != 4 or not answer:
            continue
        out[qnum] = {
            "num": qnum,
            "stemEn": re.sub(r"\s+", " ", " ".join(stem_lines)).strip(),
            "choicesEn": {k: choices[k] for k in "ABCD"},
            "answer": answer,
            "explanationEn": " ".join(expl_lines).strip(),
        }
    return out


def parse_bilingual_section(text: str) -> dict[int, dict]:
    # Start at first "01. ..." topic header after English bank
    m0 = re.search(r"(?m)^01\.\s+", text)
    if not m0:
        return {}
    bi = text[m0.start() :]
    lines = bi.splitlines()

    starts: list[tuple[int, int, str]] = []
    for i, line in enumerate(lines):
        m = BI_HEADER_RE.match(line.strip())
        if m:
            n = int(m.group(1))
            if 1 <= n <= 100:
                starts.append((i, n, m.group(2).strip()))

    out: dict[int, dict] = {}
    for idx, (start, qnum, topic) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        block = "\n".join(lines[start:end]).strip()
        # Skip pure narrative bridges (no Question: line anywhere in block)
        if "Question:" not in block and "Question：" not in block:
            continue

        stem_en, stem_zh = "", ""
        correct_en, correct_zh = "", ""
        choice_zh_map: dict[str, str] = {}
        distractor_ens: list[str] = []
        expl_zh_parts: list[str] = []
        expl_en_parts: list[str] = []
        tip_parts: list[str] = []

        mode = "head"
        for raw in lines[start + 1 : end]:
            s = raw.strip()
            if not s:
                continue
            if s.startswith("維剛，") or s.startswith("以下是第"):
                break

            qm = BI_QUESTION_RE.match(s)
            if qm:
                stem_en, stem_zh = split_en_zh(qm.group(1))
                mode = "after_q"
                continue
            # Multi-line question continuation before Correct Answer
            if mode == "after_q" and not BI_CORRECT_RE.match(s) and not s.startswith("["):
                # May be leftover English/Chinese of question on next lines
                en2, zh2 = split_en_zh(s)
                if zh2 and not stem_zh:
                    stem_zh = zh2
                if en2 and CJK_RE.search(s) is None:
                    stem_en = (stem_en + " " + en2).strip()
                elif zh2:
                    stem_zh = (stem_zh + " " + zh2).strip() if stem_zh and zh2 not in stem_zh else (stem_zh or zh2)
                continue

            cm = BI_CORRECT_RE.match(s)
            if cm:
                correct_en, correct_zh = split_en_zh(cm.group(1))
                mode = "choices"
                continue

            if mode == "choices":
                if s.startswith("詳細解析") or s.startswith("詳細計算") or s.startswith("中文解析"):
                    mode = "expl"
                else:
                    # distractor line(s)
                    cleaned = clean_choice_noise(s)
                    en, zh = split_en_zh(cleaned)
                    if en:
                        distractor_ens.append(en)
                    if en and zh:
                        choice_zh_map[normalize_key(en)] = zh
                    continue

            if s.startswith("中文解析"):
                mode = "expl_zh"
                rest = re.sub(r"^中文解析[：:\s]*", "", s).strip()
                if rest:
                    expl_zh_parts.append(rest)
                continue
            if s.startswith("English Analysis") or s.startswith("English Summary"):
                mode = "expl_en"
                rest = re.sub(r"^(English Analysis|English Summary)[：:\s]*", "", s).strip()
                if rest:
                    expl_en_parts.append(rest)
                continue
            if s.startswith("考試陷阱") or s.startswith("加州考點") or s.startswith("考試高頻"):
                mode = "tip"
                tip_parts.append(s)
                continue
            if s.startswith("干擾項") or s.startswith("邏輯：") or s.startswith("PGI") or s.startswith("EGI") or s.startswith("NOI") or s.startswith("R："):
                mode = "expl_zh"
                expl_zh_parts.append(s)
                continue
            if s.startswith("詳細解析") or s.startswith("詳細計算"):
                mode = "expl"
                continue

            if mode == "expl_zh":
                expl_zh_parts.append(s)
            elif mode == "expl_en":
                expl_en_parts.append(s)
            elif mode == "tip":
                tip_parts.append(s)
            elif mode == "expl":
                # generic expl block before labeled sections
                if CJK_RE.search(s):
                    expl_zh_parts.append(s)
                else:
                    expl_en_parts.append(s)

        if correct_en:
            choice_zh_map[normalize_key(correct_en)] = correct_zh

        out[qnum] = {
            "topic": topic,
            "stemEn": stem_en,
            "stemZh": stem_zh,
            "correctEn": correct_en,
            "correctZh": correct_zh,
            "choiceZhByEn": choice_zh_map,
            "distractorEns": distractor_ens,
            "explZh": "\n".join(expl_zh_parts).strip(),
            "explEn": "\n".join(expl_en_parts).strip(),
            "tips": "\n".join(tip_parts).strip(),
        }
    return out


def normalize_key(s: str) -> str:
    s = s.lower().strip()
    s = s.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s%$./\-]", "", s)
    return s[:120]


def similar(a: str, b: str) -> bool:
    na, nb = normalize_key(a), normalize_key(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    if na in nb or nb in na:
        return True
    # token overlap
    ta, tb = set(na.split()), set(nb.split())
    if not ta or not tb:
        return False
    return len(ta & tb) / max(len(ta), len(tb)) >= 0.72


def lookup_zh(en: str, zh_map: dict[str, str], correct_en: str, correct_zh: str) -> str:
    if correct_en and similar(en, correct_en) and correct_zh:
        return correct_zh
    key = normalize_key(en)
    if key in zh_map and zh_map[key]:
        return zh_map[key]
    for k, v in zh_map.items():
        if similar(en, k) and v:
            return v
    return ""


# Manual Chinese for common short options missing bilingual distractor zh
MANUAL_CHOICE_ZH = {
    "the dispute will not go into arbitration.": "糾紛將不會進入仲裁。",
    "the dispute will go into mediation.": "糾紛將進入調解。",
    "lawsuits can now be filed.": "現在可以提起訴訟。",
    "exclusive agency agreement": "獨家代理合約",
    "open listing agreement": "開放式委託銷售合約",
    "net listing agreement": "淨委託銷售合約",
    "sold too long ago": "成交時間過久",
    "not similar enough": "物理條件不夠相似",
    "has already sold": "已經售出",
    "electromagnetic": "電磁的",
    "asbestosis": "石棉沉著症",
    "radioactive": "放射性的",
    "an appraiser's license": "估價師執照",
    "a real estate broker's license": "不動產經紀人執照",
    "a real estate agent's license": "不動產業務員執照",
    "surplus water lines": "剩餘水管線",
    "city water lines": "市政供水管線",
    "recycled water lines": "回收水管線",
    "home ventilation and air conditioning systems": "住家通風與空調系統",
    "home vacuuming systems": "住家真空清潔系統",
    "hud, va, and commercial loans": "HUD、VA 與商業貸款",
    "void contract": "無效合約",
    "executory contract": "執行中／尚未履行完畢的合約",
    "voidable contract": "得撤銷合約",
    "the final sales price of a property": "物業的最終成交價",
    "a non-refundable form of compensation for buyer's agents": "買方代理人的不可退還報酬",
    "a listing agent's going rate": "上市經紀人的一般收費行情",
    "the property is illiquid.": "該物業流動性差。",
    "never": "永遠不行",
    "anytime": "任何時候都可以",
    "residential": "住宅",
    "commercial": "商業",
    "farm and land": "農地與土地",
    "the california department of consumer affairs": "加州消費者事務部",
    "the california association of realtors®": "加州房地產經紀人協會（C.A.R.）",
    "the national association of realtors®": "全美房地產經紀人協會（NAR）",
    "an addendum": "附錄／增補條款",
    "an option": "選擇權",
    "an offer": "報價／要約",
    "increase": "上漲",
    "stay static": "維持不變",
    "supply doesn't influence price.": "供應不影響價格。",
    "verbally": "口頭",
    "in person": "當面親自",
    "through assumptions": "透過假設／推定",
    "utility": "效用",
    "demand": "需求",
    "scarcity": "稀缺性",
    "market price": "市場價格（實際成交價）",
    "direct cost": "直接成本",
    "plottage": "合併溢價",
    "performed due diligence": "已盡職調查",
    "signed a net listing agreement": "簽署了淨委託合約",
    "owed fiduciary duties to neither party": "對雙方皆無受託義務",
    "expiration": "到期終止",
    "mutual agreement": "雙方合意終止",
    "fulfillment of purpose": "目的達成／履約完成",
    "the buyer pays the state a default fee of $5,000.": "買方向州政府支付 $5,000 違約罰鍰。",
    "the seller declares bankruptcy.": "賣方宣告破產。",
    "it's noted in the buyer's credit report.": "會註記在買方信用報告中。",
    "net lease": "淨租約",
    "gross lease": "總租約／毛租約",
    "percentage lease": "抽成租約",
    "collusion": "共謀",
    "price fixing": "價格聯合／價格操縱",
    "a tie-in agreement": "搭售協議",
    "revocation": "撤銷",
    "infeasibility": "履行不能",
    "accretion": "淤積增生",
    "erosion": "侵蝕",
    "reliction": "河湖退卻露出新陸",
    "exclusive right-to-sell listing": "獨家專任銷售合約",
    "open listing": "開放式委託",
    "net listing": "淨委託",
    "unilateral": "單邊合約",
    "implied": "默示合約",
    "yield": "收益率",
    "principle of progression": "進化原則／增值原則",
    "principle of change": "變動原則",
    "principle of digression": "偏離原則（干擾項）",
    "a backup offer": "備援要約",
    "a retainer fee": "預付委任費",
    "a legal description": "法定土地描述",
    "carbon monoxide": "一氧化碳",
    "urea-formaldehyde foam insulation": "脲甲醛泡沫絕緣材料",
    "radon gas": "氡氣",
    "10%": "10%",
    "20%": "20%",
    "2%": "2%",
    "three months": "三個月",
    "five days": "五天",
    "five weeks": "五週",
    "cost": "成本",
    "insured value": "保險價值",
    "$13,941,701.59": "$13,941,701.59",
    "5%": "5%",
    "voidable": "得撤銷合約",
    "a protection period": "保護期條款",
    "procuring cause": "促成交易主因（procuring cause）",
    "$128,000": "$128,000",
    "$122,000": "$122,000",
    "$119,000": "$119,000",
    "$131,000": "$131,000",
    "$36,937.80": "$36,937.80",
    "$900,737.20": "$900,737.20",
    "$878,327.20": "$878,327.20",
    "other income": "其他收入",
    "potential gross income": "潛在總收益（PGI）",
    "vacancy cost": "空置成本",
    "efficient gross income": "有效總收益（干擾用詞）",
    "before tax cash flow": "稅前現金流",
    "dual agency": "雙重代理",
    "protection period": "保護期",
    "due diligence": "盡職調查",
    "underground storage tanks": "地下儲油槽",
    "hardened urea-formaldehyde foam insulation": "硬化脲甲醛泡沫絕緣",
    "damp building materials": "潮濕建材",
    "compensation term": "佣金條款",
    "legal description of the property": "物業法定描述",
    "signatures of parties": "當事人簽名",
    "1974": "1974 年",
    "1972": "1972 年",
    "1976": "1976 年",
    "putting down a larger down payment": "提高頭期款",
    "offering to pay more of the closing costs": "願意負擔更多結案費用",
    "agreeing to a shorter option period": "同意縮短選擇／檢查期",
    "information about what's included with the property": "物業隨附設備／項目資訊",
    "known defects or malfunctions": "已知瑕疵或故障",
    "notice that sellers must provide buyers any inspection reports that have been completed": "賣方須提供已完成檢查報告之通知",
    "the buyer and their agent": "買方與其代理人",
    "the seller and their agent": "賣方與其代理人",
    "the buyer, seller, and broker": "買方、賣方與經紀人",
    "exclusivity of representation": "代理專屬性",
    "internet marketing law": "網路行銷法",
    "statute of frauds": "詐欺條例／書面要件法",
    "a finance contingency": "融資應變條款",
    "an appraisal contingency": "估價應變條款",
    "a sale of another property contingency": "他屋出售應變條款",
    "express": "明示合約",
    "written": "書面合約",
    "the agent should agree to not reveal the defect to buyers.": "經紀人應同意不向買方揭露瑕疵。",
    "the agent should advise the seller to hire a professional painter to do a better job at concealing the defect.": "經紀人應建議賣方雇專業油漆工更好地掩蓋瑕疵。",
    "the agent should report his client to the police.": "經紀人應向警方檢舉客戶。",
    "yes, unless his clients signed an agreement prior to the appraisal.": "可以，除非客戶在估價前已簽署協議。",
    "yes, property appraisal fees are dependent on the value of the property.": "可以，估價費取決於物業價值。",
    "no, he should have told them about the fee before appraising the property.": "不行，他應在估價前告知費用。",
    "june 20th, 2023": "2023 年 6 月 20 日",
    "december 20th, 2022": "2022 年 12 月 20 日",
    "earnest or frank": "Earnest 或 Frank",
    "frank": "房東 Frank",
    "a sublessee is not required to pay rent.": "轉租人不需要支付租金。",
    "settle for liquidated damages": "接受預定損害賠償",
    "initiate rescission": "啟動契約解除／撤銷",
    "accept compensatory damages": "接受補償性損害賠償",
    "destructibility, utility, scarcity, and transferability": "可毀滅性、效用、稀缺性、可轉讓性",
    "demand, uniqueness, scarcity, and transferability": "需求、獨特性、稀缺性、可轉讓性",
    "destructibility, usury, scarcity, and transferability": "可毀滅性、高利貸、稀缺性、可轉讓性",
    "immobility": "不可移動性",
    "indestructibility": "不可毀滅性",
    "non-homogeneity": "非同質性",
    "a large, visible crack in the foundation": "地基上明顯可見的大裂縫",
    "visible mold growth in the bathroom": "浴室可見的黴菌滋生",
    "a broken light switch": "損壞的電燈開關",
    "buyer representation agreement": "買方代理協議",
    "transaction brokerage agreement": "交易經紀協議",
    "independent contractor agreement": "獨立承攬人協議",
    "executed": "已履行完畢",
    "follow their client's request": "遵從客戶要求",
    "only disclose the material fact to buyers if they ask about it": "僅在買方詢問時才披露",
    "help their client conceal the material fact": "協助客戶隱瞞該重大事實",
    "agency law only": "僅代理法",
    "contract law only": "僅合約法",
    "state law only": "僅州法",
    "any real estate professional": "任何不動產從業人員",
    "anyone who wants to know the value of a property": "任何想知道物業價值的人",
    "a mortgage lender": "抵押貸款機構",
    "olga must give betty half of her commission.": "Olga 必須把佣金的一半給 Betty。",
    "betty is owed no commission.": "Betty 無權取得任何佣金。",
    "betty may be eligible for a full commission, but only if she can prove procuring cause.": "Betty 可能可拿全額佣金，但僅在能證明促成原因時。",
    "anderson refuses to work with clients who he knows are in same-sex partnerships.": "Anderson 拒絕服務他明知為同性伴侶的客戶。",
    "the sales comparison approach": "市場比較法",
    "the income approach": "收益法",
    "the market data approach": "市場資料法（比較法別名）",
    "accord and satisfaction": "和解清償",
    "the parol evidence rule": "口頭證據法則",
    "a single-family home": "獨棟住宅",
    "a unit in a condominium": "公寓大廈（condo）單元",
    "a duplex": "雙拼住宅",
    "an 18-month lease": "18 個月租約",
    "a purchase agreement for a condo": "公寓買賣合約",
    "a commission agreement": "佣金協議",
    "they must wait to hear from the first buyer.": "必須等待第一位買方回覆。",
    "they must proceed with the sale to the first buyer, since once they made a counteroffer, that deal became binding.": "必須與第一位買方成交，因為反報價一經提出即具拘束力。",
    "they are required to tell the first buyer about the second offer and give them an opportunity to come up to the new amount.": "必須告知第一位買方第二份報價並給其加價機會。",
    "no, the mineral company is actually violating her water rights and right to control.": "不對，礦業公司其實侵犯的是她的水權與控制權。",
    "yes, the right to quiet enjoyment means the homeowner can bar anyone from her property who is planning to make a lot of noise.": "對，安寧享有權代表屋主可禁止任何打算製造噪音者進入。",
    "yes, surface rights take priority over mineral rights. the gas company can only drill if the homeowner approves the plans.": "對，表面權優先於礦產權；天然氣公司須經屋主同意才能鑽探。",
    "to pay for legal fees": "用來支付律師費",
    "so the seller can have enough funds to pay for a title policy": "讓賣方有足夠資金支付產權保險",
    "to pay for their agent's commission": "用來支付其代理人佣金",
    "exclusive right-to-sell listing agreement": "獨家專任銷售合約",
    "after providing services": "提供服務之後",
    "at any time": "任何時間皆可",
    "realtors do not have to disclose this information.": "Realtor 無須披露此資訊。",
    "the price a buyer agrees to pay and a seller agrees to accept for a property": "買方同意支付、賣方同意接受的價格",
    "the price for which a property will theoretically sell under typical conditions": "典型條件下物業理論上可售出的價格",
    "the highest price an investor would be willing to pay for a property based on how well it will serve their investment goals": "投資人依投資目標願付的最高價格",
    "four two-bedroom houses located in various neighborhoods of the city that have sold within the past week": "分散在全市各社區、過去一週內售出的四間兩房",
    "one two-bedroom house that is more similar to the subject property than any of the other homes and has sold within the past year": "與標的最相似、過去一年內售出的單一兩房",
    "two two-bedroom homes located 10-15 miles from the grand point neighborhood that have sold within the past month": "距離 Grand Point 社區 10–15 英里、過去一個月售出的兩間兩房",
    "a type of agreement in which the seller holds the title until the buyer has fully paid": "賣方在買方付清前仍持有產權的協議（類似分期契據）",
    "a deposit made by a real estate buyer to show good faith": "買方為表示誠意所支付的押金",
    "a contract whose terms have been completely fulfilled": "條款已完全履行的合約",
    "paris is not required to maintain transaction documents for any specific amount of time.": "Paris 無須在任何特定期間保存交易文件。",
    "latoye is not obligated to disclose known defects, but she can if she chooses to.": "LaToye 無義務披露已知瑕疵，但可自行選擇披露。",
    "latoye must not disclose known defects.": "LaToye 不得披露已知瑕疵。",
    "latoye is only obligated to disclose hidden defects not easily accessible to the eye.": "LaToye 僅須披露肉眼不易發現的隱藏瑕疵。",
    "agents cannot be held liable for acting on any request made by their principal.": "經紀人遵從委託人任何要求皆不須負責。",
    "the client asks the agent not to sell to a specific marginalized group and the agent terminates the listing agreement.": "客戶要求勿售予特定邊緣群體，而經紀人終止委託。",
    "the seller-client asks the agent not to disclose that a previous occupant had aids and the agent complies.": "賣方要求勿披露前住戶曾患愛滋，經紀人照辦。",
    "there will be little effect on the supply or price of real estate from just one employer.": "僅一家雇主對不動產供給或價格影響甚微。",
    "the current residents of the town will likely try to move away, increasing supply and lowering prices.": "現住居民可能遷離，供給增加、價格下跌。",
    "because the announcement impacts industrial real estate, there will be little effect on residential properties.": "因公告影響工業地產，對住宅影響甚微。",
    "all defects on a property, regardless of whether the seller knows about them": "物業上所有瑕疵，不論賣方是否知情",
    "only patent defects": "僅顯性瑕疵",
    "only defects the buyer asks about": "僅買方詢問到的瑕疵",
    "consideration": "對價",
    "lawful objective": "合法目的",
    "a counteroffer": "反報價",
    "by law, a seller must disclose what materials the property is comprised of.": "法律規定賣方必須披露物業建材組成。",
    'disclosure of material facts is not required since "buyer beware" rules apply to real estate transactions.': "因適用買者自負，故無須披露重要事實。",
    'if a property is being sold "as is," then disclosure of material facts is not required.': "若以現況出售，則無須披露重要事實。",
    "not valid for any real estate contracts": "對任何不動產合約皆無效",
    "valid for agency agreements, but not purchase sale agreements": "僅對代理協議有效，對買賣合約無效",
    "valid for purchase sale agreements, but not agency agreements": "僅對買賣合約有效，對代理協議無效",
    "no. it can only be used as an exclusive representation contract.": "不行。BRBC 只能作專屬代理合約。",
    "yes. but raul must check the applicable box in order to make the agreement a non-exclusive representation contract.": "可以，但 Raul 必須勾選方框才會變成非專屬。",
    "yes, because the brbc cannot be used for anything but non-exclusive buyer representation.": "可以，因為 BRBC 只能用於非專屬買方代理。",
    "all contracts are dissolved if one of the parties dies.": "一方死亡則所有合約皆消滅。",
    "unless her will specifically states otherwise, the contract is nullified.": "除非遺囑另有規定，否則合約無效。",
    "the contract is dissolved unless manuel sues julia's heirs.": "除非 Manuel 起訴 Julia 繼承人，否則合約消滅。",
    "until the offer has been signed by the other party": "直到他方簽署要約為止",
    "with suppressed market value due to their physical condition or features": "因物理狀況或特徵導致市值受壓",
    "that are exempt from ad valorem taxes": "免徵從價稅的物業",
    "with market prices far exceeding other similar properties within an area": "市價遠高於同區類似物業",
    "egi includes expenses and shows the annual profit produced. noi is the total annual income a property produces and does not include expenses.": "EGI 含費用並顯示年利潤；NOI 為不含費用之年總收入。",
    "egi is used to determine if an investor should invest in a real estate property. noi is not used to determine this.": "用 EGI 決定是否投資；NOI 不用。",
    "egi is not used to determine if an investor should invest in a real estate property. noi is used to determine this.": "不用 EGI 決定是否投資；用 NOI。",
    "provide additional information about property structure": "提供建物結構的額外資訊",
    "disclose the presence of asbestos and radon in a property": "披露物業中的石棉與氡氣",
    "disclose the use of lead-based paint in a property": "披露含鉛塗料使用情形",
    "licensees are required by state law to disclose or investigate the presence of sex offenders to clients.": "州法要求持照人向客戶披露或調查性罪犯。",
    "licensee disclosure requirements regarding sex offenders are the same as anything else having a material effect on the condition of the property.": "性罪犯披露義務與其他影響屋況之重大事實相同。",
    "licensees are required by federal law to disclose or investigate the presence of sex offenders to clients.": "聯邦法要求持照人向客戶披露或調查性罪犯。",
    "the state of california promulgates a specific, standardized form for residential purchase contracts that all california real estate license holders must use.": "加州官方頒布所有持照人必須使用的標準住宅買賣合約。",
    "any california real estate license holder can write a residential purchase contract.": "任何加州不動產持照人皆可自行撰寫住宅買賣合約。",
    "only members of car can write residential purchase contracts.": "只有 C.A.R. 會員可撰寫住宅買賣合約。",
    "a financial arrangement in which the tenant agrees to pay for real estate taxes, building insurance, and maintenance": "租客同意負擔地產稅、建物保險與維護的財務安排（淨租約）",
    "a deposit paid by the seller to the buyer in order to make agreed-upon repairs": "賣方支付給買方以進行約定修繕的押金",
    "a type of property interest allowing tenants to occupy and use a property they do not own": "允許租客佔用其未擁有物業的權益類型",
    "morals are determined by an external group and are standardized, while ethics are held internally and vary by the individual.": "品行由外部團體標準化；職業道德由個體內心持有且因人而異。",
    "while morals dictate the bare minimum level of acceptable behavior, ethics dictate what is considered acceptable at a higher level.": "品行是最低可接受行為；職業道德是更高標準。",
    "while ethics dictate the bare minimum level of acceptable behavior, morals dictate what is considered acceptable at a higher level.": "職業道德是最低標準；品行是更高標準。",
    "alice's broker makes unwelcome comments about her appearance disguised as compliments. it makes her feel like he doesn't appreciate her work, just her appearance.": "Alice 的經紀人用讚美掩飾對外表的不當評論，使她覺得對方只看外表不看工作。",
    'annette, an asian american woman who grew up in los angeles, is constantly asked where she is "really" from.': "在洛杉磯長大的亞裔美國人 Annette 常被問『你到底從哪裡來』。",
    "the director of the california department of consumer affairs": "加州消費者事務部部長",
    "the governor of california": "加州州長",
    "the california association of realtors® ceo": "加州房地產經紀人協會執行長",
    "estate for years, freehold estate, estate at will, and estate at sufferance": "定期租賃、自由保有產權、意願租賃、默許租賃",
    "estate for years, estate from period to period, equitable estate, and concurrent estate": "定期租賃、週期租賃、衡平產權、共同產權",
    "equitable estate, estate from period to period, estate at will, and freehold estate": "衡平產權、週期租賃、意願租賃、自由保有產權",
    "a landlord's illegal effort to compel a tenant to stay in a lease agreement": "房東非法強迫租客繼續租約",
    "a landlord's use of a lockbox without tenant permission when trying to sell the property": "房東未經租客同意使用密碼盒以便賣屋",
    "a court's granting of a restraining order in a domestic violence case": "法院在家暴案件核發禁制令",
    "an agreement in which the seller guarantees the named broker receives a commission if the property is sold, regardless of who brings the buyer": "賣方保證指定經紀人無論誰帶來買方，只要售出即可取得佣金的協議（獨家專任）",
    "an agreement in which the seller has an exclusive relationship with a broker but retains the right to sell the property to named prospects": "賣方與經紀人專屬代理，但保留自行售予指定對象權利的協議（獨家代理）",
    "a nonexclusive listing agreement that gives multiple brokers (and owners themselves) the right to sell property": "允許多位經紀人（及屋主本人）皆可銷售的非專屬委託（開放委託）",
    "the property is being sold above market value but offers competitive agricultural opportunities.": "物業以高於市價出售，但具有具競爭力的農業機會。",
    "the property is being sold above market value due to inflation.": "物業因通膨而以高於市價出售。",
    "when the offeree communicates acceptance to the offeror": "當受要約人向要約人傳達承諾／接受時",
    "the statute of frauds": "詐欺條例（書面要件法）",
    "effective gross income": "有效總收益（EGI）",
    "net operating income": "淨營業收益（NOI）",
    "when both offeror and offeree have signed the offer": "要約人與受要約人都已簽署要約時",
    "when both offeror and offeree have performed their obligations": "雙方都已履行義務時",
    "when the option period for offer consideration has come to an end and the offeree has accepted the offer": "要約考慮期結束且受要約人已接受時",
    "exclusive right-to-sell agreement": "獨家專任銷售協議",
    "it implies that the recipient got the better of the deal.": "意味著收受方占了便宜。",
    "it is rather meaningless since it is assumed.": "幾乎無意義，因為被視為理所當然。",
    "it is language that should be considered a red flag in the agreement.": "屬協議中應視為紅旗警訊的用語。",
    "an odorless, radioactive gas produced by the decay of other radioactive materials in rocks under the surface of the earth that can cause lung cancer": "地表下岩石放射性物質衰變產生、可致肺癌的無臭放射性氣體（氡氣）",
    "chemical compounds containing chlorine, fluorine, and carbon atoms that were once used in refrigerator coolant, air conditioners, and dehumidifiers": "曾用於冷媒／空調／除濕機的氯氟碳化合物（CFCs）",
    "a naturally occurring mineral that has been used in paint and water pipes": "曾用於油漆與水管的天然礦物（多指鉛）",
    "whether or not the seller has hiv/aids": "賣方是否感染 HIV/AIDS",
    "whether or not the seller is married": "賣方是否已婚",
    "a death on the property that was the result of natural causes six years ago": "六年前該物業發生的自然死亡",
}

# Fallback Chinese stems / explanations for English Qs not covered by bilingual reorder
MANUAL_STEM_ZH = {
    32: "經紀人 Osborn 在網站上為一個普通委託（Open Listing）房屋做行銷三週。事後得知買家列印其網頁、自行看屋並直接向賣方購屋。Osborn 據此要求佣金，他的請求是基於哪項原則？",
    83: "要約（Offer）何時成為具拘束力的合約（binding contract）？",
}
MANUAL_EXPL = {
    32: "正確選項 (A) 解析：在普通委託（Open Listing）下，經紀人必須證明自己是促成交易的主導原因（Procuring Cause）。買家因 Osborn 的網站行銷而發現並購買該屋，構成不中斷的促成鏈，故可主張佣金。\n干擾選項錯誤：專屬代理、網路行銷法、詐欺條例皆非本題佣金請求的法律依據。",
    83: "正確選項 (A) 解析：要約在受要約人（offeree）向要約人（offeror）「傳達／送達接受通知」時，才成為具拘束力的合約。僅簽署但未通知、或雙方尚未履行義務，都不構成承諾完成。",
}


def fill_choice_zh(en: str, zh: str) -> str:
    if zh:
        return zh
    key = en.strip().lower()
    if key in MANUAL_CHOICE_ZH:
        return MANUAL_CHOICE_ZH[key]
    # try without trailing period differences
    key2 = key.rstrip(".")
    for k, v in MANUAL_CHOICE_ZH.items():
        if k.rstrip(".") == key2:
            return v
    return ""


def build_explanation(qnum: int, answer: str, bi: dict | None, fallback_en: str) -> str:
    parts: list[str] = []
    if bi:
        if bi.get("explZh"):
            parts.append(f"正確選項 ({answer}) 解析：{bi['explZh']}")
        if bi.get("tips"):
            parts.append(bi["tips"])
        if bi.get("explEn"):
            parts.append(f"English：{bi['explEn']}")
    if not parts and fallback_en:
        parts.append(f"正確選項 ({answer}) 解析：{fallback_en}")
    return "\n".join(parts).strip()


def format_clean_txt(questions: list[dict]) -> str:
    chunks = [
        "California Real Estate Practice LV17 Assessment（中英對照整理版）",
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


def match_bilingual(english: dict[int, dict], bilingual: dict[int, dict]) -> dict[int, dict]:
    """Bilingual section is topic-ordered; map each English Q to best bilingual block by stem."""
    bi_items = list(bilingual.values())
    used = set()
    matched: dict[int, dict] = {}

    def score(stem: str, bi: dict) -> float:
        fp = stem_fingerprint(stem)
        raw_bi = (bi.get("stemEn") or "").replace("...", " ")
        bp = stem_fingerprint(raw_bi)
        if not fp or not bp:
            # keyword rescue for abbreviated bilingual stems
            for kw in ("osborn", "blithe", "dudley", "latoye", "raul", "betty", "amelia"):
                if kw in stem.lower() and kw in (bi.get("stemEn") or "").lower():
                    return 0.9
            return 0.0
        if fp == bp:
            return 1.0
        if fp in bp or bp in fp:
            return 0.95
        # prefix overlap for ellipsis-abbreviated bilingual stems
        bp_tokens = bp.split()
        fp_tokens = fp.split()
        if len(bp_tokens) >= 4:
            prefix = " ".join(bp_tokens[:6])
            if prefix in fp or all(t in fp_tokens for t in bp_tokens[:5]):
                return 0.9
        ta, tb = set(fp_tokens), set(bp_tokens)
        if not ta or not tb:
            return 0.0
        return len(ta & tb) / max(len(ta), len(tb))

    pairs = []
    for n, e in english.items():
        for bi in bi_items:
            sc = score(e["stemEn"], bi)
            if sc >= 0.45:
                pairs.append((sc, n, id(bi), bi))
    pairs.sort(reverse=True)
    for sc, n, bid, bi in pairs:
        if n in matched or bid in used:
            continue
        matched[n] = bi
        used.add(bid)
    return matched


def main():
    raw = SRC.read_text(encoding="utf-8")
    raw = raw.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    lines = raw.split("\n")

    bi_idx = None
    for i, ln in enumerate(lines):
        if re.match(r"^01\.\s+", ln.strip()):
            bi_idx = i
            break
    eng_lines = lines if bi_idx is None else lines[:bi_idx]
    english = parse_english_section(eng_lines)
    bilingual_raw = parse_bilingual_section(raw)
    bilingual = match_bilingual(english, bilingual_raw)

    questions = []
    missing_stem_zh = []
    missing_choice_zh = []
    unmatched = []
    for n in range(1, 101):
        if n not in english:
            raise SystemExit(f"Missing English question {n}")
        e = english[n]
        bi = bilingual.get(n)
        if not bi:
            unmatched.append(n)
        stem_zh = (bi or {}).get("stemZh") or MANUAL_STEM_ZH.get(n, "")
        stem_en = e["stemEn"]

        zh_map = (bi or {}).get("choiceZhByEn") or {}
        correct_en = (bi or {}).get("correctEn") or e["choicesEn"][e["answer"]]
        correct_zh = (bi or {}).get("correctZh") or ""

        choices = []
        for key in "ABCD":
            en = e["choicesEn"][key]
            zh = lookup_zh(en, zh_map, correct_en, correct_zh)
            zh = fill_choice_zh(en, zh)
            choices.append({"key": key, "en": en, "zh": zh})
            if not zh:
                missing_choice_zh.append(f"Q{n}:{key}:{en[:90]}")

        if not stem_zh:
            missing_stem_zh.append(n)

        explanation = build_explanation(n, e["answer"], bi, e.get("explanationEn", ""))
        if n in MANUAL_EXPL and (not bi or n in (32, 83)):
            explanation = MANUAL_EXPL[n]
        topic = (bi or {}).get("topic") or ""
        questions.append(
            {
                "id": f"L{n:03d}",
                "source": source_for(n),
                "topic": topic,
                "stemEn": stem_en,
                "stemZh": stem_zh,
                "choices": choices,
                "answer": e["answer"],
                "explanation": explanation,
            }
        )

    out = []
    for q in questions:
        topic_short = q["topic"].split("(")[0].strip() if q.get("topic") else ""
        source = q["source"] + (f"：{topic_short}" if topic_short else "")
        out.append(
            {
                "id": q["id"],
                "source": source,
                "stemEn": q["stemEn"],
                "stemZh": q["stemZh"],
                "choices": q["choices"],
                "answer": q["answer"],
                "explanation": q["explanation"],
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    CLEAN.write_text(format_clean_txt(out), encoding="utf-8")

    print(f"Wrote {len(out)} questions -> {OUT}")
    print(f"Wrote formatted text -> {CLEAN}")
    print(f"English parsed: {len(english)}; bilingual blocks: {len(bilingual_raw)}; matched: {len(bilingual)}")
    print(f"unmatched english: {unmatched}")
    print(f"missing stemZh: {missing_stem_zh}")
    print(f"missing choiceZh count: {len(missing_choice_zh)}")
    for row in missing_choice_zh[:50]:
        print("  ", row)
    if len(missing_choice_zh) > 50:
        print(f"  ... and {len(missing_choice_zh) - 50} more")


if __name__ == "__main__":
    main()

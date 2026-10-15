#!/usr/bin/env python3
"""Apply ACS 2024 5-year snapshots and Wave 2 sourced copy into regions.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGIONS = ROOT / "data" / "regions.json"
ACS = ROOT / "scripts" / "_acs_raw.json"

GEO = {
    "diamond-bar": "16000US0619192",
    "walnut": "16000US0683332",
    "rowland-heights": "16000US0663218",
    "hacienda-heights": "16000US0631596",
    "chino-hills": "16000US0613214",
    "ontario": "16000US0653896",
    "pomona": "16000US0658072",
    "culver-city": "16000US0617568",
    "san-marino": "16000US0668224",
    "south-pasadena": "16000US0673220",
    "arcadia": "16000US0602462",
    "temple-city": "16000US0678148",
    "rosemead": "16000US0662896",
    "westchester": "86000US90045",
    "playa-vista": "86000US90094",
}

INDUSTRY = [
    ("C24050011", "教育醫療"),
    ("C24050010", "專業科學管理"),
    ("C24050006", "零售"),
    ("C24050012", "餐旅娛樂"),
    ("C24050004", "製造"),
    ("C24050007", "運輸倉儲公用"),
    ("C24050009", "金融保險地產"),
    ("C24050008", "資訊"),
    ("C24050003", "營造"),
    ("C24050014", "公共行政"),
    ("C24050005", "批發"),
    ("C24050013", "其他服務"),
    ("C24050002", "農林漁礦"),
]


def est(block, key):
    if not block:
        return None
    val = (block.get("estimate") or {}).get(key)
    return val


def pct(part, whole):
    if part is None or not whole:
        return None
    return round(100.0 * part / whole, 1)


def snapshot_from_acs(acs_geo, unit, price_sfh, price_as_of):
    pop = est(acs_geo.get("B01003"), "B01003001")
    race_t = est(acs_geo.get("B02001"), "B02001001")
    asian = est(acs_geo.get("B02001"), "B02001005")
    hisp_t = est(acs_geo.get("B03003"), "B03003001")
    hisp = est(acs_geo.get("B03003"), "B03003003")
    income = est(acs_geo.get("B19013"), "B19013001")
    edu_t = est(acs_geo.get("B15003"), "B15003001")
    bach = sum(
        est(acs_geo.get("B15003"), k) or 0
        for k in ("B15003022", "B15003023", "B15003024", "B15003025")
    )
    ten_t = est(acs_geo.get("B25003"), "B25003001")
    owner = est(acs_geo.get("B25003"), "B25003002")
    ind_t = est(acs_geo.get("C24050"), "C24050001")
    industries = []
    if ind_t:
        ranked = []
        for key, label in INDUSTRY:
            n = est(acs_geo.get("C24050"), key)
            if n is None:
                continue
            ranked.append(
                {"key": key, "labelZh": label, "pct": round(100.0 * n / ind_t, 1)}
            )
        industries = sorted(ranked, key=lambda x: x["pct"], reverse=True)[:3]
    return {
        "vintage": "ACS 2020–2024",
        "priorVintage": None,
        "population": int(pop) if pop is not None else None,
        "populationDeltaPct": None,
        "asianAlonePct": pct(asian, race_t),
        "hispanicPct": pct(hisp, hisp_t),
        "medianIncome": int(income) if income is not None else None,
        "medianIncomeDeltaPct": None,
        "bachelorsPlusPct": pct(bach, edu_t),
        "ownerOccupiedPct": pct(owner, ten_t),
        "residentIndustry": industries,
        "priceSfh": price_sfh,
        "priceAsOf": price_as_of,
        "unit": unit,
    }


def add_source(region, src):
    urls = {s.get("url") for s in region.get("sources") or []}
    if src["url"] in urls:
        return
    region.setdefault("sources", []).append(src)


def main():
    data = json.loads(REGIONS.read_text(encoding="utf-8"))
    acs = json.loads(ACS.read_text(encoding="utf-8"))
    acs_data = acs["data"]

    price_keep = {}
    for r in data["regions"]:
        price_keep[r["id"]] = (
            (r.get("snapshot") or {}).get("priceSfh"),
            (r.get("snapshot") or {}).get("priceAsOf"),
        )

    # Living-in SFH (same axis). Neighborhood all-types stay out of priceSfh.
    price_keep["culver-city"] = (1799283, "2026-10")
    price_keep["san-marino"] = (3448625, "2026-10")
    price_keep["south-pasadena"] = (1844265, "2026-10")
    price_keep["arcadia"] = (1949223, "2026-10")
    price_keep["temple-city"] = (1191525, "2026-10")
    price_keep["rosemead"] = (924631, "2026-10")
    price_keep["westchester"] = (None, None)
    price_keep["playa-vista"] = (None, None)

    by_id = {r["id"]: r for r in data["regions"]}
    for rid, geoid in GEO.items():
        region = by_id[rid]
        unit = "zcta" if (region.get("geo") or {}).get("kind") == "zcta" else "place"
        ps, pa = price_keep[rid]
        region["snapshot"] = snapshot_from_acs(acs_data[geoid], unit, ps, pa)
        add_source(
            region,
            {
                "label": "Census Reporter ACS 2024 5-year",
                "url": f"https://censusreporter.org/profiles/{geoid}",
                "date": "2026-10-15",
                "note": "ACS 2020–2024 via Census Reporter API; industry C24050 resident employment",
            },
        )

    apply_copy(by_id)
    for cl in data["clusters"]:
        if cl["id"] == "westside-lax":
            cl["blurbZh"] = (
                "Westchester（ZCTA 90045）、Playa Vista（ZCTA 90094）、Culver City（獨立市）。"
                "前兩格不是市；Culver 已可進 SFH 對照軸。"
            )
        elif cl["id"] == "core-sgv-north":
            cl["blurbZh"] = (
                "南帕薩迪納、聖馬利諾、亞凱迪亞、天普市、羅斯密。"
                "五城皆有 Living-in SFH；羅斯密學區是拼圖。"
            )
        elif cl["id"] == "east-sgv-60":
            cl["blurbZh"] = (
                "鑽石吧、沃爾納特、羅蘭崗、哈仙達崗。"
                "哈仙達崗 SFH 單獨中位尚未與他城同軸，對照條故意留空。"
            )
    data["dataNotesZh"] = (
        "盤點日 2026-10-15。ACS 人口／所得／產業為 2020–2024 五年估計（Census Reporter），"
        "不是今年行情。Asian alone ≠ 台／陸籍。Westchester／Playa Vista 用 ZCTA。"
        "SFH 對照軸只放 Redfin Living-in 獨立屋中位；全類型另寫在價格帶。"
    )
    REGIONS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for r in data["regions"]:
        s = r["snapshot"]
        print(
            f"{r['id']:18} pop={s['population']} asian={s['asianAlonePct']} "
            f"hisp={s['hispanicPct']} inc={s['medianIncome']} sfh={s['priceSfh']} "
            f"{[x['labelZh'] for x in s['residentIndustry']]}"
        )


def apply_copy(by_id):
    # --- Batch 5 helper used across all cities ---
    def set_explain(rid, text):
        by_id[rid]["explainZh"] = text

    # Batch 1: ACS-backed explain + trend for Wave 1
    w1_explain = {
        "diamond-bar": "展示時先指 60／57 交會的山城，再講雙學區。ACS 亞裔是普查分類，不要說成台籍比例。",
        "walnut": "東 SGV 標尺城：同廊道裡所得與亞裔比例都偏高。先問是不是 WVUSD，再比鑽石吧預算。",
        "rowland-heights": "開場先講「不是市、是 CDP」。華人商圈強，但市政服務走縣府／特別區。",
        "hacienda-heights": "不要和羅蘭崗混成同一個華人崗。亞裔與西語裔都高；SFH 單獨中位尚未與他城對齊，對照條空白是故意的。",
        "chino-hills": "跨出 LA 縣。規劃社區＋CVUSD。價位接近東 SGV 中段，通勤軸換成 71／60／91。",
        "ontario": "物流與機場城，不是東 SGV 延伸社區。學區是拼圖，地址沒對完不要報校名。",
        "pomona": "LA 縣、價位接近安大略、學區 PUSD。部分鑽石吧地址也是 PUSD，可當學區對照。",
    }
    for rid, text in w1_explain.items():
        set_explain(rid, text)

    s = lambda rid: by_id[rid]["snapshot"]

    def belt(rid, prefix):
        x = s(rid)
        extra = (
            f"ACS 2020–2024：人口約 {x['population']:,}、Asian alone {x['asianAlonePct']}%"
            + (f"、Hispanic {x['hispanicPct']}%" if x["hispanicPct"] is not None else "")
            + f"、家戶所得中位 ${x['medianIncome']:,}。"
            " Asian alone 是普查分類，不是台／陸籍。"
        )
        return prefix + extra

    by_id["diamond-bar"]["basics"]["chineseBelt"] = belt(
        "diamond-bar", "LA 縣建制市。"
    )
    by_id["walnut"]["basics"]["chineseBelt"] = belt(
        "walnut", "LA 縣建制市。東 SGV 山市標尺。"
    )
    by_id["rowland-heights"]["basics"]["chineseBelt"] = belt(
        "rowland-heights",
        "LA County 未建制 CDP（非獨立市）。Redfin Living-in 稱其為區域華人文化／商業活動中心之一。",
    )
    by_id["hacienda-heights"]["basics"]["chineseBelt"] = belt(
        "hacienda-heights",
        "LA County 未建制 CDP。亞裔與西語裔都高，不是單一族群標籤。",
    )
    by_id["chino-hills"]["basics"]["chineseBelt"] = belt(
        "chino-hills",
        "San Bernardino County 建制市（1991-12-01 建市，市府 Demographics）。",
    )
    by_id["ontario"]["basics"]["chineseBelt"] = belt(
        "ontario",
        "San Bernardino County 大城。非華人多數城 — 勿用東 SGV 標籤套用。",
    )
    by_id["pomona"]["basics"]["chineseBelt"] = belt(
        "pomona",
        "LA 縣建制市。舊城與各 ZIP 差異大，勿套東 SGV 山市標籤。",
    )

    def trend(rid):
        x = s(rid)
        bits = []
        if x["population"] is not None:
            bits.append(f"人口約 {x['population']:,}")
        if x["asianAlonePct"] is not None:
            bits.append(f"Asian alone {x['asianAlonePct']}%")
        if x["hispanicPct"] is not None:
            bits.append(f"Hispanic {x['hispanicPct']}%")
        if x["medianIncome"] is not None:
            bits.append(f"家戶所得中位 ${x['medianIncome']:,}")
        if x["bachelorsPlusPct"] is not None:
            bits.append(f"學士+ {x['bachelorsPlusPct']}%")
        if x["ownerOccupiedPct"] is not None:
            bits.append(f"自住 {x['ownerOccupiedPct']}%")
        top = "、".join(i["labelZh"] + f" {i['pct']}%" for i in (x["residentIndustry"] or [])[:3])
        line = "ACS 2020–2024：" + "；".join(bits) + "。五年估計，非今年行情。"
        if top:
            line += f" 居民產業前三：{top}。"
        return line

    for rid in GEO:
        by_id[rid]["trendLine"] = trend(rid)
        by_id[rid]["lastReviewed"] = "2026-10-15"

    # Wave 1 jobs: point to resident industry
    for rid in ("diamond-bar", "walnut", "rowland-heights", "hacienda-heights", "chino-hills"):
        top = by_id[rid]["snapshot"]["residentIndustry"]
        if top:
            by_id[rid]["highlights"]["jobs"] = (
                f"居民從事的產業前三（ACS 2020–2024，不是本地崗位）："
                + "、".join(f"{i['labelZh']} {i['pct']}%" for i in top)
                + "。就業仍多依賴區域通勤。"
            )
    ont_top = by_id["ontario"]["snapshot"]["residentIndustry"]
    by_id["ontario"]["highlights"]["jobs"] = (
        "本地有機場／物流敘事（Economic Census 運輸倉儲），但展示條只講居民就業。"
        + (
            " ACS 居民前三：" + "、".join(f"{i['labelZh']} {i['pct']}%" for i in ont_top) + "。"
            if ont_top
            else ""
        )
    )
    pom_top = by_id["pomona"]["snapshot"]["residentIndustry"]
    by_id["pomona"]["highlights"]["jobs"] = (
        "區域就業＋高等教育／展會地標（Cal Poly Pomona、Fairplex）。"
        + (
            " 居民產業前三：" + "、".join(f"{i['labelZh']} {i['pct']}%" for i in pom_top) + "。"
            if pom_top
            else ""
        )
    )

    # --- Batch 2: Westside ---
    w = by_id["westchester"]
    w["status"] = "review"
    w["basics"]["chineseBelt"] = (
        "LA 市內社區，不是獨立市。ACS／地圖用 ZCTA 90045（含 LAX 周邊），"
        f"人口約 {s('westchester')['population']:,}、Asian alone {s('westchester')['asianAlonePct']}%（普查分類）。"
        "口語「西徹斯特」比 ZCTA 小，不要用全市 LA 數字代替。"
    )
    w["basics"]["schoolBand"] = (
        "LAUSD。請用 LAUSD Resident School Identifier 對址，不引用單一校分數。"
        "Redfin 社區頁常見 Kentwood／Cowan／Playa Del Rey 等校名，僅作線索。"
    )
    w["priceBand"] = {
        "sfhRange": "未取得與他城同口徑的 Redfin Living-in SFH 中位 — 對照條留空。",
        "condoRange": "Redfin 社區 housing-market：全類型近 3 月中位約 $1,683,414（至 2026-06）。此為社區／全類型，不是 SFH 軸。",
        "ageProfile": "戰後郊區屋與更新案混雜；以建造年為準。",
        "hoaMello": "部分規劃村有 HOA；LA 市社區另須確認市政與機場噪音／航道。",
        "asOf": "2026-06",
    }
    w["highlights"]["jobs"] = (
        "鄰 LAX 與 LMU。居民就業不是本地崗位：ACS 前三為"
        + "、".join(f"{i['labelZh']} {i['pct']}%" for i in s("westchester")["residentIndustry"])
        + "。不要把機場地標說成全市職業結構。"
    )
    w["highlights"]["amenities"] = "靠近 LAX、Westchester 商業帶與 LMU；常和 Playa Vista／Culver City 一起被西區客人問。"
    w["highlights"]["buyerFit"] = "要近機場／西區、能接受 LA 市與 LAUSD 對址的自住或企業派駐。"
    w["caveats"]["propertyCaveats"] = "90045 含住宅與機場相關用地；帶看分清住商、航道與噪音，勿把 ZCTA 當市界。"
    w["caveats"]["schoolReality"] = "LAUSD 對址。不要用 Culver City USD 套過來。"
    w["caveats"]["pitchLine"] = (
        "西徹斯特是 LA 市社區（不是市），ZIP 90045；普查用 ZCTA，範圍含 LAX 周邊。"
        f"ACS 人口約 {s('westchester')['population']:,}。房價對照先講全類型約 $168 萬級（Redfin 社區，2026-06），SFH 軸暫空。"
    )
    w["compareLine"] = "Culver City 是獨立市＋CCUSD；西徹斯特仍在 LA 市／LAUSD。Playa Vista 更新、更規劃，但是同一個 LA 市框架。"
    w["explainZh"] = "先講「不是市」。地圖看左下小圖。數字是郵區不是口語社區；含 LAX 周邊，但居民產業前三是專業／教育醫療／資訊，不是「人人在機場上班」。"
    add_source(w, {"label": "LAUSD Resident School Identifier", "url": "https://rsi.lausd.net/ResidentSchoolIdentifier/", "date": "2026-10-15", "note": "Address-level LAUSD lookup"})
    add_source(w, {"label": "Redfin Westchester LA housing market", "url": "https://www.redfin.com/neighborhood/290650/CA/Los-Angeles/Westchester/housing-market", "date": "2026-06", "note": "Neighborhood all-types median $1,683,414; not SFH axis"})

    p = by_id["playa-vista"]
    p["status"] = "review"
    p["basics"]["chineseBelt"] = (
        "LA 市內較新規劃社區，不是市。ACS 用很小的 ZCTA 90094，"
        f"人口僅約 {s('playa-vista')['population']:,}，百分比會跳、誤差大。"
    )
    p["basics"]["schoolBand"] = "LAUSD。對址用官方工具。鄰近討論常見 Playa Vista Elementary，仍不是全市保證。"
    p["priceBand"] = {
        "sfhRange": "未取得 Living-in SFH 分拆；社區以 Condo／規劃產品為主，不進 SFH 對照軸。",
        "condoRange": "Redfin 社區 housing-market 全類型中位約 $1,280,000（頁面寫至 2026-03 的三個月）。Culver City Living-in 鄰里表亦列 Playa Vista $1,280,000。",
        "ageProfile": "2000 年代後規劃為主；HOA／CC&Rs 幾乎必讀。",
        "hoaMello": "規劃社區 HOA 常見；費用與租賃限制逐案。",
        "asOf": "2026-03",
    }
    p["highlights"]["jobs"] = (
        "西區媒體／科技通勤敘事常見。ACS 基數小，只作方向："
        + "、".join(f"{i['labelZh']} {i['pct']}%" for i in s("playa-vista")["residentIndustry"]) + "。"
    )
    p["highlights"]["amenities"] = "Redfin／Culver 指南常把它和 Culver City、Westchester 放在同一西區比較表。"
    p["highlights"]["buyerFit"] = "要較新規劃、能接受 HOA 與 Condo 權重、並拿來和 Culver City 比總價的客人。"
    p["caveats"]["propertyCaveats"] = "90094 很小，listing 可能跨相鄰 ZIP；HOA 與出租規則先讀。"
    p["caveats"]["schoolReality"] = "LAUSD，不是 CCUSD。"
    p["caveats"]["pitchLine"] = (
        "Playa Vista（90094）是 LA 市規劃社區，不是市。常和 Culver City 一起比較，但行政與學區是兩套。"
        "全類型中位約 $128 萬級（Redfin 社區，資料較舊至 2026-03）；SFH 軸故意留空。"
    )
    p["compareLine"] = "Culver City 有自己的市府與 CCUSD；Playa Vista 更新、HOA 更密，但仍是 LA 市。別把兩格的人口加總成「一座西區市」。"
    p["explainZh"] = "小郵區、百分比不穩。對客重點是規劃社區＋LA 市，不是再造一個市名。"
    add_source(p, {"label": "Redfin Playa Vista housing market", "url": "https://www.redfin.com/neighborhood/496706/CA/Los-Angeles/Playa-Vista/housing-market", "date": "2026-03", "note": "Neighborhood all-types median $1,280,000"})
    add_source(p, {"label": "Redfin Culver City living-in neighborhood table", "url": "https://www.redfin.com/living-in/CA/Culver-City/6/4557", "date": "2026-10-15", "note": "Lists Playa Vista neighborhood median $1,280,000"})

    c = by_id["culver-city"]
    c["status"] = "ready"
    c["basics"]["chineseBelt"] = (
        "LA 縣建制市（非 LA 市）。"
        f"ACS 人口約 {s('culver-city')['population']:,}、Asian alone {s('culver-city')['asianAlonePct']}%、Hispanic {s('culver-city')['hispanicPct']}%。"
        "90230 只是 ZIP 之一，普查用全市。"
    )
    c["basics"]["schoolBand"] = "Culver City Unified School District（CCUSD）。地址仍須向學區確認。"
    c["priceBand"] = {
        "sfhRange": "SFH 中位約 $1,799,283（Redfin Living-in）",
        "condoRange": "Condo/Co-op 中位約 $599,938；Townhouse 中位約 $1,199,014。全類型中位約 $1,399,334。",
        "ageProfile": "舊城、Fox Hills、媒體園區周邊屋齡差大。",
        "hoaMello": "Condo／部分規劃區有 HOA；逐案查 CC&Rs。",
        "asOf": "2026-10",
    }
    c["highlights"]["jobs"] = (
        "Redfin 指南稱電影／電視製作樞紐（Sony Pictures 等公開地標）。居民產業≠人人在片場："
        + " ACS 前三 " + "、".join(f"{i['labelZh']} {i['pct']}%" for i in s("culver-city")["residentIndustry"]) + "。"
    )
    c["highlights"]["amenities"] = "Redfin：約 13 座公園、Walk Score 76；Downtown Culver／Washington Blvd 餐飲。列舉 Museum of Jurassic Technology、Kirk Douglas Theatre、Culver City Park。"
    c["highlights"]["buyerFit"] = "要西區獨立市、CCUSD、能接受 SFH 中位明顯高於東 SGV 中段的客人。"
    c["caveats"]["propertyCaveats"] = "全市 ZIP 含 90230／90232；帶看分區，勿用單一郵遞區號概括。"
    c["caveats"]["schoolReality"] = "CCUSD 為主軸，仍用地址確認。"
    c["caveats"]["pitchLine"] = (
        "Culver City 是西區獨立市，不是 LA 市；學區 CCUSD。"
        "SFH 中位約 $180 萬、全類型約 $140 萬（Redfin Living-in）。"
        "和 Westchester／Playa Vista 最大差別是「有自己的市府與學區」。"
    )
    c["compareLine"] = "若客人從聖蓋博來：這是西區就業與總價結構，不是 210 廊道名校市。和西徹斯特比，這裡是市、那裡是 LA 市社區。"
    c["explainZh"] = "獨立市。先報 CCUSD 與 SFH／Condo 價差（Condo 約 $60 萬級），再比隔壁兩塊 ZCTA。"
    add_source(c, {"label": "Redfin Culver City living-in", "url": "https://www.redfin.com/living-in/CA/Culver-City/6/4557", "date": "2026-10-15", "note": "SFH $1,799,283; Condo $599,938; TH $1,199,014; all-types $1,399,334"})
    add_source(c, {"label": "Redfin Culver City housing market", "url": "https://www.redfin.com/city/4557/CA/Culver-City/housing-market", "date": "2026-09", "note": "All-types ~$1.3M on market page; Living-in used for type split"})
    add_source(c, {"label": "Culver City Unified School District", "url": "https://www.ccusd.org/", "date": "2026-10-15", "note": "District serving Culver City"})

    # --- Batch 3: 110/210 ---
    sm = by_id["san-marino"]
    sm["status"] = "ready"
    sm["basics"]["chineseBelt"] = (
        "LA 縣建制小城。"
        f"ACS 人口約 {s('san-marino')['population']:,}、Asian alone {s('san-marino')['asianAlonePct']}%、"
        f"家戶所得中位約 ${s('san-marino')['medianIncome']:,}、學士+ {s('san-marino')['bachelorsPlusPct']}%。"
        "基數小，百分比波動大。"
    )
    sm["priceBand"] = {
        "sfhRange": "SFH 中位約 $3,448,625（Redfin Living-in；與全類型 $3,448,358 几乎同一量級——庫存以獨立屋為主）",
        "condoRange": "Living-in 未另列穩定 Condo 分拆；小城庫存少，逐案 MLS。",
        "ageProfile": "經典住宅街區與改建並存；規範須問市府。",
        "hoaMello": "多數討論為獨立屋地稅／特別評估，HOA 非全市預設。",
        "asOf": "2026-10",
    }
    sm["highlights"]["jobs"] = (
        "自住向小城，就業多通勤。"
        + " 居民前三：" + "、".join(f"{i['labelZh']} {i['pct']}%" for i in s("san-marino")["residentIndustry"]) + "。"
    )
    sm["highlights"]["amenities"] = "Redfin：Huntington Library／植物園、Lacy Park。開場地標用亨廷頓，不包裝成「保證學區分數」。"
    sm["highlights"]["buyerFit"] = "預算能對上北聖蓋博最高總價帶、鎖定 SMUSD 的自住家庭。"
    sm["caveats"]["propertyCaveats"] = "小城、成交筆數少（housing-market 近月約 30 筆量級），中位會被單筆豪宅拉動。"
    sm["caveats"]["schoolReality"] = "SMUSD，不要用帕薩迪納或亞凱迪亞學區名套過來。"
    sm["caveats"]["pitchLine"] = (
        "聖馬利諾（91108）是獨立小城，不是帕薩迪納一區。"
        "SFH 中位約 $345 萬（Redfin Living-in）。先講 SMUSD 與總價，再比南帕／亞凱迪亞。"
    )
    sm["compareLine"] = "亞凱迪亞盤面較大、SFH 約 $195 萬級；南帕 SFH 約 $184 萬級。聖馬是「更小、更貴、另一套 USD」。"
    sm["explainZh"] = "總價錨點。筆數少，中位敏感。學區只報 SMUSD，不報排名。"
    add_source(sm, {"label": "Redfin San Marino living-in", "url": "https://www.redfin.com/living-in/CA/San-Marino/6/17481", "date": "2026-10-15", "note": "SFH $3,448,625; all-types $3,448,358"})
    add_source(sm, {"label": "Redfin San Marino housing market", "url": "https://www.redfin.com/city/17481/CA/San-Marino/housing-market", "date": "2026-08", "note": "All-types $3,448,718; 3 months ending Aug 2026"})
    add_source(sm, {"label": "San Marino Unified School District", "url": "https://www.smusd.us/", "date": "2026-10-15", "note": "SMUSD"})

    sp = by_id["south-pasadena"]
    sp["status"] = "ready"
    sp["basics"]["chineseBelt"] = (
        "LA 縣建制小城，夾在帕薩迪納與 LA 市之間。"
        f"ACS 人口約 {s('south-pasadena')['population']:,}、Asian alone {s('south-pasadena')['asianAlonePct']}%、"
        f"Hispanic {s('south-pasadena')['hispanicPct']}%、學士+ {s('south-pasadena')['bachelorsPlusPct']}%。"
    )
    sp["priceBand"] = {
        "sfhRange": "SFH 中位約 $1,844,265（Redfin Living-in）",
        "condoRange": "Condo/Co-op 中位約 $910,906；Townhouse 中位約 $1,374,516。全類型中位約 $1,649,215。",
        "ageProfile": "老街區與歷史建築常見。",
        "hoaMello": "Condo／少數規劃案有 HOA；老屋改建規範可能比新區嚴。",
        "asOf": "2026-10",
    }
    sp["highlights"]["jobs"] = (
        "近 DTLA／110。居民前三："
        + "、".join(f"{i['labelZh']} {i['pct']}%" for i in s("south-pasadena")["residentIndustry"]) + "。"
    )
    sp["highlights"]["amenities"] = "Redfin：Walk Score 67、Transit 50；Mission／Fair Oaks 餐飲、Garfield Park、Arroyo Seco 綠帶。"
    sp["highlights"]["buyerFit"] = "要老街區尺度、SPUSD、能接受小城庫存的自住比較者。"
    sp["caveats"]["propertyCaveats"] = "歷史街區改建／停車規範須問市府。"
    sp["caveats"]["schoolReality"] = "SPUSD 與帕薩迪納、LAUSD 都不同。"
    sp["caveats"]["pitchLine"] = (
        "南帕薩迪納（91030）是獨立市，不是「帕薩迪納南邊某區」。學區 SPUSD，通勤軸 110。"
        "SFH 約 $184 萬、全類型約 $165 萬（Redfin Living-in）。"
    )
    sp["compareLine"] = "和聖馬比：都是小城，但兩套 USD、總價差一截。和亞凱迪亞比：南帕更靠 110／LA 市邊界。"
    sp["explainZh"] = "開場三句：獨立市、110、SPUSD。老屋改建別承諾能加蓋。"
    add_source(sp, {"label": "Redfin South Pasadena living-in", "url": "https://www.redfin.com/living-in/CA/South-Pasadena/6/18661", "date": "2026-10-15", "note": "SFH $1,844,265; Condo $910,906; TH $1,374,516; all-types $1,649,215"})
    add_source(sp, {"label": "Redfin South Pasadena housing market", "url": "https://www.redfin.com/city/18661/CA/South-Pasadena/housing-market", "date": "2026-09", "note": "All-types $1,649,215; 3 months ending Sep 2026"})
    add_source(sp, {"label": "South Pasadena Unified School District", "url": "https://www.spusd.net/", "date": "2026-10-15", "note": "SPUSD"})

    ar = by_id["arcadia"]
    ar["status"] = "ready"
    ar["basics"]["chineseBelt"] = (
        "LA 縣建制市，北聖蓋博標尺。"
        f"ACS 人口約 {s('arcadia')['population']:,}、Asian alone {s('arcadia')['asianAlonePct']}%、"
        f"家戶所得中位約 ${s('arcadia')['medianIncome']:,}。"
    )
    ar["priceBand"] = {
        "sfhRange": "SFH 中位約 $1,949,223（Redfin Living-in）",
        "condoRange": "Condo/Co-op 中位約 $828,915；Townhouse 中位約 $918,011。全類型中位約 $1,739,172。",
        "ageProfile": "平地與山麓、賽馬場／植物園周邊差異大。",
        "hoaMello": "Condo／部分社區有 HOA；逐案。",
        "asOf": "2026-10",
    }
    ar["highlights"]["jobs"] = (
        "自住向郊區市。居民前三："
        + "、".join(f"{i['labelZh']} {i['pct']}%" for i in s("arcadia")["residentIndustry"]) + "。"
    )
    ar["highlights"]["amenities"] = "Redfin：Santa Anita、LA County Arboretum、Arcadia County Park。Baldwin／Huntington 商業。"
    ar["highlights"]["buyerFit"] = "鎖定 AUSD、需要比聖馬更大盤面的自住家庭。"
    ar["caveats"]["propertyCaveats"] = "91006／91007 與山麓／平地屋況不同。"
    ar["caveats"]["schoolReality"] = "多數討論指向 AUSD，仍不是全市單一保證。"
    ar["caveats"]["pitchLine"] = (
        "亞凱迪亞（91006／91007）學區主軸 AUSD，當北聖蓋博標尺。"
        "SFH 約 $195 萬、全類型約 $174 萬（Redfin Living-in）。往上比聖馬、往下比天普市。"
    )
    ar["compareLine"] = "若你熟鑽石吧／Walnut：亞凱是 210 廊道另一套名校市，不是 60 廊道延伸。總價帶高於東 SGV 山市。"
    ar["explainZh"] = "210 標尺。先 AUSD 對址，再把聖馬（更貴更小）和天普市（較可接近）放到同一句。"
    add_source(ar, {"label": "Redfin Arcadia living-in", "url": "https://www.redfin.com/living-in/CA/Arcadia/6/645", "date": "2026-10-15", "note": "SFH $1,949,223; Condo $828,915; TH $918,011; all-types $1,739,172"})
    add_source(ar, {"label": "Redfin Arcadia housing market", "url": "https://www.redfin.com/city/645/CA/Arcadia/housing-market", "date": "2026-08", "note": "All-types $1,645,000 on market page (Aug 2026); Living-in used for type split"})
    add_source(ar, {"label": "Arcadia Unified School District", "url": "https://www.ausd.net/", "date": "2026-10-15", "note": "AUSD"})

    # --- Batch 4: Temple City / Rosemead ---
    tc = by_id["temple-city"]
    tc["status"] = "ready"
    tc["basics"]["chineseBelt"] = (
        "LA 縣建制市。相對亞凱／聖馬，常被當成同廊道較可接近的自住市。"
        f"ACS 人口約 {s('temple-city')['population']:,}、Asian alone {s('temple-city')['asianAlonePct']}%、"
        f"Hispanic {s('temple-city')['hispanicPct']}%。"
    )
    tc["priceBand"] = {
        "sfhRange": "SFH 中位約 $1,191,525（Redfin Living-in）",
        "condoRange": "Condo/Co-op 中位約 $749,923；Townhouse 中位約 $988,012。全類型中位約 $1,174,441（housing-market 至 2026-09）。",
        "ageProfile": "戰後郊區屋為主，屋況差大。",
        "hoaMello": "Condo 較常見 HOA；獨立屋逐案。",
        "asOf": "2026-09",
    }
    tc["highlights"]["jobs"] = (
        "自住＋區域通勤。居民前三："
        + "、".join(f"{i['labelZh']} {i['pct']}%" for i in s("temple-city")["residentIndustry"]) + "。"
    )
    tc["highlights"]["amenities"] = "Redfin：Camellia Festival、Las Tunas／Rosemead Blvd 餐飲、Temple City Park。"
    tc["highlights"]["buyerFit"] = "要北聖蓋博自住、預算低於亞凱／聖馬、學區走 TCUSD 的比較者。"
    tc["caveats"]["propertyCaveats"] = "與羅斯密／亞凱迪亞交界地址要看清門牌所在市。"
    tc["caveats"]["schoolReality"] = "以 TCUSD 為主；交界可能被誤以為亞凱迪亞 — 必須對址。"
    tc["caveats"]["pitchLine"] = (
        "天普市（91780）獨立市、學區 TCUSD。"
        "SFH 約 $119 萬、全類型約 $117 萬（Redfin）。常和羅斯密一起問，市政與學區不同。"
    )
    tc["compareLine"] = "亞凱 SFH 約 $195 萬級、聖馬約 $345 萬級；天普市是同廊道較可接近的自住市。羅斯密更偏商業帶、學區拼圖更複雜。"
    tc["explainZh"] = "可接近的 210 自住市。先 TCUSD，再把羅斯密當隔壁對照而不是同一座城。"
    add_source(tc, {"label": "Redfin Temple City living-in", "url": "https://www.redfin.com/living-in/CA/Temple-City/6/19707", "date": "2026-10-15", "note": "SFH $1,191,525; Condo $749,923; TH $988,012; all-types $1,174,441"})
    add_source(tc, {"label": "Redfin Temple City housing market", "url": "https://www.redfin.com/city/19707/CA/Temple-City/housing-market", "date": "2026-09", "note": "All-types $1,174,441; 3 months ending Sep 2026"})
    add_source(tc, {"label": "Temple City Unified School District", "url": "https://www.tcusd.net/", "date": "2026-10-15", "note": "TCUSD"})

    rm = by_id["rosemead"]
    rm["status"] = "ready"
    rm["basics"]["chineseBelt"] = (
        "LA 縣建制市。Valley Blvd／Garvey 商業帶強；不要用聖馬客群標籤套過來。"
        f"ACS 人口約 {s('rosemead')['population']:,}、Asian alone {s('rosemead')['asianAlonePct']}%、"
        f"Hispanic {s('rosemead')['hispanicPct']}%。"
    )
    rm["basics"]["schoolBand"] = (
        "市府列出三套：Garvey School District、Rosemead School District（K-8）、"
        "高中多走 El Monte Union High（Rosemead High）。必須用地址查，禁止報單一 USD。"
    )
    rm["priceBand"] = {
        "sfhRange": "SFH 中位約 $924,631（Redfin Living-in）",
        "condoRange": "Condo/Co-op 中位約 $659,932；Townhouse 中位約 $745,009。全類型中位約 $923,060（至 2026-09）。",
        "ageProfile": "主幹道商業與巷內住宅混雜。",
        "hoaMello": "Condo／少數新案有 HOA。",
        "asOf": "2026-09",
    }
    rm["highlights"]["jobs"] = (
        "Redfin：Edison International 總部在本市（公開地標，不是全市職業結構）。"
        " 居民前三：" + "、".join(f"{i['labelZh']} {i['pct']}%" for i in s("rosemead")["residentIndustry"]) + "。"
    )
    rm["highlights"]["amenities"] = "Valley Blvd／Garvey 餐飲與超市密集；Rosemead Park 等。"
    rm["highlights"]["buyerFit"] = "要聖蓋博生活圈機能、總價低於聖馬／亞凱、能接受學區對址功課的客人。"
    rm["caveats"]["propertyCaveats"] = "商業走廊與住宅混雜；帶看分清主幹道與巷內。"
    rm["caveats"]["schoolReality"] = "K-8 可能是 Garvey 或 Rosemead SD，高中多為 EMUHSD — 成交條件寫明對址。"
    rm["caveats"]["pitchLine"] = (
        "羅斯密（91770）獨立市，商業帶強、學區是拼圖。"
        "SFH 約 $92 萬、全類型約 $92 萬（Redfin Living-in，兩者接近）。先對地址再比天普市。"
    )
    rm["compareLine"] = "和天普市比：隔壁、客群重疊，但羅斯密不是單一 USD 故事，總價帶也較低。和聖馬比則街廓與總價完全不同。"
    rm["explainZh"] = "先講學區拼圖（Garvey／Rosemead SD／EMUHSD），再講 Valley Blvd 機能。不要用聖馬標籤。"
    add_source(rm, {"label": "City of Rosemead — school districts", "url": "https://rosemeadca.hosted.civiclive.com/contacts/resources/local_resources/school_districts", "date": "2026-10-15", "note": "Garvey SD, Rosemead SD, EMUHSD / Rosemead High"})
    add_source(rm, {"label": "Rosemead School District About", "url": "https://www.rosemead.k12.ca.us/our-district", "date": "2026-10-15", "note": "K-8 serves Rosemead and portions of El Monte, San Gabriel, Temple City"})
    add_source(rm, {"label": "Redfin Rosemead living-in", "url": "https://www.redfin.com/living-in/CA/Rosemead/6/16137", "date": "2026-10-15", "note": "SFH $924,631; Condo $659,932; TH $745,009; all-types $923,060"})
    add_source(rm, {"label": "Redfin Rosemead housing market", "url": "https://www.redfin.com/city/16137/CA/Rosemead/housing-market", "date": "2026-09", "note": "All-types $923,060; 3 months ending Sep 2026"})

    hh = by_id["hacienda-heights"]
    hh["priceBand"]["sfhRange"] = (
        "仍未取得與他城同頁口徑的 Redfin Living-in SFH 單獨中位。"
        "ZIP 91745 全類型中位約 $970,500（至 2026-08）只寫在備註，不進 SFH 對照軸。"
    )
    hh["explainZh"] = "對照條 SFH 空白是口徑，不是沒有市場。亞裔與西語裔都高，別預設單一客群。"

    # Batch 5 extra compare polish for wave 1 using ACS
    by_id["diamond-bar"]["compareLine"] = (
        f"Walnut 亞裔約 {s('walnut')['asianAlonePct']}%、SFH 約 $130 萬；鑽石吧亞裔約 {s('diamond-bar')['asianAlonePct']}%、SFH 約 $123 萬，但學區可能是 WVUSD 或 PUSD。"
    )
    by_id["walnut"]["compareLine"] = (
        f"Wave 1 裡 ACS 亞裔 {s('walnut')['asianAlonePct']}%、所得中位約 ${s('walnut')['medianIncome']:,}，當東 SGV 天花板再往羅蘭崗／鑽石吧比預算。"
    )
    by_id["ontario"]["compareLine"] = (
        f"鑽石吧 SFH 約 $123 萬、亞裔約 {s('diamond-bar')['asianAlonePct']}%；安大略 SFH 約 $72 萬、Hispanic {s('ontario')['hispanicPct']}%、亞裔 {s('ontario')['asianAlonePct']}% — 不是同一客群故事。"
    )


if __name__ == "__main__":
    main()

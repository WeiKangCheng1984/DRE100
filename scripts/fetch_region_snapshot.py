#!/usr/bin/env python3
"""Bake ACS 5-year snapshots into data/regions.json.

Requires env CENSUS_API_KEY (https://api.census.gov/data/key_signup.html).
Does not fetch Redfin. Does not invent numbers when a variable is missing.

Usage (from repo root):
  set CENSUS_API_KEY=...
  python scripts/fetch_region_snapshot.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGIONS = ROOT / "data" / "regions.json"
API_BASE = "https://api.census.gov/data"

# Prefer newest 5-year; ACS 5-year Data Profiles lag ~1 year after calendar year.
CANDIDATE_YEARS = (2024, 2023, 2022)

# Detailed tables: names are stabler than DP* across vintages.
VARS = {
    "population": "B01003_001E",
    "race_total": "B02001_001E",
    "asian_alone": "B02001_005E",
    "hisp_total": "B03003_001E",
    "hispanic": "B03003_003E",
    "median_income": "B19013_001E",
    "edu_total": "B15003_001E",
    "edu_bachelors": "B15003_022E",
    "edu_masters": "B15003_023E",
    "edu_prof": "B15003_024E",
    "edu_doctorate": "B15003_025E",
    "tenure_total": "B25003_001E",
    "tenure_owner": "B25003_002E",
    "ind_total": "C24050_001E",
    "ind_ag": "C24050_002E",
    "ind_const": "C24050_003E",
    "ind_mfg": "C24050_004E",
    "ind_wholesale": "C24050_005E",
    "ind_retail": "C24050_006E",
    "ind_trans": "C24050_007E",
    "ind_info": "C24050_008E",
    "ind_fin": "C24050_009E",
    "ind_prof": "C24050_010E",
    "ind_edu_health": "C24050_011E",
    "ind_arts": "C24050_012E",
    "ind_other": "C24050_013E",
    "ind_pub": "C24050_014E",
}

INDUSTRY_LABELS = [
    ("ind_edu_health", "教育醫療"),
    ("ind_prof", "專業科學管理"),
    ("ind_retail", "零售"),
    ("ind_arts", "餐旅娛樂"),
    ("ind_mfg", "製造"),
    ("ind_trans", "運輸倉儲公用"),
    ("ind_fin", "金融保險地產"),
    ("ind_info", "資訊"),
    ("ind_const", "營造"),
    ("ind_pub", "公共行政"),
    ("ind_wholesale", "批發"),
    ("ind_other", "其他服務"),
    ("ind_ag", "農林漁礦"),
]


def _get(url: str) -> list:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _census_url(year: int, get_vars: list[str], geo_for: str, key: str) -> str:
    params = {
        "get": ",".join(get_vars),
        "for": geo_for,
        "key": key,
    }
    if geo_for.startswith("place:"):
        params["in"] = "state:06"
    return f"{API_BASE}/{year}/acs/acs5?{urllib.parse.urlencode(params)}"


def _year_available(year: int, key: str) -> bool:
    url = _census_url(year, ["NAME", "B01003_001E"], "place:19192", key)
    try:
        rows = _get(url)
        return isinstance(rows, list) and len(rows) >= 2
    except Exception as exc:
        print(f"  {year} not usable: {exc}")
        return False


def _to_num(value) -> float | None:
    if value in (None, "", ".", "-666666666", "-888888888", "-999999999"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _pct(part, whole) -> float | None:
    p, w = _to_num(part), _to_num(whole)
    if p is None or w in (None, 0):
        return None
    return round(100.0 * p / w, 1)


def _delta_pct(curr, prior) -> float | None:
    c, p = _to_num(curr), _to_num(prior)
    if c is None or p in (None, 0):
        return None
    return round(100.0 * (c - p) / p, 1)


def _rows_to_map(rows: list, id_key: str) -> dict[str, dict]:
    header, *body = rows
    idx = {name: i for i, name in enumerate(header)}
    out = {}
    for row in body:
        geoid = row[idx[id_key]]
        out[geoid] = {name: row[i] for name, i in idx.items()}
    return out


def fetch_split(year: int, key: str, place_codes: list[str], zctas: list[str]) -> dict[str, dict]:
    var_names = ["NAME"] + list(VARS.values())
    merged: dict[str, dict] = {}
    if place_codes:
        codes = ",".join(sorted(set(place_codes)))
        url = _census_url(year, var_names, f"place:{codes}", key)
        print("GET", url.replace(key, "***"))
        merged.update(_rows_to_map(_get(url), "place"))
    if zctas:
        codes = ",".join(sorted(set(zctas)))
        url = _census_url(year, var_names, f"zip code tabulation area:{codes}", key)
        print("GET", url.replace(key, "***"))
        merged.update(_rows_to_map(_get(url), "zip code tabulation area"))
    return merged


def snapshot_from_row(row: dict, prior: dict | None, unit: str, price_sfh, price_as_of) -> dict:
    bachelors_plus = None
    edu_t = _to_num(row.get(VARS["edu_total"]))
    if edu_t:
        parts = [
            _to_num(row.get(VARS[k])) or 0
            for k in ("edu_bachelors", "edu_masters", "edu_prof", "edu_doctorate")
        ]
        bachelors_plus = round(100.0 * sum(parts) / edu_t, 1)

    industries = []
    ind_total = _to_num(row.get(VARS["ind_total"]))
    if ind_total:
        ranked = []
        for key, label in INDUSTRY_LABELS:
            n = _to_num(row.get(VARS[key]))
            if n is None:
                continue
            ranked.append({"key": key.replace("ind_", ""), "labelZh": label, "pct": round(100.0 * n / ind_total, 1)})
        industries = sorted(ranked, key=lambda x: x["pct"], reverse=True)[:3]

    pop = _to_num(row.get(VARS["population"]))
    income = _to_num(row.get(VARS["median_income"]))
    prior_pop = _to_num(prior.get(VARS["population"])) if prior else None
    prior_income = _to_num(prior.get(VARS["median_income"])) if prior else None

    return {
        "vintage": None,  # filled by caller
        "priorVintage": None,
        "population": int(pop) if pop is not None else None,
        "populationDeltaPct": _delta_pct(pop, prior_pop),
        "asianAlonePct": _pct(row.get(VARS["asian_alone"]), row.get(VARS["race_total"])),
        "hispanicPct": _pct(row.get(VARS["hispanic"]), row.get(VARS["hisp_total"])),
        "medianIncome": int(income) if income is not None else None,
        "medianIncomeDeltaPct": _delta_pct(income, prior_income),
        "bachelorsPlusPct": bachelors_plus,
        "ownerOccupiedPct": _pct(row.get(VARS["tenure_owner"]), row.get(VARS["tenure_total"])),
        "residentIndustry": industries,
        "priceSfh": price_sfh,
        "priceAsOf": price_as_of,
        "unit": unit,
    }


def main() -> int:
    key = os.environ.get("CENSUS_API_KEY", "").strip()
    if not key:
        print("Missing CENSUS_API_KEY. Get one at https://api.census.gov/data/key_signup.html")
        return 1

    data = json.loads(REGIONS.read_text(encoding="utf-8"))
    places, zctas = [], []
    for region in data["regions"]:
        geo = region.get("geo") or {}
        kind = geo.get("kind")
        geoid = str(geo.get("geoid") or "")
        if kind == "zcta":
            zctas.append(geoid)
        elif geoid.startswith("06") and len(geoid) == 7:
            places.append(geoid[2:])

    print("Detecting ACS 5-year vintage…")
    year = next((y for y in CANDIDATE_YEARS if _year_available(y, key)), None)
    if year is None:
        print("No ACS 5-year vintage responded.")
        return 1
    prior_year = year - 5
    print(f"Using ACS {year} 5-year; prior {prior_year} 5-year")

    current = fetch_split(year, key, places, zctas)
    prior = {}
    try:
        prior = fetch_split(prior_year, key, places, zctas)
    except Exception as exc:
        print(f"Prior vintage skipped: {exc}")

    vintage_label = f"ACS {year - 4}–{year}"
    prior_label = f"ACS {prior_year - 4}–{prior_year}" if prior else None

    updated = 0
    for region in data["regions"]:
        geo = region.get("geo") or {}
        kind = geo.get("kind")
        geoid = str(geo.get("geoid") or "")
        lookup = geoid[2:] if kind in ("city", "cdp") and geoid.startswith("06") else geoid
        row = current.get(lookup)
        if not row:
            print("  skip (no ACS row):", region["id"], lookup)
            continue
        snap = region.get("snapshot") or {}
        region["snapshot"] = snapshot_from_row(
            row,
            prior.get(lookup),
            snap.get("unit") or ("zcta" if kind == "zcta" else "place"),
            snap.get("priceSfh"),
            snap.get("priceAsOf"),
        )
        region["snapshot"]["vintage"] = vintage_label
        region["snapshot"]["priorVintage"] = prior_label if prior else None
        updated += 1
        print("  ok", region["id"], region["snapshot"]["population"], "Asian%", region["snapshot"]["asianAlonePct"])

    REGIONS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {updated} snapshots -> {REGIONS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

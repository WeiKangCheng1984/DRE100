#!/usr/bin/env python3
"""Download Census TIGER/Cartographic boundaries and bake a hand-drawn locator SVG.

Outputs:
  data/region-shapes.json
  assets/regions/la-locator.svg
"""
from __future__ import annotations

import json
import math
import ssl
import urllib.parse
import urllib.request
import zipfile
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGIONS = ROOT / "data" / "regions.json"
OUT_JSON = ROOT / "data" / "region-shapes.json"
OUT_SVG = ROOT / "assets" / "regions" / "la-locator.svg"

CTX = ssl.create_default_context()
UA = {"User-Agent": "DRE-100-field-ops-locator/1.0 (personal study site)"}

PLACE_SHP = "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_06_place_500k.zip"
ZCTA_SHP = "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_zcta520_500k.zip"

# TIGERweb fallbacks (smaller payloads than national ZCTA zip)
TIGER_PLACE = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Places_CouSub_ConCity_SubMCD/MapServer/{layer}/query"
TIGER_ZCTA = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/PUMA_TAD_TAZ_UGA_ZCTA/MapServer/1/query"
LA_CITY_GEOID = "0644000"

W = 1200.0
H = 640.0
PAD = 28.0
# Greater LA: Santa Monica Bay → Ontario, South Pas / Arcadia → Chino Hills
BOUNDS = dict(west=-118.55, east=-117.50, south=33.86, north=34.22)
INSET = dict(west=-118.48, east=-118.34, south=33.94, north=34.04)
INSET_BOX = dict(x=36, y=318, w=310, h=250)

CLUSTER_FILL = {
    "westside-lax": "#3D7A7A",
    "core-sgv-north": "#6B3A3A",
    "east-sgv-60": "#C4A06A",
    "west-ie": "#4A6280",
}


def fetch(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as resp:
        return resp.read()


def fetch_json(url: str):
    return json.loads(fetch(url).decode("utf-8"))


def douglas_peucker(points, epsilon):
    if len(points) < 3:
        return points

    def perp(p, a, b):
        if a == b:
            return math.hypot(p[0] - a[0], p[1] - a[1])
        t = ((p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])) / (
            (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2
        )
        t = max(0.0, min(1.0, t))
        x = a[0] + t * (b[0] - a[0])
        y = a[1] + t * (b[1] - a[1])
        return math.hypot(p[0] - x, p[1] - y)

    max_d, idx = 0.0, 0
    for i in range(1, len(points) - 1):
        d = perp(points[i], points[0], points[-1])
        if d > max_d:
            max_d, idx = d, i
    if max_d > epsilon:
        left = douglas_peucker(points[: idx + 1], epsilon)
        right = douglas_peucker(points[idx:], epsilon)
        return left[:-1] + right
    return [points[0], points[-1]]


def simplify_ring(ring, epsilon):
    if len(ring) < 5:
        return ring
    closed = ring[0] == ring[-1]
    pts = ring[:-1] if closed else list(ring)
    out = douglas_peucker(pts, epsilon)
    if len(out) < 4:
        return ring
    if closed:
        out.append(out[0])
    return out


def geom_rings(geom):
    gtype = geom.get("type")
    coords = geom.get("coordinates") or []
    rings = []
    if gtype == "Polygon":
        rings.extend(coords)
    elif gtype == "MultiPolygon":
        for poly in coords:
            rings.extend(poly)
    return rings


def simplify_geom(geom, epsilon):
    rings = [simplify_ring(r, epsilon) for r in geom_rings(geom)]
    rings = [r for r in rings if len(r) >= 4]
    if not rings:
        return None
    if geom.get("type") == "MultiPolygon" or len(rings) > 1:
        # keep as MultiPolygon of single-ring polygons (ignore holes for locator)
        return {"type": "MultiPolygon", "coordinates": [[r] for r in rings]}
    return {"type": "Polygon", "coordinates": [rings[0]]}


def centroid(geom):
    rings = geom_rings(geom)
    if not rings:
        return 0, 0
    outer = rings[0]
    n = max(len(outer) - 1, 1)
    xs = [p[0] for p in outer[:-1]]
    ys = [p[1] for p in outer[:-1]]
    return sum(xs) / n, sum(ys) / n


def project(lon, lat, bounds=BOUNDS, x0=PAD, y0=PAD, w=W - 2 * PAD, h=H - 2 * PAD):
    x = x0 + (lon - bounds["west"]) / (bounds["east"] - bounds["west"]) * w
    y = y0 + (bounds["north"] - lat) / (bounds["north"] - bounds["south"]) * h
    return x, y


def path_d(geom, bounds=None, box=None):
    if bounds is None:
        bounds = BOUNDS
    if box is None:
        box = dict(x=PAD, y=PAD, w=W - 2 * PAD, h=H - 2 * PAD)
    parts = []
    for ring in geom_rings(geom):
        cmds = []
        for i, (lon, lat) in enumerate(ring):
            x, y = project(lon, lat, bounds, box["x"], box["y"], box["w"], box["h"])
            cmds.append(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}")
        parts.append(" ".join(cmds) + " Z")
    return " ".join(parts)


def query_tiger_place(geoid: str):
    state, place = geoid[:2], geoid[2:]
    for layer in (4, 5, 2, 3):
        params = {
            "where": f"STATE='{state}' AND PLACE='{place}'",
            "outFields": "GEOID,NAME",
            "returnGeometry": "true",
            "outSR": "4326",
            "maxAllowableOffset": "0.0015",
            "geometryPrecision": "5",
            "f": "geojson",
        }
        url = TIGER_PLACE.format(layer=layer) + "?" + urllib.parse.urlencode(params)
        try:
            data = fetch_json(url)
        except Exception:
            continue
        feats = data.get("features") or []
        if feats:
            return feats[0]["geometry"]
    # GEOID only
    for layer in (4, 5):
        params = {
            "where": f"GEOID='{geoid}'",
            "outFields": "GEOID,NAME",
            "returnGeometry": "true",
            "outSR": "4326",
            "maxAllowableOffset": "0.0015",
            "geometryPrecision": "5",
            "f": "geojson",
        }
        url = TIGER_PLACE.format(layer=layer) + "?" + urllib.parse.urlencode(params)
        try:
            data = fetch_json(url)
        except Exception:
            continue
        feats = data.get("features") or []
        if feats:
            return feats[0]["geometry"]
    return None


def query_tiger_zcta(zcta: str):
    wheres = [
        f"ZCTA5='{zcta}'",
        f"GEOID='{zcta}'",
        f"ZCTA5CE20='{zcta}'",
    ]
    for where in wheres:
        params = {
            "where": where,
            "outFields": "*",
            "returnGeometry": "true",
            "outSR": "4326",
            "maxAllowableOffset": "0.001",
            "geometryPrecision": "5",
            "f": "geojson",
        }
        url = TIGER_ZCTA + "?" + urllib.parse.urlencode(params)
        try:
            data = fetch_json(url)
            feats = data.get("features") or []
            if feats:
                return feats[0]["geometry"]
        except Exception:
            continue
    return None


def try_shp_places(needed: set[str]):
    """Optional: parse cb_2024_06_place_500k if pyshp is available."""
    try:
        import shapefile  # type: ignore
    except ImportError:
        return {}
    print("Downloading CA place 500k…")
    raw = fetch(PLACE_SHP, timeout=180)
    zf = zipfile.ZipFile(BytesIO(raw))
    tmp = ROOT / "scripts" / "_tmp_place"
    tmp.mkdir(exist_ok=True)
    zf.extractall(tmp)
    shp = next(tmp.glob("*.shp"))
    sf = shapefile.Reader(str(shp))
    names = [f[0] for f in sf.fields[1:]]
    out = {}
    for rec, shape in zip(sf.iterRecords(), sf.iterShapes()):
        row = dict(zip(names, rec))
        geoid = str(row.get("GEOID") or row.get("GEOID20") or "")
        if geoid not in needed:
            continue
        parts = []
        if shape.shapeType in (5, 15, 25):  # polygon
            pts = shape.points
            for i, part in enumerate(shape.parts):
                end = shape.parts[i + 1] if i + 1 < len(shape.parts) else len(pts)
                ring = [[p[0], p[1]] for p in pts[part:end]]
                if ring and ring[0] != ring[-1]:
                    ring.append(ring[0])
                parts.append(ring)
        if not parts:
            continue
        geom = {"type": "MultiPolygon", "coordinates": [[r] for r in parts]} if len(parts) > 1 else {
            "type": "Polygon",
            "coordinates": [parts[0]],
        }
        out[geoid] = geom
    return out


def collect_geoms(payload):
    needed_places = set()
    zctas = []
    for r in payload["regions"]:
        geo = r.get("geo") or {}
        if geo.get("kind") == "zcta":
            zctas.append(str(geo["geoid"]))
        else:
            needed_places.add(str(geo["geoid"]))
    needed_places.add(LA_CITY_GEOID)

    geoms = {}
    shp = try_shp_places(needed_places)
    geoms.update(shp)

    for geoid in sorted(needed_places):
        if geoid in geoms:
            print("  place from shapefile", geoid)
            continue
        print("  TIGERweb place", geoid)
        g = query_tiger_place(geoid)
        if g:
            geoms[geoid] = g
        else:
            print("  MISSING place", geoid)

    for z in zctas:
        print("  TIGERweb ZCTA", z)
        g = query_tiger_zcta(z)
        if g:
            geoms[z] = g
        else:
            print("  MISSING zcta", z)
    return geoms


def bay_path():
    # Schematic Santa Monica Bay coastline (lon/lat), west of Westchester
    pts = [
        (-118.55, 34.06),
        (-118.52, 34.02),
        (-118.50, 33.98),
        (-118.47, 33.94),
        (-118.44, 33.90),
        (-118.42, 33.86),
        (-118.55, 33.86),
        (-118.55, 34.06),
    ]
    cmds = []
    for i, (lon, lat) in enumerate(pts):
        x, y = project(lon, lat)
        cmds.append(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}")
    return " ".join(cmds) + " Z"


def freeway_polylines():
    # Schematic corridors, geographically placed (not full TIGER roads).
    return [
        ("405", [(-118.45, 34.08), (-118.42, 34.02), (-118.40, 33.96), (-118.38, 33.90)]),
        ("10", [(-118.40, 34.045), (-118.22, 34.055), (-118.08, 34.06), (-117.90, 34.06), (-117.65, 34.065), (-117.52, 34.07)]),
        ("110", [(-118.21, 34.16), (-118.19, 34.12), (-118.17, 34.06)]),
        ("210", [(-118.18, 34.15), (-118.08, 34.14), (-118.00, 34.135), (-117.90, 34.13)]),
        ("605", [(-118.02, 34.16), (-118.01, 34.08), (-118.00, 34.00), (-117.99, 33.94)]),
        ("60", [(-118.08, 34.04), (-117.97, 34.00), (-117.85, 33.995), (-117.72, 34.00), (-117.58, 34.02)]),
        ("57", [(-117.86, 34.08), (-117.82, 34.02), (-117.80, 33.94)]),
        ("71", [(-117.72, 34.04), (-117.73, 33.96), (-117.74, 33.90)]),
    ]


def svg_label(text, x, y, fill="#1c1917", size=11, anchor="middle"):
    esc = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="Fraunces, Noto Sans TC, serif" font-size="{size}" fill="{fill}">{esc}</text>'
    )


def build_svg(payload, geoms):
    cluster_of = {r["id"]: r.get("clusterId") for r in payload["regions"]}
    color_of = {c["id"]: c.get("color") or CLUSTER_FILL.get(c["id"], "#888") for c in payload["clusters"]}
    id_by_geoid = {}
    for r in payload["regions"]:
        geo = r.get("geo") or {}
        id_by_geoid[str(geo.get("geoid"))] = r

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {int(W)} {int(H)}" role="img" aria-label="Greater Los Angeles region locator">',
        "<defs>",
        '<filter id="paper" x="-5%" y="-5%" width="110%" height="110%">',
        '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" result="n"/>',
        '<feDiffuseLighting in="n" lighting-color="#f7f3ec" surfaceScale="0.6">',
        '<feDistantLight azimuth="40" elevation="55"/>',
        "</feDiffuseLighting>",
        "</filter>",
        f'<clipPath id="mapClip"><rect x="{PAD}" y="{PAD}" width="{W-2*PAD}" height="{H-2*PAD-36}" rx="8"/></clipPath>',
        "</defs>",
        '<rect width="100%" height="100%" fill="#f3efe8"/>',
        '<rect width="100%" height="100%" filter="url(#paper)" opacity="0.18"/>',
        '<g clip-path="url(#mapClip)">',
        f'<path d="{bay_path()}" fill="#d5e1e6" stroke="none" opacity="0.85"/>',
        svg_label("Santa Monica Bay", 70, 430, "#6f8f9e", 10, "start"),
    ]

    # Faint LA city
    la = geoms.get(LA_CITY_GEOID)
    if la:
        la_s = simplify_geom(la, 0.008) or la
        parts.append(
            f'<path d="{path_d(la_s)}" fill="#1c1917" fill-opacity="0.045" stroke="#1c1917" '
            f'stroke-opacity="0.18" stroke-width="0.8" stroke-dasharray="3 4"/>'
        )
        parts.append(svg_label("Los Angeles city（淡影，非本卡數字）", 210, 175, "#8a8078", 10, "start"))

    for code, line in freeway_polylines():
        cmds = []
        for i, (lon, lat) in enumerate(line):
            x, y = project(lon, lat)
            cmds.append(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}")
        mx, my = project(*line[len(line) // 2])
        parts.append(
            f'<path d="{" ".join(cmds)}" fill="none" stroke="#1c1917" stroke-opacity="0.28" '
            f'stroke-width="1.2" stroke-linecap="round" stroke-dasharray="5 4"/>'
        )
        parts.append(svg_label(code, mx + 6, my - 6, "#4a453f", 9, "start"))

    # Region polygons (main map)
    for r in payload["regions"]:
        geo = r.get("geo") or {}
        geoid = str(geo.get("geoid"))
        geom = geoms.get(geoid)
        if not geom:
            continue
        simple = simplify_geom(geom, 0.0025) or geom
        fill = color_of.get(r.get("clusterId"), "#888")
        parts.append(
            f'<path id="{r["id"]}" class="region-shape" data-id="{r["id"]}" data-cluster="{r.get("clusterId")}" '
            f'd="{path_d(simple)}" fill="{fill}" fill-opacity="0.55" stroke="#1c1917" stroke-width="1.15" '
            f'stroke-linejoin="round"/>'
        )

    # Labels on main map (skip tiny westside — those live in inset)
    for r in payload["regions"]:
        if r.get("clusterId") == "westside-lax":
            continue
        geo = r.get("geo") or {}
        geom = geoms.get(str(geo.get("geoid")))
        lon, lat = (geo.get("lng"), geo.get("lat"))
        if geom:
            lon, lat = centroid(geom)
        if lon is None:
            continue
        x, y = project(lon, lat)
        parts.append(svg_label(r["nameZh"], x, y + 4, "#1c1917", 11))
    parts.append("</g>")

    # Westside inset
    ib = INSET_BOX
    parts.append(
        f'<rect x="{ib["x"]}" y="{ib["y"]}" width="{ib["w"]}" height="{ib["h"]}" rx="14" '
        f'fill="#f7f3ec" fill-opacity="0.94" stroke="#1c1917" stroke-opacity="0.35" stroke-width="1.2"/>'
    )
    parts.append(svg_label("西區小圖 · LAX 帶", ib["x"] + 14, ib["y"] + 22, "#3D7A7A", 12, "start"))
    west_ids = [r for r in payload["regions"] if r.get("clusterId") == "westside-lax"]
    for r in west_ids:
        geom = geoms.get(str((r.get("geo") or {}).get("geoid")))
        if not geom:
            continue
        simple = simplify_geom(geom, 0.0012) or geom
        fill = color_of.get("westside-lax", "#3D7A7A")
        parts.append(
            f'<path id="{r["id"]}-inset" class="region-shape" data-id="{r["id"]}" data-cluster="westside-lax" '
            f'd="{path_d(simple, INSET, dict(x=ib["x"]+12, y=ib["y"]+32, w=ib["w"]-24, h=ib["h"]-48))}" '
            f'fill="{fill}" fill-opacity="0.62" stroke="#1c1917" stroke-width="1.1" stroke-linejoin="round"/>'
        )
        lon, lat = centroid(simple)
        x, y = project(lon, lat, INSET, ib["x"] + 12, ib["y"] + 32, ib["w"] - 24, ib["h"] - 48)
        parts.append(svg_label(r["nameZh"], x, y + 3, "#1c1917", 10))

    parts.append(
        '<text x="28" y="622" font-family="Outfit, Noto Sans TC, sans-serif" font-size="10" fill="#6b645c">'
        "Boundaries: U.S. Census Bureau Cartographic / TIGER. Freeways schematic. ZCTA 90045/90094 ≠ city limits."
        "</text>"
    )
    parts.append("</svg>")
    return "\n".join(parts), cluster_of


def main():
    payload = json.loads(REGIONS.read_text(encoding="utf-8"))
    geoms = collect_geoms(payload)

    shapes = {
        "attribution": "U.S. Census Bureau TIGER/Cartographic Boundary (place + ZCTA). LA city outline is context only.",
        "bounds": BOUNDS,
        "insetBounds": INSET,
        "laCityGeoid": LA_CITY_GEOID,
        "features": [],
    }
    for r in payload["regions"]:
        geo = r.get("geo") or {}
        geoid = str(geo.get("geoid"))
        geom = geoms.get(geoid)
        if not geom:
            continue
        simple = simplify_geom(geom, 0.002) or geom
        lon, lat = centroid(simple)
        shapes["features"].append(
            {
                "id": r["id"],
                "geoid": geoid,
                "kind": geo.get("kind"),
                "clusterId": r.get("clusterId"),
                "nameZh": r.get("nameZh"),
                "centroid": [round(lon, 5), round(lat, 5)],
                "geometry": simple,
            }
        )
    la = geoms.get(LA_CITY_GEOID)
    if la:
        shapes["laCity"] = simplify_geom(la, 0.01)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(shapes, ensure_ascii=False), encoding="utf-8")
    OUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    svg, _ = build_svg(payload, geoms)
    OUT_SVG.write_text(svg, encoding="utf-8")
    print("wrote", OUT_JSON, "features", len(shapes["features"]))
    print("wrote", OUT_SVG, "bytes", OUT_SVG.stat().st_size)
    missing = [
        r["id"]
        for r in payload["regions"]
        if str((r.get("geo") or {}).get("geoid")) not in geoms
    ]
    if missing:
        print("MISSING", missing)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

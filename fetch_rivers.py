"""
fetch_rivers.py — FloodWatch river geometry (two LOD files)
-----------------------------------------------------------
Generates two files:
  rivers-overview.geojson  ~2MB  zoom 4-8   major rivers, simplified
  rivers-detail.geojson    ~8MB  zoom 9+    all named rivers, full detail

Run once:
    pip install requests
    python fetch_rivers.py
"""

import json, time, math, requests, os

ENDPOINT = (
    "https://hosting.wsapi.cloud.bom.gov.au/arcgis/rest/services/"
    "ahgf/Geofabric_V3x_All_Products/FeatureServer/5/query"
)

CONFIGS = [
    {
        "file":        "rivers-overview.geojson",
        "label":       "Overview (zoom 4-8)",
        "where":       "Hierarchy='Major' AND upstrdarea >= 5000000000",  # 5000 km2
        "epsilon":     0.008,   # ~800m simplification
        "round":       3,       # ~100m coordinate precision
    },
    {
        "file":        "rivers-detail.geojson",
        "label":       "Detail (zoom 9+)",
        "where":       "Hierarchy='Major' AND upstrdarea >= 500000000",   # 500 km2
        "epsilon":     0.001,   # ~100m simplification — preserves meanders
        "round":       4,       # ~11m coordinate precision
    },
]

BASE_PARAMS = {
    "outFields":      "name,flowdir,upstrdarea",
    "returnGeometry": "true",
    "inSR":           "4326",
    "outSR":          "4326",
    "f":              "geoJSON",
    "resultRecordCount": "2000",
    "orderByFields":  "objectid",
}

def douglas_peucker(coords, epsilon):
    if len(coords) <= 2:
        return coords
    start, end = coords[0], coords[-1]
    dx, dy = end[0]-start[0], end[1]-start[1]
    length = math.sqrt(dx*dx + dy*dy)
    max_dist, max_idx = 0, 0
    for i in range(1, len(coords)-1):
        if length == 0:
            dist = math.sqrt((coords[i][0]-start[0])**2+(coords[i][1]-start[1])**2)
        else:
            dist = abs(dy*coords[i][0]-dx*coords[i][1]+end[0]*start[1]-end[1]*start[0])/length
        if dist > max_dist:
            max_dist, max_idx = dist, i
    if max_dist > epsilon:
        return douglas_peucker(coords[:max_idx+1],epsilon)[:-1]+douglas_peucker(coords[max_idx:],epsilon)
    return [start, end]

def fetch_all(where):
    features, offset, page = [], 0, 1
    while True:
        params = {**BASE_PARAMS, "where": where, "resultOffset": offset}
        print(f"    Page {page}...", end=" ", flush=True)
        resp = requests.get(ENDPOINT, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("features", [])
        features.extend(batch)
        print(f"{len(batch)} (total: {len(features)})")
        if not data.get("exceededTransferLimit", False) or len(batch) == 0:
            break
        offset += len(batch)
        page += 1
        time.sleep(0.3)
    return features

def process(features, epsilon, round_dp):
    out = []
    for f in features:
        props = f.get("properties", {})
        geom  = f.get("geometry")
        if not geom: continue
        name    = props.get("name") or ""
        flowdir = props.get("flowdir", 1)
        area    = props.get("upstrdarea", 0) or 0
        # Scale epsilon by river size — big rivers get finer detail
        if area > 1e11:   eps = epsilon * 0.3
        elif area > 1e10: eps = epsilon * 0.6
        else:             eps = epsilon
        lines = ([geom["coordinates"]] if geom["type"]=="LineString"
                 else geom.get("coordinates",[]))
        simplified = []
        for coords in lines:
            s = douglas_peucker(coords, eps)
            s = [[round(c[0],round_dp), round(c[1],round_dp)] for c in s]
            if len(s) >= 2:
                simplified.append(s)
        if not simplified: continue
        new_geom = ({"type":"LineString","coordinates":simplified[0]}
                    if len(simplified)==1
                    else {"type":"MultiLineString","coordinates":simplified})
        out.append({
            "type": "Feature",
            "properties": {"name":name,"flowdir":flowdir,"area":round(area/1e6)},
            "geometry": new_geom
        })
    return out

for cfg in CONFIGS:
    print(f"\n── {cfg['label']} ──")
    print(f"   Filter: {cfg['where']}")
    features = fetch_all(cfg["where"])
    print(f"   Processing {len(features)} features...")
    processed = process(features, cfg["epsilon"], cfg["round"])
    geojson = {"type":"FeatureCollection","features":processed}
    with open(cfg["file"],"w") as f:
        json.dump(geojson, f, separators=(",",":"))
    mb = os.path.getsize(cfg["file"])/1024/1024
    status = "✓" if mb < 10 else ("⚠" if mb < 25 else "✗ too large")
    print(f"   {status} Saved {cfg['file']} — {len(processed)} features, {mb:.1f} MB")

print("\n── Done ──")
print("git add rivers-overview.geojson rivers-detail.geojson index.html fetch_rivers.py")
print("git commit -m 'Add Geofabric LOD river geometry'")
print("git push")

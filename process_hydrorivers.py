"""
process_hydrorivers.py — FloodWatch global river geometry
----------------------------------------------------------
Processes the HydroRIVERS v10 global shapefile into three
LOD GeoJSON files for use in FloodWatch.

Requirements:
    pip install geopandas shapely

Usage:
    python process_hydrorivers.py --input HydroRIVERS_v10_shp/HydroRIVERS_v10.shp

Output files (commit all three to repo, delete old BOM files):
    rivers-global.geojson    ~3MB   zoom 2-5   stream order 1-3
    rivers-regional.geojson  ~15MB  zoom 6-8   stream order 1-5
    rivers-local.geojson     ~40MB  zoom 9+    stream order 1-7

HydroRIVERS key fields:
    ORD_FLOW   Stream order 1-10 (1=largest rivers, 10=small creeks)
    LENGTH_KM  Segment length in km
    UPLAND_SKM Upstream drainage area in km²
    MAIN_RIV   Main river ID (links segments of same river)
    HYRIV_ID   Unique segment ID

License: CC BY 4.0 — attribution required
    © WWF / HydroSHEDS — www.hydrosheds.org
"""

import argparse
import json
import math
import os
import sys
import time

try:
    import geopandas as gpd
    from shapely.geometry import mapping
except ImportError:
    print("ERROR: Missing dependencies. Run: pip install geopandas shapely")
    sys.exit(1)


# ── LOD configuration ─────────────────────────────────────────────────────────

LODS = [
    {
        "file":       "rivers-global.geojson",
        "label":      "Global (zoom 2-5)",
        "max_order":  3,       # Only major rivers — Amazon, Nile, Murray scale
        "epsilon":    0.05,    # ~5km simplification — fine at global zoom
        "round":      2,       # ~1km coordinate precision
    },
    {
        "file":       "rivers-regional.geojson",
        "label":      "Regional (zoom 6-8)",
        "max_order":  5,       # Medium rivers visible at state/country zoom
        "epsilon":    0.008,   # ~800m simplification
        "round":      3,       # ~100m coordinate precision
    },
    {
        "file":       "rivers-local.geojson",
        "label":      "Local (zoom 9+)",
        "max_order":  7,       # Most named rivers, exclude tiny creeks
        "epsilon":    0.001,   # ~100m simplification — preserves meanders
        "round":      4,       # ~11m coordinate precision
    },
]


# ── Douglas-Peucker simplification ────────────────────────────────────────────

def douglas_peucker(coords, epsilon):
    if len(coords) <= 2:
        return coords
    start, end = coords[0], coords[-1]
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.sqrt(dx * dx + dy * dy)
    max_dist, max_idx = 0, 0
    for i in range(1, len(coords) - 1):
        if length == 0:
            dist = math.sqrt((coords[i][0] - start[0])**2 + (coords[i][1] - start[1])**2)
        else:
            dist = abs(dy * coords[i][0] - dx * coords[i][1] + end[0] * start[1] - end[1] * start[0]) / length
        if dist > max_dist:
            max_dist, max_idx = dist, i
    if max_dist > epsilon:
        left  = douglas_peucker(coords[:max_idx + 1], epsilon)
        right = douglas_peucker(coords[max_idx:],     epsilon)
        return left[:-1] + right
    return [start, end]


def simplify_and_round(coords, epsilon, decimals):
    simplified = douglas_peucker(list(coords), epsilon)
    return [[round(c[0], decimals), round(c[1], decimals)] for c in simplified]


# ── Main processing ───────────────────────────────────────────────────────────

def process_lod(gdf, lod):
    filtered = gdf[gdf['ORD_FLOW'] <= lod['max_order']].copy()
    print(f"  Filtered to order ≤ {lod['max_order']}: {len(filtered):,} segments")

    features = []
    skipped  = 0

    for _, row in filtered.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            skipped += 1
            continue

        order  = int(row['ORD_FLOW'])
        area   = float(row['UPLAND_SKM']) if row['UPLAND_SKM'] else 0
        length = float(row['LENGTH_KM'])  if row['LENGTH_KM']  else 0

        # Scale epsilon by stream order — larger rivers get finer detail
        if order == 1:   eps = lod['epsilon'] * 0.2
        elif order == 2: eps = lod['epsilon'] * 0.4
        elif order == 3: eps = lod['epsilon'] * 0.6
        else:            eps = lod['epsilon']

        # Width: 0.5px (small) to 3px (major) based on stream order
        width = round(max(0.5, 3.5 - (order * 0.4)), 1)

        # Extract coordinates from LineString or MultiLineString
        raw_geom  = mapping(geom)
        geom_type = raw_geom['type']

        if geom_type == 'LineString':
            lines = [list(raw_geom['coordinates'])]
        elif geom_type == 'MultiLineString':
            lines = [list(c) for c in raw_geom['coordinates']]
        else:
            skipped += 1
            continue

        simplified_lines = []
        for coords in lines:
            s = simplify_and_round(coords, eps, lod['round'])
            if len(s) >= 2:
                simplified_lines.append(s)

        if not simplified_lines:
            skipped += 1
            continue

        if len(simplified_lines) == 1:
            new_geom = {"type": "LineString", "coordinates": simplified_lines[0]}
        else:
            new_geom = {"type": "MultiLineString", "coordinates": simplified_lines}

        features.append({
            "type": "Feature",
            "properties": {
                "order":  order,
                "area":   round(area),
                "width":  width,
                "length": round(length, 1),
            },
            "geometry": new_geom
        })

    print(f"  Features: {len(features):,} kept, {skipped} skipped")
    return features


def main():
    parser = argparse.ArgumentParser(description='Process HydroRIVERS shapefile into FloodWatch LOD GeoJSON files')
    parser.add_argument('--input', required=True, help='Path to HydroRIVERS_v10.shp')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: File not found: {args.input}")
        sys.exit(1)

    print(f"Loading {args.input} ...")
    t0 = time.time()
    gdf = gpd.read_file(args.input)
    print(f"Loaded {len(gdf):,} segments in {time.time()-t0:.1f}s")
    print(f"Columns: {list(gdf.columns)}")
    print(f"CRS: {gdf.crs}")
    print()

    # Reproject to WGS84 if needed
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        print("Reprojecting to WGS84 (EPSG:4326)...")
        gdf = gdf.to_crs(epsg=4326)

    for lod in LODS:
        print(f"── {lod['label']} → {lod['file']}")
        t1 = time.time()
        features = process_lod(gdf, lod)

        geojson = {"type": "FeatureCollection", "features": features}
        with open(lod['file'], 'w') as f:
            json.dump(geojson, f, separators=(',', ':'))

        mb     = os.path.getsize(lod['file']) / 1024 / 1024
        status = "✓" if mb < 10 else ("⚠" if mb < 50 else "✗ too large")
        print(f"  {status} Saved {lod['file']} — {len(features):,} features, {mb:.1f} MB ({time.time()-t1:.1f}s)")
        print()

    print("── Complete ──")
    print("Next steps:")
    print("  1. Delete old BOM files:")
    print("       del rivers-overview.geojson")
    print("       del rivers-detail.geojson")
    print("  2. Commit new files:")
    print("       git add rivers-global.geojson rivers-regional.geojson rivers-local.geojson")
    print("       git add index.html process_hydrorivers.py PROJECT.md")
    print("       git commit -m 'Switch to HydroRIVERS global river data'")
    print("       git push")
    print()
    print("Attribution required in app:")
    print("  © WWF / HydroSHEDS (hydrosheds.org) — CC BY 4.0")


if __name__ == '__main__':
    main()

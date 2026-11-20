"""Cut the gridfinder network into self-hosted GeoJSON tiles.

Why: the page used to ask the World Bank ArcGIS service for lines, which caps
every response at 2000 features. The full dataset is already on disk, so the
lines are cut here instead and served as static files from our own site.

Input : data/raw/grid.gpkg (3,678,243 LineStrings, EPSG:4326)
Output: data/tiles/{z}/{x}/{y}.json   z4 coarse, z5 detail

Each feature is placed in every tile its bounding box touches, then clipped to
the tile rectangle with a small overlap so neighbours join without seams.
"""
import json, math, os, sys, time
import numpy as np
import pyogrio
import shapely
import shapely.ops as ops

HERE = os.path.dirname(os.path.abspath(__file__))
GPKG = os.path.join(HERE, "data/raw/grid.gpkg")
OUT = os.path.join(HERE, "data/tiles")

LEVELS = {4: (0.08, 0.15, 3), 5: (0.02, 0.05, 4)}   # zoom -> (simplify, min part length, decimals)

def tile_of(lon, lat, z):
    n = 2 ** z
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.log(math.tan(math.radians(lat)) + 1/math.cos(math.radians(lat))) / math.pi) / 2.0 * n)
    return max(0, min(n-1, x)), max(0, min(n-1, y))

def tile_bounds(x, y, z):
    n = 2 ** z
    lon1 = x / n * 360.0 - 180.0
    lon2 = (x + 1) / n * 360.0 - 180.0
    lat1 = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    lat2 = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
    return lon1, lat2, lon2, lat1   # ymin, ymax for clip_by_rect

print("reading", GPKG, flush=True)
t0 = time.time()
gdf = pyogrio.read_dataframe(GPKG, columns=[])
geoms = np.array(gdf.geometry.values, dtype=object)
print("features", len(geoms), "%.1fs" % (time.time() - t0), flush=True)

b = shapely.bounds(geoms)   # minx, miny, maxx, maxy
print("bounds done %.1fs" % (time.time() - t0), flush=True)

buckets = {}
for z in LEVELS:
    buckets[z] = {}

for z in LEVELS:
    n = 2 ** z
    # corner tiles of each feature bbox
    xs0 = np.clip(((b[:, 0] + 180.0) / 360.0 * n).astype(int), 0, n - 1)
    xs1 = np.clip(((b[:, 2] + 180.0) / 360.0 * n).astype(int), 0, n - 1)
    ys0 = np.clip((np.log(np.tan(np.pi/4 + np.radians(b[:, 3])/2)) / np.pi * -1 + 1) / 2 * n, 0, n - 1).astype(int)
    ys1 = np.clip((np.log(np.tan(np.pi/4 + np.radians(b[:, 1])/2)) / np.pi * -1 + 1) / 2 * n, 0, n - 1).astype(int)
    for i in range(len(geoms)):
        for tx in range(xs0[i], xs1[i] + 1):
            for ty in range(ys0[i], ys1[i] + 1):
                buckets[z].setdefault((tx, ty), []).append(geoms[i])
    print("z%d tiles touched %d %.1fs" % (z, len(buckets[z]), time.time() - t0), flush=True)

for z, (tol, minlen, dec) in LEVELS.items():
    d = os.path.join(OUT, str(z))
    os.makedirs(d, exist_ok=True)
    total = 0
    for (tx, ty), gs in buckets[z].items():
        lon1, lat1, lon2, lat2 = tile_bounds(tx, ty, z)
        pad_lon = (lon2 - lon1) * 0.02
        pad_lat = (lat2 - lat1) * 0.02
        try:
            clipped = shapely.clip_by_rect(shapely.union_all(gs),
                                           lon1 - pad_lon, lat1 - pad_lat,
                                           lon2 + pad_lon, lat2 + pad_lat)
        except Exception as e:
            print('tile failed', z, tx, ty, repr(e)[:80], flush=True)
            continue
        if clipped.is_empty:
            continue
        try:
            merged = ops.linemerge(clipped)
        except Exception:
            merged = clipped
        simp = merged.simplify(tol, preserve_topology=False)
        parts = list(getattr(simp, "geoms", [simp]))
        coords = []
        for p in parts:
            if p.length < minlen:
                continue
            c = np.round(np.asarray(p.coords), dec)
            if len(c) >= 2:
                coords.append(c.tolist())
        if not coords:
            continue
        p = os.path.join(d, f"{tx}_{ty}.json")
        txt = json.dumps({"type": "MultiLineString", "coordinates": coords}, separators=(",", ":"))
        open(p, "w").write(txt)
        total += len(txt)
    print("z%d wrote %d files %.1f MB" % (z, len(buckets[z]), total / 1e6), flush=True)

print("done %.1fs" % (time.time() - t0))

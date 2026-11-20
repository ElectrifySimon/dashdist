"""Per-country network metrics from the ESMAP gridfinder line layer.

Inputs : data/raw/grid.gpkg (lines, EPSG:4326), data/countries.geo.json
Output : data/network.json  {iso: {km, km_per_1000km2, km_per_1000_people, ...}}

Length is measured in an equal-area projection so km are real. Country area
comes from the same polygons, so density is internally consistent.
"""
import json, os
import geopandas as gpd
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
GPKG = os.path.join(HERE, "data/raw/grid.gpkg")
CTRY = os.path.join(HERE, "data/countries.geo.json")
OUT = os.path.join(HERE, "data/network.json")

# Equal-area projection (EPSG:6933) for length and area measurement.
EA = "EPSG:6933"

print("reading countries")
countries = gpd.read_file(CTRY)
countries = countries.rename(columns={c: c.lower() for c in countries.columns})
iso_col = "iso" if "iso" in countries.columns else None
if iso_col is None:
    raise SystemExit("no iso column in countries.geo.json")
countries = countries[["iso", "geometry"]].to_crs(EA)
countries["area_km2"] = countries.geometry.area / 1e6
print("countries", len(countries))

print("reading grid lines, this takes a minute")
lines = gpd.read_file(GPKG, layer=0)
print("lines", len(lines), "crs", lines.crs)
lines = lines.to_crs(EA)
lines["len_km"] = lines.geometry.length / 1000

print("spatial join")
joined = gpd.sjoin(lines[["len_km", "geometry"]], countries[["iso", "geometry"]],
                   how="inner", predicate="intersects")
by_iso = joined.groupby("iso")["len_km"].sum()

pop = {}
try:
    src = json.load(open(os.path.join(HERE, "src/data.json")))
    for r in src["rows"]:
        pop[r["iso"]] = r.get("pop_m")
except Exception as e:
    print("population merge skipped:", e)

out = {}
for _, row in countries.iterrows():
    iso = row["iso"]; km = float(by_iso.get(iso, 0.0))
    if km <= 0:
        continue
    pop_m = pop.get(iso)
    out[iso] = {
        "km": round(km, 1),
        "km_per_1000km2": round(km / max(row["area_km2"], 1) * 1000, 2),
        "km_per_1000_people": round(km / pop_m, 2) if pop_m else None,
        "area_km2": round(float(row["area_km2"]), 0),
    }

json.dump({"meta": {"source": "ESMAP gridfinder grid.gpkg, predicted network",
                    "licence": "CC BY 4.0", "measured_in": EA,
                    "countries": len(out)},
           "rows": out}, open(OUT, "w"), indent=1)
print("wrote", OUT, len(out), "countries")
print(sorted(out.items(), key=lambda kv: -kv[1]["km"])[:5])

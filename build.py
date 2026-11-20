#!/usr/bin/env python3
"""Regenerate data.js from src/data.json, merging derived network metrics.

data/network.json is produced by make_network.py from the ESMAP gridfinder
line layer. Missing countries simply carry nulls.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
data = json.loads((ROOT / "src" / "data.json").read_text())

net_path = ROOT / "data" / "network.json"
net = {}
if net_path.exists():
    net = json.loads(net_path.read_text()).get("rows", {})

merged = 0
for row in data["rows"]:
    n = net.get(row["iso"])
    if n:
        row["net_km"] = n.get("km")
        row["km_per_1000km2"] = n.get("km_per_1000km2")
        row["km_per_1000_people"] = n.get("km_per_1000_people")
        merged += 1
    else:
        row.setdefault("net_km", None)
        row.setdefault("km_per_1000km2", None)
        row.setdefault("km_per_1000_people", None)

data["meta"]["network_source"] = "ESMAP gridfinder predicted network, CC BY 4.0"
body = json.dumps(data, ensure_ascii=False, indent=1)
(ROOT / "data.js").write_text("window.TRACKER_DATA = " + body + ";\n")
print(f"wrote data.js ({len(body)} bytes, {len(data['rows'])} rows, {merged} with network metrics)")

# machine-readable export for agents and analysts
export = {
    "name": "DashDist - distribution grid indicators",
    "url": "https://electrifysimon.github.io/dashdist/",
    "as_of": data["meta"].get("as_of"),
    "licence": "CC BY 4.0",
    "units": {
        "pop_m": "millions", "access": "percent of population",
        "urban": "percent of urban population", "rural": "percent of rural population",
        "unserved_m": "millions, population x (1 - access/100)",
        "losses": "percent of electrical output", "kwh_pc": "kWh per capita",
        "gdp_pc": "current USD per capita", "net_km": "km of predicted distribution network",
        "km_per_1000km2": "km per 1000 km2", "km_per_1000_people": "km per 1000 people",
        "year_access": "year of latest observation", "year_losses": "year of latest observation",
        "year_kwh": "year of latest observation",
    },
    "rows": data["rows"],
}
(ROOT / "data" / "dashboard.json").write_text(json.dumps(export, ensure_ascii=False, indent=1))
print("wrote data/dashboard.json (%d rows)" % len(export["rows"]))

(ROOT / "llms.txt").write_text("""# DashDist

URL: https://electrifysimon.github.io/dashdist/
Machine-readable data: https://electrifysimon.github.io/dashdist/data/dashboard.json
Licence: CC BY 4.0. Attribution: Simon Benmarraze, DashDist.

## What it is
A country panel of distribution grid indicators for 113 countries above five
million population. Four views: access gap, consumption and losses, predicted
network, data coverage. Two chart tabs: Apache ECharts and ChartGPU (WebGPU).
A world map renders the same indicators in 2D, 3D and globe projection.

## Fields in data/dashboard.json rows
iso (ISO3), country, region, income, pop_m (millions), access (percent),
urban (percent), rural (percent), unserved_m (millions, population times one
minus access), losses (percent of output), kwh_pc (kWh per capita),
gdp_pc (current USD), net_km (predicted network length), km_per_1000km2,
km_per_1000_people, year_access, year_losses, year_kwh.

## Sources
World Bank World Development Indicators (CC BY 4.0). ESMAP gridfinder predicted
distribution network, World Bank (CC BY 4.0), about 70 percent validated at 1 km.
Natural Earth 110m boundaries (public domain). OpenFreeMap and OpenStreetMap
contributors (ODbL) for the basemap.

## Caveats
Network length is model output, not an asset register. Unserved people are derived,
not reported. Countries below five million population are excluded.
""")
print("wrote llms.txt")

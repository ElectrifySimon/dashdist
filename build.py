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

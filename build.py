#!/usr/bin/env python3
"""Regenerate data.js from src/data.json."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
data = json.loads((ROOT / "src" / "data.json").read_text())
body = json.dumps(data, ensure_ascii=False, indent=1)
(ROOT / "data.js").write_text("window.TRACKER_DATA = " + body + ";\n")
print(f"wrote data.js ({len(body)} bytes, {len(data['rows'])} rows)")

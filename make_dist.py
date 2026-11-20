#!/usr/bin/env python3
"""Build dist/index.html: gate-free single file ready for Staticrypt."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
html = (ROOT / "index.html").read_text()
data = (ROOT / "data.js").read_text()

html = html.replace('<script src="data.js"></script>', "<script>" + data + "</script>")
html = re.sub(r'<section id="lock".*?</section>\s*', "", html, flags=re.S)
html = html.replace('<div class="wrap" id="app" hidden>', '<div class="wrap" id="app">')
html = re.sub(
    r"/\* GATE-START \*/.*?/\* GATE-END \*/",
    "  start();",
    html,
    flags=re.S,
)
for needle in ("GATE-START", 'id="lock"'):
    if needle in html:
        raise SystemExit(f"build failed, leftover: {needle}")
(ROOT / "dist").mkdir(exist_ok=True)
(ROOT / "dist" / "index.html").write_text(html)
print(f"wrote dist/index.html ({len(html)} bytes)")

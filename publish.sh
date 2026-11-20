#!/usr/bin/env bash
# Build the gated publish folder: gated/index.html (encrypted) + data/ + vendor/
set -euo pipefail
cd "$(dirname "$0")"

python3 build.py

rm -rf build gated
mkdir -p build
cp index.tpl.html build/index.html
# inline data.js so the table data sits inside the encrypted payload
python3 - <<'PY'
import pathlib, re
p = pathlib.Path("build/index.html")
html = p.read_text()
data = pathlib.Path("data.js").read_text()
html = html.replace('<script src="data.js"></script>', "<script>" + data + "</script>")
# staticrypt is the only gate: strip the in-page lock and start immediately
html = re.sub(r'<section id="lock".*?</section>\s*', "", html, flags=re.S)
html = html.replace('<div class="wrap" id="app" hidden>', '<div class="wrap" id="app">')
html = re.sub(r"/\* GATE-START \*/.*?/\* GATE-END \*/", "start();", html, flags=re.S)
for needle in ("GATE-START", 'id="lock"'):
    if needle in html:
        raise SystemExit("build failed, leftover: " + needle)
p.write_text(html)
print("inlined data.js and stripped inner gate:", len(html), "bytes")
PY

npx --yes staticrypt@3.5.4 build/index.html -p distribution -d gated --remember 0 --short

mkdir -p gated/data
cp data/countries.geo.json data/grid_presence.png data/density.png data/dashboard.json gated/data/
cp -r data/tiles gated/data/tiles
cp -r vendor gated/
cp README.md gated/README.md 2>/dev/null || true
cp llms.txt gated/llms.txt
echo "--- gated tree ---"
find gated -maxdepth 2 -type f | sort
du -sh gated

# DashDist dev log

Public, keyless, open-source distribution-grid dashboard. Live at
https://electrifysimon.github.io/dashdist/ behind a Staticrypt passphrase.
Repo: https://github.com/ElectrifySimon/dashdist (branch `master`).

Read this before touching anything. It carries the state, the method that
converged, and the traps that cost time.

## State at 2026-11-23

HEAD `8e90b56`. Working tree clean. Local server for testing:
`python3 -m http.server 8098 --bind 127.0.0.1` from the repo root, then
`http://127.0.0.1:8098/gated/index.html`.

Pass condition after every publish:

- 6 tabs, 5 KPI cards, 113 rows in each of the three tables
- map zoom 2.1, 3D pitch 52, 4 ECharts canvases, `errs []`
- page scrolls: `scrollHeight` about 2069, not 1000

Verified on the build now live: 5 KPIs, 6 tabs, zoom 2.1, pitch 52, 4 charts,
zero console errors, scroll intact, contour background rated 8/10 by the vision
review.

## What shipped, in order

1. Data and map: 113 countries, 170-country predicted network (9,133,932 km),
   MapLibre with local vector tiles, deck.gl overlay for choropleth and lines,
   2D / 3D / globe.
2. Charts: four ECharts panels with crosshair tooltips, never covering the map.
3. Design system: `DESIGN.md` is the contract. Near-black canvas, graphite
   panels, mint accent, Instrument Sans for UI, Bricolage Grotesque for the
   wordmark, Lucide icons, 4px space scale, three elevations.
4. Surface craft: floating glass toolbar over the map, hairline borders with a
   shadow, 36px KPI figures with unit split, underline tabs, four-column footer
   with provenance, entrance stagger.
5. Background: fixed canvas contour field in the accent colour, drifting at a
   tide pace, plus 4.5 percent fractal-noise grain. 30fps cap, stops on tab
   hide, single paint under reduced motion.
6. Map legibility: every basemap symbol layer hidden, water and boundaries
   retuned, one-hue access ramp with rising lightness, neutral grey for no-data,
   network lines as a 3px halo plus a thin core.

## The method that actually worked

Change, screenshot at 1440, ask a vision model for one blunt rating and the
single worst flaw, fix that flaw, repeat. Two or three rounds moved the page
from "cluttered functional dump" to 8.5/10 while my own judgement of the work
stayed flat. My taste is not a reliable grader here; the loop is.

Screenshot pipeline: LXC 106 to magnus host to LXC 111, then
`docker cp mg-atelier-desktop:/tmp/shots/x.png` before `pct pull`. Chrome on
port 9222 needs `--no-sandbox`. Cache-bust every probe with `?v=$(date +%s)`.

## Open items

1. **Basemap is third-party.** `https://tiles.openfreemap.org/styles/dark` is
   fetched at runtime. Self-hosting the style and the tiles is the remaining
   breach of the "self-hosted" requirement.
2. **ChartGPU tab.** WebGPU adapter is null on mg-atelier across five flag sets.
   The tab explains itself and points at the ECharts tab. Either find a machine
   with a working adapter or drop the tab.
3. **Light theme background.** Tuned for dark only; never screenshot-reviewed.
   Grain is multiply at 8.5 percent there.
4. **Country labels.** Hidden deliberately, so hover and the table carry names.
   Revisit only if the map feels mute.
5. **Mobile 390 review.** Not run since the repaint.
6. **Repo hygiene for the long life.** No README with the data provenance, no
   LICENSE file, no committed screenshots.

## Traps already paid for

- Never `replace("body{", ...)`. It also matches `html,body{` and makes the
  document `position:fixed`, which silently kills scrolling. The accent glow
  belongs on `body::before`.
- Staticrypt fields are `#staticrypt-password` and `input[type=submit]`, not
  `#gate input`.
- SVG `<rect>` has no default fill; sparklines rendered black until
  `fill="currentColor"` went in.
- Heredocs collapse through `pct exec`. Use base64-pipe for multi-KB writes.
- Probes must be cache-busted or GitHub Pages serves the previous build.
- Ramp colours are the map's meaning. One hue family with rising lightness, five
  stops; no-data in neutral grey. A rainbow ramp reads as mud and a pale tint for
  missing data steals attention from real values.

# DashDist data manifest

Everything the dashboard reads, where it came from, and what it feeds.
Last built 2026-11-20.

## Downloaded files

| File | Size | md5 prefix | Licence | Feeds |
|---|---|---|---|---|
| `data/raw/grid.gpkg` | 692M | e5d0e9bd8ce4 | CC BY 4.0 | Network table: predicted line km per country |
| `data/raw/lv.tif` | 240M | d2e4e3078ab3 | CC BY 4.0 | Reserved for low-voltage availability analysis |
| `data/raw/targets.tif` | 28M | 14ea25c90df8 | CC BY 4.0 | `data/grid_presence.png`, the world map overlay |
| `data/countries.geo.json` | 172K | cc591136fa4b | Public domain (Natural Earth) | Country polygons for the map and area maths |
| `data/grid_presence.png` | 256K | 29d2b46a14f2 | derived | Map raster layer |
| `data/network.json` | 20K | bfb0914ec3cf | derived | Network table, density colour |

`data/raw/` is gitignored. It holds about 960M and can be fetched again from the
source URLs below.

## Sources

- ESMAP gridfinder, World Bank, Zenodo record 3628142.
  `https://zenodo.org/records/3628142/files/grid.gpkg?download=1`
  `https://zenodo.org/records/3628142/files/lv.tif?download=1`
  `https://zenodo.org/records/3628142/files/targets.tif?download=1`
  Predicted transmission and distribution network, about 70 percent accurate at 1 km.
- World Bank World Development Indicators, API v2, indicators
  `EG.ELC.ACCS.ZS`, `EG.ELC.ACCS.UR.ZS`, `EG.ELC.ACCS.RU.ZS`, `EG.ELC.LOSS.ZS`,
  `EG.USE.ELEC.KH.PC`, `SP.POP.TOTL`, `NY.GDP.PCAP.CD`, 2010 to 2025,
  latest non-null observation per country. Licence CC BY 4.0.
- Natural Earth 110m admin 0 countries, via `nvkelso/natural-earth-vector`.
  Public domain. `ISO_A3` with `ADM0_A3` fallback.
- Line geometry is served from `data/tiles/`, generated locally by `make_tiles.py`
  from `data/raw/grid.gpkg`. Nothing is fetched from a third party at runtime.
- Basemap: OpenFreeMap `dark` style, OpenStreetMap data, ODbL. No API key.

## Derived network metrics

`make_network.py` reads `grid.gpkg`, reprojects to EPSG:6933, measures each
segment, joins segments to country polygons, and sums length per ISO code.

Output per country: predicted network length in km, km per 1000 km squared, and
km per 1000 people. 170 countries have lines, 111 of the 113 dashboard countries
match. Hong Kong and Singapore have no predicted lines at this resolution.

Global total: 9,133,932 km of predicted network.

These are model output, not a utility statistic. They are comparable across
countries because the same model produced them, which is the point. They are not
a substitute for a regulator's own asset register.

## Rebuild

```
/home/simon/.venvs/geo/bin/python make_network.py   # network.json, about 4 min
python3 build.py                                    # merge into data.js
bash publish.sh                                      # encrypt and stage gated/
```

## Line tiles

`make_tiles.py` cuts the 3.7M-segment network into static GeoJSON tiles:

- `data/tiles/4/` 84 files, 1.9 MB, simplify 0.08 degrees, parts under 0.15 degrees dropped
- `data/tiles/5/` 247 files, 18.5 MB, simplify 0.02 degrees, parts under 0.05 degrees dropped

Below zoom 3 the page shows the presence raster only. Zoom 3 to 4.5 loads level 4
tiles, above that level 5. Tiles are cached in the browser per session.

## Vendored libraries

| File | Version | Licence |
|---|---|---|
| `vendor/maplibre-gl.mjs` + worker + css | 6.19.0 | BSD-3-Clause |
| `vendor/deck.gl.min.js` | 9.4.1 | MIT |
| `vendor/vizzu.min.js` + `vendor/cvizzu.wasm` | 0.18.0 | Apache-2.0 (61,404 + 399,475 bytes) |

All of these are served from the site. No CDN and no API key at runtime.

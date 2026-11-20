# DashDist

Distribution grid dashboard for 113 countries. Access gap, consumption and
losses, network length, and a 2D, 3D and globe map of the predicted grid.

Live: https://electrifysimon.github.io/dashdist/
Passphrase: on request

## Stack

- MapLibre GL JS 6.19, deck.gl 9.4, OpenFreeMap basemap, no API keys
- Static single-file gate via Staticrypt 3.5.4
- Data: World Bank WDI, ESMAP gridfinder, Natural Earth

## Build

```
python3 build.py        # merge src/data.json with data/network.json
bash publish.sh         # inline, encrypt, stage gated/
```

Data sources and file hashes: `data/MANIFEST.md`.

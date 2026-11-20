# Distribution Grid Dashboard

Country panel on electricity distribution: access, consumption and network losses.

Live: https://electrifysimon.github.io/distribution-grid-dashboard/

Passphrase: shared separately.

## Data

World Bank World Development Indicators, latest available year per series (2010 to 2025):

- `EG.ELC.ACCS.ZS` access to electricity, % of population
- `EG.ELC.ACCS.UR.ZS` access, urban
- `EG.ELC.ACCS.RU.ZS` access, rural
- `EG.ELC.LOSS.ZS` electric power transmission and distribution losses, % of output
- `EG.USE.ELEC.KH.PC` electric power consumption per capita
- `SP.POP.TOTL` population
- `NY.GDP.PCAP.CD` GDP per capita

Countries under 5 million population are excluded. Unserved population is derived as population x (1 - access rate).

## Scope

Three tables: access gap, consumption and losses, data coverage. Network asset data (line length, transformer capacity) and distribution capex are absent because no public country series exists. That layer needs a primary survey.

## Build

```
python3 build.py       # src/data.json -> data.js
python3 make_dist.py   # gate-free single file -> dist/index.html
npx staticrypt dist/index.html -p <passphrase> -d gated --remember 0 --short
cp gated/index.html index.html
```

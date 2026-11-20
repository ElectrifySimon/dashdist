"""Render the gridfinder network as a density field for the world view.

The published page used to show `targets.tif` as an overlay, which is a thin
presence raster: at world zoom it reads as faint lines, not shading. This
aggregates the actual network length per 0.25 degree cell and paints a heat
field, so zoomed out it reads as density and zoomed in the vector lines take
over.

Input : data/raw/grid.gpkg
Output: data/density.png  (0.25 degree cells, teal ramp, alpha by density)
"""
import numpy as np
import pyogrio
import shapely
from PIL import Image

GPKG = "data/raw/grid.gpkg"
OUT = "data/density.png"
CELL = 0.25
W, H = 1440, 720

gdf = pyogrio.read_dataframe(GPKG, columns=[])
geoms = gdf.geometry.values
print("features", len(geoms), flush=True)

lengths = shapely.length(geoms)
# midpoint of each segment, in degrees
mid = shapely.get_coordinates(shapely.centroid(geoms))
print("centroids", mid.shape, flush=True)

# drop the antimeridian outliers
ok = np.isfinite(mid).all(axis=1)
mid, lengths = mid[ok], lengths[ok]

col = np.clip(((mid[:, 0] + 180.0) / 360.0 * W).astype(int), 0, W - 1)
row = np.clip(((90.0 - mid[:, 1]) / 180.0 * H).astype(int), 0, H - 1)

acc = np.zeros((H, W), dtype=np.float32)
np.add.at(acc, (row, col), lengths.astype(np.float32))
print("cells with data", int((acc > 0).sum()), "total deg", float(acc.sum()), flush=True)

# fill holes a little so the field reads as an area, not confetti
def box_blur(a, k=3):
    p = np.pad(a, k, mode="edge")
    c = np.cumsum(np.cumsum(p, axis=0), axis=1)
    c = np.pad(c, ((1, 0), (1, 0)))
    return (c[2*k+1:, 2*k+1:] - c[:-2*k-1, 2*k+1:] - c[2*k+1:, :-2*k-1] + c[:-2*k-1, :-2*k-1]) / ((2*k+1) ** 2)

field = box_blur(acc, 2)
field = np.log1p(field * 40.0)
field /= max(1e-6, field.max())

# teal ramp, alpha follows the field
stops = [(0.00, (20, 60, 80)),
         (0.25, (26, 120, 130)),
         (0.50, (34, 211, 238)),
         (0.75, (125, 235, 190)),
         (1.00, (250, 240, 150))]
xs = np.array([s[0] for s in stops])
cols = np.array([s[1] for s in stops], dtype=np.float32)
t = np.clip(field, 0, 1)
r = np.interp(t, xs, cols[:, 0])
g = np.interp(t, xs, cols[:, 1])
b = np.interp(t, xs, cols[:, 2])
a = np.clip(np.sqrt(t) * 255 * 1.35, 0, 235)

img = np.zeros((H, W, 4), dtype=np.uint8)
img[..., 0] = r.astype(np.uint8)
img[..., 1] = g.astype(np.uint8)
img[..., 2] = b.astype(np.uint8)
img[..., 3] = a.astype(np.uint8)
Image.fromarray(img, "RGBA").save(OUT, optimize=True)
print("wrote", OUT, flush=True)

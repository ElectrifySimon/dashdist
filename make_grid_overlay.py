#!/usr/bin/env python3
"""Render the ESMAP gridfinder targets raster as a web-mercator PNG overlay.

Input: data/targets.tif, EPSG:4326, 15 arc-second, binary mask of locations
predicted to be connected to a distribution grid.
Output: data/grid_presence.png, rows evenly spaced in mercator Y.
"""
import math
import numpy as np
import rasterio
from PIL import Image

SRC = "/home/simon/projects/distribution-dashboard/data/targets.tif"
OUT = "/home/simon/projects/distribution-dashboard/data/grid_presence.png"

W = 4096
with rasterio.open(SRC) as ds:
    b = ds.bounds
    print("bounds", b, "crs", ds.crs, "size", ds.width, ds.height)
    # decimated read, keep aspect. Read 4x and block-max so thin lines survive.
    h = int(round(W * (b.top - b.bottom) / (b.right - b.left)))
    arr = ds.read(1, out_shape=(h * 4, W * 4), resampling=rasterio.enums.Resampling.nearest)
    arr = arr.reshape(h, 4, W, 4).max(axis=(1, 3))
print("decimated", arr.shape, "unique", np.unique(arr)[:6])

top_lat, bot_lat = b.top, b.bottom


def merc(lat):
    lat = max(min(lat, 85.05), -85.05)
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


y_top, y_bot = merc(top_lat), merc(bot_lat)
H = int(round(W * (y_top - y_bot) / (2 * math.pi)))
print("mercator canvas", W, H)

out = np.zeros((H, W, 4), dtype=np.uint8)
for row in range(H):
    my = y_top + (y_bot - y_top) * (row + 0.5) / H
    lat = math.degrees(2 * math.atan(math.exp(my)) - math.pi / 2)
    src_row = int((top_lat - lat) / (top_lat - bot_lat) * (arr.shape[0] - 1))
    src_row = max(0, min(arr.shape[0] - 1, src_row))
    line = arr[src_row]
    mask = line == 1
    out[row, mask, 0] = 76
    out[row, mask, 1] = 194
    out[row, mask, 2] = 160
    out[row, mask, 3] = 120

Image.fromarray(out, "RGBA").save(OUT, optimize=True)
import os
print("wrote", OUT, os.path.getsize(OUT), "bytes")

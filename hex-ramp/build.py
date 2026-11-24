#!/usr/bin/env python3
"""Add a tileable honeycomb of through-holes to ramp_half.stl to cut weight.

Part anatomy (STL coords):
  X : ramp running length   -105.6 .. +31.4  (plate 0.06 -> 13.7 -> 0.06 mm thick)
  Y : plate thickness axis   0 .. 17.9       (holes are cut along this axis)
  Z : ramp half width        0 .. 228.6      (2 x 228.6 = 457.2 mm = 18 in)

Honeycomb: flat-top hexagons on a triangular lattice, rows every p/2 with the
seam land = WEB/2 at each Z end, so a mirrored copy butts up seamlessly and the
joint reads as one normal rib.
"""
import numpy as np, trimesh

import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--src", default="/home/reed/Downloads/ramp_half.stl")
ap.add_argument("--out", default="ramp_half_hex.stl")
ap.add_argument("--web", type=float, default=4.5)   # rib width between holes
ap.add_argument("--rows", type=int, default=19)     # lattice rows over 228.6 mm
ap.add_argument("--min-t", type=float, default=2.5) # skip thinner material
ap.add_argument("--x-marg", type=float, default=3.0)
ap.add_argument("--sample", type=float, default=1.0,
                help="fraction of the hex footprint that must be thick enough")
a = ap.parse_args()

SRC, OUT = a.src, a.out
WEB, N_ROWS, MIN_T, X_MARG, SAMPLE = a.web, a.rows, a.min_t, a.x_marg, a.sample

# ---- load -------------------------------------------------------------------
part = trimesh.load(SRC, process=True)
part.fix_normals()
assert part.is_watertight
b = part.bounds
X0, X1 = b[0, 0], b[1, 0]
Z0, Z1 = b[0, 2], b[1, 2]
ZMAX = Z1 - Z0

p = ZMAX / N_ROWS                  # row pitch  (2 rows per p)
a = p - WEB                        # hex across-flats
R = a / np.sqrt(3)                 # hex circumradius
col = np.sqrt(3) * p               # in-row horizontal pitch

# ---- plate thickness vs X ---------------------------------------------------
xs = np.linspace(X0, X1, 2000)
loc = np.stack([xs, np.full_like(xs, b[0, 1] - 5), np.full_like(xs, ZMAX / 2)], 1)
pts, idx, _ = part.ray.intersects_location(loc, np.tile([0.0, 1.0, 0.0], (len(loc), 1)))
ylo = np.full(len(loc), np.nan)
yhi = np.full(len(loc), np.nan)
for y, i in zip(pts[:, 1], idx):
    ylo[i] = np.nanmin([ylo[i], y]) if not np.isnan(ylo[i]) else y
    yhi[i] = np.nanmax([yhi[i], y]) if not np.isnan(yhi[i]) else y
thick = yhi - ylo
good = ~np.isnan(thick)
xs, thick = xs[good], thick[good]
local_t = lambda x: np.interp(x, xs, thick)

# ---- hexagon prisms ---------------------------------------------------------
def hex_prism(cx, cz, r, y0, y1):
    """Flat-top regular hexagon in the XZ plane, extruded along Y."""
    ang = np.arange(6) * np.pi / 3          # vertices at 0/60/.../300 deg
    x = cx + r * np.cos(ang)
    z = cz + r * np.sin(ang)
    v = np.vstack([np.stack([x, np.full(6, y0), z], 1),
                   np.stack([x, np.full(6, y1), z], 1)])
    f = []
    for k in range(6):
        k2 = (k + 1) % 6
        f += [[k, k2, k2 + 6], [k, k2 + 6, k + 6]]
    f += [[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 5]]
    f += [[6, 8, 7], [6, 9, 8], [6, 10, 9], [6, 11, 10]]
    m = trimesh.Trimesh(v, np.array(f), process=True)
    trimesh.repair.fix_normals(m)
    return m

hexes, skipped = [], []
y0, y1 = b[0, 1] - 5, b[1, 1] + 5
for j in range(1, 2 * N_ROWS):                   # rows every p/2; k=0 and k=2n
    cz = Z0 + j * p / 2                          # sit on the seam edges -> skipped
    off = (col / 2) if (j % 2) else 0.0
    x = X0 + X_MARG + off
    while x <= X1 - X_MARG:
        ang = np.arange(6) * np.pi / 3
        r = R * SAMPLE
        xsamp = np.concatenate([x + r * np.cos(ang),
                                x + r * np.cos(ang + np.pi / 6),
                                [x - r, x, x + r]])
        if local_t(xsamp).min() >= MIN_T:
            hexes.append(hex_prism(x, cz, R, y0, y1))
        else:
            skipped.append((x, cz))
        x += col

print(f"lattice p={p:.2f} a={a:.2f} R={R:.2f} col={col:.2f} web={WEB} "
      f"rows={2*N_ROWS} open={100*1.5*np.sqrt(3)*R*R/(0.5*p*col):.0f}%")
print(f"holes kept={len(hexes)} skipped={len(skipped)}")

# ---- cut -------------------------------------------------------------------
out = trimesh.boolean.difference([part] + hexes, engine="manifold", check_volume=True)
out.fix_normals()
assert out.is_watertight and out.body_count == 1
print(f"volume {part.volume/1000:.1f} -> {out.volume/1000:.1f} cm3 "
      f"(-{100*(1-out.volume/part.volume):.1f}%)  faces {len(out.faces)}")
out.export(OUT)
np.save(OUT.replace(".stl", "_hexes.npy"), np.array([[h.centroid[0], h.centroid[2]] for h in hexes]))
print("wrote", OUT)

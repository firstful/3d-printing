#!/usr/bin/env python3
"""
Generate a printable internal support tree for the filter sphere cavity.

PRINT ORIENTATION: collet down, on the build plate. In model coordinates the
print direction is -Z, so the cavity ceiling is the model's *lower* inner
hemisphere (z < -z_safe). Everything at z >= -z_safe is within `thresh` of
vertical and prints on its own.

Algorithm (as specified):
  1. sample random points on the overhanging ceiling
  2. find the nearest safe geometry
  3. if nothing safe within R_sup, cast rays at EXACTLY `branch_ang` from the
     vertical axis and take the shortest that reaches safe geometry
  4. add that branch, mark what it covers, repeat

Safe geometry = the self-supporting wall (off the apertures) + the vertical
columns + any branch already generated. Columns are tested first in effect,
since taking the shortest ray naturally prefers a nearby column over the far
side of the sphere.
"""

import math
import numpy as np

# ---- geometry -------------------------------------------------------------
Ri = 36.1                      # cavity radius
Ro = 38.1                      # outer radius

# vertical columns (must match lattice() in strainer-assembly.scad)
COL_XY = [-24, -8, 8, 24]
COL_D = 2.5
COL_R = COL_D/2
COL_Ri = 36.5                  # lattice clips against this

# ---- printability ---------------------------------------------------------
thresh = 20.0                  # deg from vertical: self-supporting below this
branch_ang = 20.0              # deg from vertical -- all rays use exactly this
R_sup = 10.0                   # max unsupported reach for a P1S
branch_r = 1.2

z_safe = Ri*math.cos(math.radians(90.0 - thresh))
sin_b = math.sin(math.radians(branch_ang))
cos_b = math.cos(math.radians(branch_ang))

rng = np.random.default_rng(7)

# ---- aperture pattern (must match strainer-assembly.scad) -----------------
HOLE_D = 1.5
PITCH = 3.0


def hole_dirs():
    dirs = []
    dlat = (PITCH*math.sqrt(3)/2)/Ro*180/math.pi
    n = int(168//dlat)
    for i in range(n+1):
        lat = -84 + i*dlat
        lon_step = (PITCH/Ro)*180/math.pi/math.cos(math.radians(lat))
        off = (i % 2)*lon_step/2
        lon = off
        while lon < 360 + off - 0.01:
            la, lo = math.radians(lat), math.radians(lon)
            dirs.append([math.cos(la)*math.cos(lo),
                         math.cos(la)*math.sin(lo),
                         math.sin(la)])
            lon += lon_step
    return np.array(dirs)


HOLES = hole_dirs()
HOLE_R = HOLE_D/2


def off_holes(pts):
    if len(HOLES) == 0:
        return np.ones(len(pts), bool)
    u = pts/np.linalg.norm(pts, axis=1)[:, None]
    d = np.arccos(np.clip(u @ HOLES.T, -1, 1))*Ri
    return d.min(axis=1) > HOLE_R + 0.15


def pillars():
    out = []
    for x in COL_XY:
        for y in COL_XY:
            r = math.hypot(x, y)
            if r < COL_Ri - 3:
                hz = math.sqrt(COL_Ri**2 - r*r)
                out.append((np.array([x, y, -hz]), np.array([x, y, hz])))
    return out


PILLARS = pillars()

# ---- sampling -------------------------------------------------------------
def sample_cap(n):
    out = []
    while sum(len(a) for a in out) < n:
        v = rng.normal(size=(6*n, 3))
        v /= np.linalg.norm(v, axis=1)[:, None]
        v = v[v[:, 2] < -z_safe/Ri]*Ri
        out.append(v[off_holes(v)])
    return np.vstack(out)[:n]


def sample_safe(n):
    out = []
    while sum(len(a) for a in out) < n:
        v = rng.normal(size=(6*n, 3))
        v /= np.linalg.norm(v, axis=1)[:, None]
        v = v[v[:, 2] >= -z_safe/Ri]*Ri
        out.append(v[off_holes(v)])
    return np.vstack(out)[:n]


ceil_pts = sample_cap(3000)
safe_pts = sample_safe(4000)
print(f"ceiling samples {len(ceil_pts)}, safe samples {len(safe_pts)}, "
      f"holes {len(HOLES)}, columns {len(PILLARS)}")

branches = []


def seg_dist(pts, A, B):
    AB = B - A
    L2 = AB @ AB
    if L2 < 1e-12:
        return np.linalg.norm(pts - A, axis=1)
    t = np.clip(((pts - A) @ AB)/L2, 0.0, 1.0)
    return np.linalg.norm(pts - (A + t[:, None]*AB), axis=1)


def support_dist(pts):
    d = np.full(len(pts), np.inf)
    for i in range(0, len(pts), 256):
        chunk = pts[i:i+256]
        dd = np.linalg.norm(chunk[:, None, :] - safe_pts[None, :, :],
                            axis=2).min(axis=1)
        d[i:i+256] = np.minimum(d[i:i+256], dd)
    for (A, B) in PILLARS:
        d = np.minimum(d, seg_dist(pts, A, B) - COL_R)
    for (A, B) in branches:
        d = np.minimum(d, seg_dist(pts, A, B))
    return d


def ray_seg(P, d, A, B, rad):
    """ray/segment closest approach; returns t or inf"""
    AB = B - A
    w0 = P - A
    a = d @ d
    b = d @ AB
    c = AB @ AB
    dd = d @ w0
    e = AB @ w0
    den = a*c - b*b
    if abs(den) < 1e-9:
        return np.inf
    s = (b*e - c*dd)/den
    u = (a*e - b*dd)/den
    if s > 0.5 and -0.05 <= u <= 1.05:
        dist = np.linalg.norm(P + s*d - (A + np.clip(u, 0, 1)*AB))
        if dist < rad:
            return s
    return np.inf


def cast(P):
    """shortest ray at exactly branch_ang from the vertical axis that reaches
    safe geometry. Columns are just segments in the hit test, so a nearby
    column wins automatically when it is the shortest."""
    best = None
    for k in range(72):
        az = 2*math.pi*k/72
        d = np.array([sin_b*math.cos(az), sin_b*math.sin(az), cos_b])
        # exact: the ray is (sin20*cos, sin20*sin, cos20), |d| = 1
        t_hit = np.inf
        t = -2.0*(P @ d)
        if t > 0.5:
            Q = P + t*d
            if Q[2] >= -z_safe:
                t_hit = t
        for (A, B) in PILLARS:
            t_hit = min(t_hit, ray_seg(P, d, A, B, COL_R + branch_r))
        for (A, B) in branches:
            t_hit = min(t_hit, ray_seg(P, d, A, B, branch_r*2.0))
        if t_hit < np.inf and (best is None or t_hit < best[0]):
            best = (t_hit, d)
    return best


for it in range(150):
    d = support_dist(ceil_pts)
    worst = int(np.argmax(d))
    if d[worst] <= R_sup:
        break
    P = ceil_pts[worst]
    res = cast(P)
    if res is None:
        # still exactly branch_ang: pick azimuth 0 rather than going vertical
        d_vec = np.array([sin_b, 0.0, cos_b])
        t = -2.0*(P @ d_vec)
    else:
        t, d_vec = res
    Q = P + t*d_vec
    # extend along the ray itself (not radially) so the segment stays exactly
    # branch_ang from vertical, while still burying both ends in the shell
    A = P - 0.6*d_vec
    B = Q + 0.6*d_vec
    branches.append((A, B))

final = support_dist(ceil_pts)
print(f"z_safe            = {z_safe:.2f} mm")
print(f"branches          = {len(branches)}")
print(f"max uncovered     = {final.max():.2f} mm  (R_sup {R_sup})")
print(f"uncovered > R_sup = {(final > R_sup).sum()}")

total = sum(np.linalg.norm(B-A) for A, B in branches)
print(f"total branch len  = {total:.0f} mm   "
      f"volume ~ {math.pi*branch_r**2*total/1000:.2f} cm3")


def vec(v):
    return f"[{v[0]:.3f},{v[1]:.3f},{v[2]:.3f}]"


with open("generated-supports.scad", "w") as f:
    f.write("// generated by gen_supports.py -- do not edit by hand\n")
    f.write(f"// {len(branches)} branches, max uncovered {final.max():.2f} mm\n")
    f.write("// print orientation: collet down, supports rise toward +Z\n")
    f.write("// every branch is exactly 20 deg from the vertical axis\n\n")
    f.write("module generated_supports() {\n")
    for A, B in branches:
        f.write("    hull() {\n")
        f.write(f"        translate({vec(A)}) sphere(r={branch_r}, $fn=12);\n")
        f.write(f"        translate({vec(B)}) sphere(r={branch_r}, $fn=12);\n")
        f.write("    }\n")
    f.write("}\n")

print("wrote generated-supports.scad")

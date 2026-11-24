#!/usr/bin/env python3
"""Minimal binary-STL inspector: bbox, volume, watertightness, connected bodies."""
import struct, sys
from collections import defaultdict


def load(path):
    with open(path, "rb") as f:
        data = f.read()
    n = struct.unpack_from("<I", data, 80)[0]
    tris = []
    off = 84
    for _ in range(n):
        vals = struct.unpack_from("<12f", data, off)
        tris.append((vals[3:6], vals[6:9], vals[9:12]))
        off += 50
    return tris


def inspect(path):
    tris = load(path)
    pts = [p for t in tris for p in t]
    xs, ys, zs = zip(*pts)
    vol = 0.0
    for a, b, c in tris:
        vol += (a[0] * (b[1] * c[2] - b[2] * c[1])
                - a[1] * (b[0] * c[2] - b[2] * c[0])
                + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0

    # watertight: every directed edge must have exactly one reverse partner
    edges = defaultdict(int)
    for t in tris:
        for i in range(3):
            u, v = t[i], t[(i + 1) % 3]
            edges[(u, v)] += 1
    open_edges = 0
    for (u, v), cnt in edges.items():
        if edges.get((v, u), 0) != cnt:
            open_edges += 1

    # connected bodies: union-find over vertices shared by triangles
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for t in tris:
        union(t[0], t[1])
        union(t[1], t[2])
    bodies = len({find(p) for p in parent})

    print(f"=== {path}")
    print(f"  triangles      : {len(tris)}")
    print(f"  bbox X         : {min(xs):8.3f} .. {max(xs):8.3f}   ({max(xs)-min(xs):7.3f} mm)")
    print(f"  bbox Y         : {min(ys):8.3f} .. {max(ys):8.3f}   ({max(ys)-min(ys):7.3f} mm)")
    print(f"  bbox Z         : {min(zs):8.3f} .. {max(zs):8.3f}   ({max(zs)-min(zs):7.3f} mm)")
    print(f"  volume         : {abs(vol)/1000.0:8.3f} cm^3")
    print(f"  PLA mass       : {abs(vol)/1000.0*1.24:8.2f} g   (1.24 g/cm^3)")
    print(f"  open edges     : {open_edges}")
    print(f"  separate bodies: {bodies}")
    return dict(bbox=(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs)),
                vol=abs(vol) / 1000.0, bodies=bodies, open_edges=open_edges)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        inspect(p)

#!/usr/bin/env python3
"""Extract the EXACT planar polygon of a flat face from an STL triangle soup.

Method: pick all triangles lying in a z-plane, quantize vertices (1e-4 mm),
drop interior edges (shared by exactly 2 tris), trace remaining boundary
edges into loops (outer + holes), merge collinear runs, RDP-simplify.

Output: face_top.json / face_bot.json with points + paths (SCAD-ready).
"""
import json
import sys
from collections import Counter

import numpy as np

ZTOL = 1e-3   # z-plane tolerance
Q = 10000     # coordinate quantization = 0.0001 mm


def shoelace(loop):
    a = 0.0
    n = len(loop)
    for i in range(n):
        x1, y1 = loop[i]
        x2, y2 = loop[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return a


def rdp(pts, eps):
    """Rammer-Douglas-Peucker for closed removal (open list here)."""
    if len(pts) < 3:
        return [np.asarray(p) for p in pts]
    stack = [(0, len(pts) - 1)]
    keep = {0, len(pts) - 1}
    while stack:
        i0, i1 = stack.pop()
        if i1 <= i0 + 1:
            continue
        p0, p1 = np.asarray(pts[i0]), np.asarray(pts[i1])
        seg = p1 - p0
        L = np.linalg.norm(seg)
        if L == 0:
            d = np.linalg.norm(np.asarray(pts[i0 + 1:i1]) - p0, axis=1)
        else:
            v = np.asarray(pts[i0 + 1:i1]) - p0
            cross = np.abs(v[:, 0] * seg[1] - v[:, 1] * seg[0])
            d = cross / L
        imax = int(np.argmax(d))
        if d[imax] > eps:
            k = i0 + 1 + imax
            keep.add(k)
            stack.append((i0, k))
            stack.append((k, i1))
    return [np.asarray(pts[i]) for i in sorted(keep)]


def extract(tris, zval, label):
    sel = np.all(np.abs(tris[:, :, 2] - zval) < ZTOL, axis=1)
    tsel = tris[sel]
    nt = len(tsel)

    # unique vertices, keep float coords of first occurrence
    vdict = {}
    tri_keys = []
    for t in tsel:
        keys = []
        for x, y, z in t:
            k = (int(round(x * Q)), int(round(y * Q)))
            if k not in vdict:
                vdict[k] = (float(x), float(y))
            keys.append(k)
        tri_keys.append(keys)

    # edge multiset over the coplanar patch
    edges = Counter()
    for keys in tri_keys:
        for i in range(3):
            a, b = keys[i], keys[(i + 1) % 3]
            if a == b:
                print(f'{label}: degenerate edge {a}')
                continue
            edges[tuple(sorted((a, b)))] += 1

    hist = Counter(edges.values())
    print(f'{label}: tris={nt} verts={len(vdict)} edges={len(edges)} '
          f'multihist={dict(sorted(hist.items()))}')
    bad = [(e, c) for e, c in edges.items() if c > 2]
    if bad:
        print(f'{label}: {len(bad)} edges shared >2! sample={bad[:6]}')

    bnd = [(a, b) for (a, b), c in edges.items() if c == 1]
    adj = {}
    for a, b in bnd:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    used = set()
    loops = []
    for a, b in bnd:
        e = tuple(sorted((a, b)))
        if e in used:
            continue
        loop = [a, b]
        used.add(e)
        prev, cur = a, b
        while True:
            nxt = None
            for cand in adj[cur]:
                ce = tuple(sorted((cur, cand)))
                if ce not in used and cand != prev:
                    nxt = (cand, ce)
                    break
            if nxt is None:
                break
            prev, cur = cand, nxt[0]
            used.add(nxt[1])
            if cur == loop[0]:
                break
            loop.append(cur)
        loops.append(loop)

    loopsxy = [np.array([[vdict[k][0], vdict[k][1]] for k in loop])
               for loop in loops]
    areas = [shoelace(l.tolist()) for l in loopsxy]
    so = np.argsort([-abs(a) for a in areas])
    loopsxy = [loopsxy[i] for i in so]
    areas = [areas[i] for i in so]
    print(f'{label}: loops={len(loops)} |outer|={abs(areas[0]):.3f} '
          f'hole_count={len(areas)-1} '
          f'sum_abs={sum(abs(a) for a in areas)/2:.2f}')

    # merge collinear then RDP
    simplified = []
    for loop in loopsxy:
        n = len(loop)
        out = []
        i = 0
        while i < n:
            p = loop[i]
            q = loop[(i + 1) % n]
            r = loop[(i + 2) % n]
            v1 = q - p
            v2 = r - q
            n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
            if n1 > 0 and n2 > 0:
                cr = v1[0] * v2[1] - v1[1] * v2[0]
                dt = float(v1 @ v2) / (n1 * n2)
                i_move = True
                if abs(cr) < 1e-7 and dt > 0.999999:
                    i_move = True  # drop q (straight)
                    out.append(p)
            if out == [] or not np.allclose(out[-1], p, atol=1e-9):
                out.append(p)
            i += 1
        pts = [tuple(p) for p in out]
        pts = rdp(pts, 0.02)
        simplified.append([list(p) for p in pts])

    npts = sum(len(s) for s in simplified)
    outer_a = shoelace(simplified[0])
    holes_a = sum(shoelace(s) for s in simplified[1:])
    exact = round(sum(abs(a) for a in areas) / 2, 4)
    print(f'{label}: simplified pts={npts} outer_signed={outer_a:.3f} '
          f'holes_signed_sum={holes_a:.3f} exact_area={exact}')
    # signed areas: OpenSCAD wants outer CCW(+), holes CW(-)
    if outer_a < 0:
        simplified[0] = simplified[0][::-1]
    for j in range(1, len(simplified)):
        a = shoelace(simplified[j])
        if a > 0:
            simplified[j] = simplified[j][::-1]
    return {'tris': nt, 'verts': len(vdict), 'loops': simplified,
            'exact_area': exact,
            'outer_area': abs(outer_a),
            'nholes': len(simplified) - 1}


def main():
    tris = np.load(sys.argv[1])
    faces = []
    for zval, name in ((6.2, 'top'), (0.0, 'bot')):
        r = extract(tris, zval, name.upper())
        faces.append(r)
    # cross-check that the two faces share identical outline
    def canon(r):
        return sorted(sorted((round(x, 4), round(y, 4)) for x, y in loop)
                      for loop in r['loops'])
    same = canon(faces[0]) == canon(faces[1])
    print('TOP outline == BOTTOM outline:', same)
    json.dump({'top': faces[0], 'bot': faces[1], 'outline_equal': same,
               'Q': Q}, open('face_polygon.json', 'w'))
    print('wrote face_polygon.json')


if __name__ == '__main__':
    main()

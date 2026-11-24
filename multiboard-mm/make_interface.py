#!/usr/bin/env python3
"""Generate the M_Interface slab: exact contact patch between stacked plates.

Reads face_polygon.json (produced by extract_face_polygon.py) and writes an
OpenSCAD file that extrudes the polygon (outer + 114 holes) by one layer
height. Produces interface_0.2.stl / interface_0.1.stl via OpenSCAD.
"""
import json
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'face_polygon.json')


def scad_for(polygon, height, out_scad):
    pts, paths = [], []
    base = 0
    for i, loop in enumerate(polygon):
        for x, y in loop:
            pts.append([x, y])
        paths.append([j + base for j in range(len(loop))])
        base += len(loop)
    with open(out_scad, 'w') as f:
        f.write('// auto-generated; do not edit\n')
        f.write('pts = %s;\n' % str(pts))
        f.write('paths = %s;\n' % str(paths))
        f.write('height = %r;\n' % height)
        f.write('linear_extrude(height=height, convexity=10) polygon(points=pts, paths=paths);\n')


def main():
    data = json.load(open(SRC))
    poly = data['top']['loops']
    for h in (0.2, 0.1):
        out_scad = os.path.join(HERE, f'interface_{h:.1f}.scad'.replace('0.1', '0p1').replace('0.2', '0p2'))
        out_stl = out_scad.replace('.scad', '.stl')
        scad_for(poly, h, out_scad)
        print('writing', out_stl)
        r = subprocess.run(['openscad', '-o', out_stl, out_scad],
                           capture_output=True, text=True, timeout=900)
        if r.returncode != 0 or not os.path.exists(out_stl):
            print('OpenSCAD FAILED:', r.stderr[-2000:])
            sys.exit(1)
        print('  ok, size', os.path.getsize(out_stl))


if __name__ == '__main__':
    main()

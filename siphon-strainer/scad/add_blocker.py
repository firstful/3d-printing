#!/usr/bin/env python3
"""
Turn the loose 'Sphere' object in the Bambu project into a proper support
blocker that is a part of the strainer object, sized and placed to fill the
cavity.

The blocker mesh is baked at its final size/position so every transform stays
identity -- no ambiguity between the component transform and the part matrix.
"""
import math
import os
import re
import shutil
import zipfile

PROJECT = os.path.expanduser("~/opencode-sessions/siphon-strainer")
SRC = os.path.join(PROJECT, "stl/strainer-assembly.3mf")
WORK = os.path.join(PROJECT, "build/p3mf")

# cavity: centre in mesh coords, and a radius that stays inside the 36.1 shell
CAVITY_R = 35.5
CAVITY_Z = 16.972946          # = print z 72.0 - build translate 55.027054


def sphere_model(path, r, cz, nlat=24, nlon=48):
    verts = []
    # top pole
    verts.append((0.0, 0.0, cz + r))
    idx = {}
    for i in range(1, nlat):
        th = math.pi*i/nlat
        rr = r*math.sin(th)
        zz = cz + r*math.cos(th)
        for j in range(nlon):
            ph = 2*math.pi*j/nlon
            idx[(i, j)] = len(verts)
            verts.append((rr*math.cos(ph), rr*math.sin(ph), zz))
    verts.append((0.0, 0.0, cz - r))
    bot = len(verts)-1

    tris = []
    # top cap
    for j in range(nlon):
        tris.append((0, idx[(1, j)], idx[(1, (j+1) % nlon)]))
    # bands
    for i in range(1, nlat-1):
        for j in range(nlon):
            a = idx[(i, j)]
            b = idx[(i, (j+1) % nlon)]
            c = idx[(i+1, (j+1) % nlon)]
            d = idx[(i+1, j)]
            tris.append((a, b, c))
            tris.append((a, c, d))
    # bottom cap
    for j in range(nlon):
        tris.append((bot, idx[(nlat-1, (j+1) % nlon)], idx[(nlat-1, j)]))

    with open(path, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<model unit="millimeter" xml:lang="en-US" '
                'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n')
        f.write(' <resources>\n')
        f.write('  <object id="3" type="model">\n   <mesh>\n    <vertices>\n')
        for v in verts:
            f.write(f'     <vertex x="{v[0]:.6f}" y="{v[1]:.6f}" z="{v[2]:.6f}"/>\n')
        f.write('    </vertices>\n    <triangles>\n')
        for t in tris:
            f.write(f'     <triangle v1="{t[0]}" v2="{t[1]}" v3="{t[2]}"/>\n')
        f.write('    </triangles>\n   </mesh>\n  </object>\n </resources>\n</model>\n')
    return len(tris)


shutil.rmtree(WORK, ignore_errors=True)
os.makedirs(WORK, exist_ok=True)
with zipfile.ZipFile(SRC) as z:
    z.extractall(WORK)

nfaces = sphere_model(os.path.join(WORK, "3D/Objects/object_4.model"),
                      CAVITY_R, CAVITY_Z)
print(f"blocker mesh: {nfaces} faces, r={CAVITY_R}, cz={CAVITY_Z}")

# ---- patch 3dmodel.model --------------------------------------------------
p = os.path.join(WORK, "3D/3dmodel.model")
s = open(p).read()

comp = ('    <component p:path="/3D/Objects/object_4.model" objectid="3" '
        'p:UUID="00040000-b206-40ff-9872-83e8017abed1" '
        'transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n')
s = s.replace(
    '    <component p:path="/3D/Objects/object_2.model" objectid="1" '
    'p:UUID="00020000-b206-40ff-9872-83e8017abed1" '
    'transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n',
    '    <component p:path="/3D/Objects/object_2.model" objectid="1" '
    'p:UUID="00020000-b206-40ff-9872-83e8017abed1" '
    'transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n' + comp)

# drop the standalone object 4 and its build item
s = re.sub(r'  <object id="4".*?</object>\n', '', s, flags=re.S)
s = re.sub(r'  <item objectid="4".*?/>\n', '', s, flags=re.S)
open(p, "w").write(s)

# ---- patch model_settings.config -----------------------------------------
p = os.path.join(WORK, "Metadata/model_settings.config")
s = open(p).read()

part2 = (f'    <part id="2" subtype="support_blocker" '
         f'uuid="b509e336-0187-4d86-9513-1f918295aab7">\n'
         f'      <metadata key="name" value="Sphere"/>\n'
         f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'
         f'      <mesh_stat face_count="{nfaces}" edges_fixed="0" '
         f'degenerate_facets="0" facets_removed="0" facets_reversed="0" '
         f'backwards_edges="0"/>\n'
         f'    </part>\n')

# insert after the first part of object 2
s = re.sub(r'(<part id="1" subtype="normal_part".*?</part>\n)', r'\1' + part2,
           s, count=1, flags=re.S)

# remove the standalone object 4 block, its instance and its assemble items
s = re.sub(r'  <object id="4">.*?</object>\n', '', s, flags=re.S)
s = re.sub(r'    <model_instance>\s*<metadata key="object_id" value="4"/>.*?</model_instance>\n',
           '', s, flags=re.S)
s = re.sub(r'   <assemble_item object_id="4".*?/>\n', '', s, flags=re.S)

open(p, "w").write(s)

# ---- rezip ---------------------------------------------------------------
tmp_out = SRC + ".new"
with zipfile.ZipFile(tmp_out, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(WORK, "[Content_Types].xml"), "[Content_Types].xml")
    for root, _, files in os.walk(WORK):
        for fn in files:
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, WORK)
            if rel == "[Content_Types].xml":
                continue
            z.write(full, rel)
os.replace(tmp_out, SRC)
print("rewrote", SRC)

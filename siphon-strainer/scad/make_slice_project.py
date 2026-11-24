#!/usr/bin/env python3
"""Wrap strainer-nosupport.stl into a sliceable Bambu 3MF project."""
import os, re, struct, zipfile, shutil, math

PROJECT = os.path.expanduser("~/opencode-sessions/siphon-strainer")
SRC_STL = os.path.join(PROJECT, "stl/strainer-nosupport.stl")
TEMPLATE = os.path.join(PROJECT, "stl/strainer-assembly.3mf")
OUT = os.path.join(PROJECT, "build/slice/nosupport.3mf")
WORK = os.path.join(PROJECT, "build/slice/work")

# --- read binary STL
data = open(SRC_STL, "rb").read()
n = struct.unpack_from("<I", data, 80)[0]
dt = [("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]
import numpy as np
arr = np.frombuffer(data, dtype=np.dtype(dt), count=n, offset=84)
V = arr["v"].reshape(-1, 3).astype(np.float64)
zmin, zmax = V[:, 2].min(), V[:, 2].max()
cx = (V[:, 0].min() + V[:, 0].max())/2
cy = (V[:, 1].min() + V[:, 1].max())/2
V[:, 0] -= cx; V[:, 1] -= cy; V[:, 2] -= zmin
height = zmax - zmin
print(f"mesh: {n} tris, height {height:.2f}, x/y centred")

shutil.rmtree(WORK, ignore_errors=True)
os.makedirs(WORK, exist_ok=True)
with zipfile.ZipFile(TEMPLATE) as z:
    z.extractall(WORK)

# --- rewrite the model mesh
# --- weld the duplicated STL vertices into a shared index (otherwise the
#     slicer sees every triangle as its own floating shell)
vidx = {}
tris = []
for i in range(n):
    tri = []
    for k in range(3):
        key = tuple(np.round(V[i*3+k], 5))
        if key not in vidx:
            vidx[key] = len(vidx)
        tri.append(vidx[key])
    tris.append(tri)

lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<model unit="millimeter" xml:lang="en-US" '
         'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
         ' <resources>', '  <object id="1" type="model">', '   <mesh>', '    <vertices>']
for key in vidx:
    lines.append(f'     <vertex x="{key[0]:.5f}" y="{key[1]:.5f}" z="{key[2]:.5f}"/>')
lines += ['    </vertices>', '    <triangles>']
for t in tris:
    lines.append(f'     <triangle v1="{t[0]}" v2="{t[1]}" v3="{t[2]}"/>')
lines += ['    </triangles>', '   </mesh>', '  </object>', ' </resources>', '</model>']
open(os.path.join(WORK, "3D/Objects/object_2.model"), "w").write("\n".join(lines))
print(f"welded to {len(vidx)} vertices")

# --- drop the now-moot blocker object, fix the build transform
p = os.path.join(WORK, "3D/3dmodel.model")
s = open(p).read()
s = re.sub(r'    <component p:path="/3D/Objects/object_4\.model".*?/>\n', '', s)
s = re.sub(r'  <object id="4".*?</object>\n', '', s, flags=re.S)
s = re.sub(r'  <item objectid="4".*?/>\n', '', s, flags=re.S)
s = re.sub(r'(<item objectid="2"[^>]*transform=")1 0 0 0 1 0 0 0 1 [-\d.]+ [-\d.]+ [-\d.]+(")',
           rf'\g<1>1 0 0 0 1 0 0 0 1 128 128 0\g<2>', s)
open(p, "w").write(s)

# --- model settings: single normal part, supports off
p = os.path.join(WORK, "Metadata/model_settings.config")
s = open(p).read()
s = re.sub(r'    <part id="2" subtype="support_blocker".*?</part>\n', '', s, flags=re.S)
s = re.sub(r'  <object id="4">.*?</object>\n', '', s, flags=re.S)
s = re.sub(r'    <model_instance>\s*<metadata key="object_id" value="4"/>.*?</model_instance>\n', '', s, flags=re.S)
s = re.sub(r'   <assemble_item object_id="4".*?/>\n', '', s, flags=re.S)
s = re.sub(r'face_count="\d+"', f'face_count="{n}"', s)
s = s.replace('<metadata key="support_on_build_plate_only" value="1"/>',
              '<metadata key="support_on_build_plate_only" value="0"/>')
open(p, "w").write(s)

if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(WORK, "[Content_Types].xml"), "[Content_Types].xml")
    for root, _, files in os.walk(WORK):
        for fn in files:
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, WORK)
            if rel == "[Content_Types].xml":
                continue
            z.write(full, rel)
print("wrote", OUT, os.path.getsize(OUT)//1024, "KB")

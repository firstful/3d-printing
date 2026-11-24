#!/usr/bin/env python3
"""Wrap a hex-cut STL into a copy of the user's Bambu project (same plate,
same process settings, optional overrides) so it can be sliced as-is.

usage: make_3mf.py <stl> <out.3mf> [key=value ...]
"""
import shutil, zipfile, json, sys
import numpy as np, trimesh
from pathlib import Path

SRC_3MF = Path("mf")
OFFSET = np.array([-37.078778266906738, 8.9544649124145508, 114.30000305175781])

stl, out_path = Path(sys.argv[1]), Path(sys.argv[2])
overrides = dict(kv.split("=", 1) for kv in sys.argv[3:])

m = trimesh.load(stl, process=True)
V = m.vertices - OFFSET
F = m.faces

body = ['   <mesh>', '    <vertices>']
body += [f'     <vertex x="{v[0]:.7f}" y="{v[1]:.7f}" z="{v[2]:.7f}"/>' for v in V]
body += ['    </vertices>', '    <triangles>']
body += [f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in F]
body += ['    </triangles>', '   </mesh>']
new_mesh = "\n".join(body)

src = (SRC_3MF / "3D/Objects/object_2.model").read_text()
i = src.index("<mesh>")
j = src.index("</mesh>") + len("</mesh>")
patched = src[:i] + new_mesh.strip() + src[j:]

work = out_path.parent / "project"
if work.exists():
    shutil.rmtree(work)
shutil.copytree(SRC_3MF, work)
(work / "3D/Objects/object_2.model").write_text(patched)
(work / "Metadata/model_settings.config").write_text(
    (SRC_3MF / "Metadata/model_settings.config").read_text().replace(
        'value="ramp_half.stl"', f'value="{stl.name}"'))

if overrides:
    cfg_path = work / "Metadata/project_settings.config"
    cfg = json.loads(cfg_path.read_text())
    for k, v in overrides.items():
        assert k in cfg, f"unknown setting {k}"
        cfg[k] = v
        print(f"  {k} = {v}")
    cfg_path.write_text(json.dumps(cfg, indent=4))

out_path.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(work / "[Content_Types].xml", "[Content_Types].xml")
    z.write(work / "_rels/.rels", "_rels/.rels")
    for f in sorted(work.rglob("*")):
        if f.is_file() and f.name not in ("[Content_Types].xml", ".rels"):
            z.write(f, str(f.relative_to(work)))
print("wrote", out_path, f"({len(F)} tris)")

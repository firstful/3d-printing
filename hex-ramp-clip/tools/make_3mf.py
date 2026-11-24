#!/usr/bin/env python3
"""Wrap a clip STL in the user's Bambu P1S project template and slice it.

usage: make_3mf.py <stl> <out.3mf> [key=value ...]
"""
import shutil, zipfile, json, sys
import trimesh
from pathlib import Path

SRC_3MF = Path("/home/reed/opencode-sessions/ramp-half-hex/mf")

stl, out_path = Path(sys.argv[1]), Path(sys.argv[2])
overrides = dict(kv.split("=", 1) for kv in sys.argv[3:])

m = trimesh.load(stl, process=True)
V, F = m.vertices, m.faces
lo, hi = V.min(0), V.max(0)
tx, ty = 128.0 - (lo[0] + hi[0]) / 2, 128.0 - (lo[1] + hi[1]) / 2

body = ["   <mesh>", "    <vertices>"]
body += [f'     <vertex x="{v[0]:.7f}" y="{v[1]:.7f}" z="{v[2]:.7f}"/>' for v in V]
body += ["    </vertices>", "    <triangles>"]
body += [f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in F]
body += ["    </triangles>", "   </mesh>"]
new_mesh = "\n".join(body)

work = out_path.parent / "project"
if work.exists():
    shutil.rmtree(work)
shutil.copytree(SRC_3MF, work)

src = (work / "3D/Objects/object_2.model").read_text()
i = src.index("<mesh>"); j = src.index("</mesh>") + len("</mesh>")
(work / "3D/Objects/object_2.model").write_text(src[:i] + new_mesh + src[j:])

model = (work / "3D/3dmodel.model").read_text()
import re
model = re.sub(r'<item objectid="2"[^/]*/>',
               f'<item objectid="2" transform="1 0 0 0 1 0 0 0 1 {tx:.4f} {ty:.4f} 0" printable="1"/>',
               model)
(work / "3D/3dmodel.model").write_text(model)

cfg = (work / "Metadata/model_settings.config").read_text()
cfg = cfg.replace('value="ramp_half_hex.stl"', f'value="{stl.name}"')
for k in ("source_offset_x", "source_offset_y", "source_offset_z"):
    cfg = re.sub(r'(key="%s" value=")[^"]*' % k, r'\g<1>0', cfg)
(work / "Metadata/model_settings.config").write_text(cfg)

if overrides:
    p = work / "Metadata/project_settings.config"
    c = json.loads(p.read_text())
    for k, v in overrides.items():
        assert k in c, f"unknown setting {k}"
        c[k] = v
    p.write_text(json.dumps(c, indent=4))

out_path.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(work / "[Content_Types].xml", "[Content_Types].xml")
    z.write(work / "_rels/.rels", "_rels/.rels")
    for f in sorted(work.rglob("*")):
        if f.is_file() and f.name not in ("[Content_Types].xml", ".rels"):
            z.write(f, str(f.relative_to(work)))
print("wrote", out_path, f"({len(F)} tris)")

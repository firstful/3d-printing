#!/usr/bin/env python3
"""Minimal multi-filament assignment experiments for Bambu CLI.

Builds cube STLs + tiny 3MF projects in several layouts, slices each with
Bambu CLI, and reports '; filament: n' + M620/T tool lines so we learn how
Bambu Studio 2.8 assigns extruders to objects/parts.
"""
import json
import os
import re
import struct
import subprocess
import uuid
import zipfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.expanduser("~/.local/bin/BambuStudio")
DT = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])


def cube_stl(path, cx, cy, z0, size=20.0, h=2.0):
    x0, x1 = cx - size / 2, cx + size / 2
    y0, y1 = cy - size / 2, cy + size / 2
    z1 = z0 + h
    v = [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
    ]
    # bottom (down), top (up), sides
    quads = [
        (3, 2, 1, 0, (0, 0, -1)),     # bottom
        (4, 5, 6, 7, (0, 0, 1)),      # top
        (0, 1, 5, 4, (0, -1, 0)),
        (1, 2, 6, 5, (1, 0, 0)),
        (2, 3, 7, 6, (0, 1, 0)),
        (3, 0, 4, 7, (0, -1, 0)),
    ]
    tris = []
    for a, b, c, d, n in quads:
        tris.append((a, b, c, n))
        tris.append((a, c, d, n))
    with open(path, "wb") as f:
        f.write(b"cube".ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        rec = np.zeros(len(tris), dtype=DT)
        for i, (a, b, c, n) in enumerate(tris):
            rec["n"][i] = n
            rec["v"][i] = [v[a], v[b], v[c]]
        rec.tofile(f)


def weld(tris):
    vbits = tris.astype(np.float32).view(np.uint32).reshape(-1, 3)
    keys = {}
    out = []
    for k in map(tuple, vbits):
        if k not in keys:
            keys[k] = len(keys)
    verts = [struct.unpack("<fff", struct.pack("<III", *k)) for k in keys]
    idx = np.array([keys[k] for k in map(tuple, vbits)]).reshape(-1, 3)
    return verts, idx


def mesh_xml(objid, verts, tris):
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<model unit="millimeter" xml:lang="en-US" '
         'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
         ' <resources>', f'  <object id="{objid}" type="model">', '   <mesh>',
         '    <vertices>']
    L += ['     <vertex x="%.4f" y="%.4f" z="%.4f"/>' % t for t in verts]
    L += ['    </vertices>', '    <triangles>']
    L += ['     <triangle v1="%d" v2="%d" v3="%d"/>' % tuple(t) for t in tris]
    L += ['    </triangles>', '   </mesh>', '  </object>', ' </resources>',
          '</model>']
    return "\n".join(L)


IDENT = lambda: str(uuid.uuid4())


def compose(out, layout, ps_base=json.load(open(os.path.join(HERE, "refx-p1s-project_settings.json")))):
    """layout: 'objects' or 'one-object-parts'"""
    d = os.path.dirname(out)
    os.makedirs(d, exist_ok=True)
    cube_stl(os.path.join(d, "c1.stl"), 0, 0, 0)
    cube_stl(os.path.join(d, "c2.stl"), 0, 0, 2.2)   # stacked variant
    c1 = read_cube(os.path.join(d, "c1.stl"))
    c2 = read_cube(os.path.join(d, "c2.stl"))
    v1, t1 = weld(c1)
    v2, t2 = weld(c2)

    if layout == "objects":
        comps = [
            ('/3D/Objects/m1.model', 1, "1 0 0 0 1 0 0 0 1 118 118 0"),
            ('/3D/Objects/m2.model', 1, "1 0 0 0 1 0 0 0 1 158 138 0"),
        ]
        objs = [(1, "c1.stl", 1), (2, "c2.stl", 2)]
        parts_xml = None
        mesh_specs = [('/3D/Objects/m1.model', 1, v1, t1),
                      ('/3D/Objects/m2.model', 1, v2, t2)]
    else:
        # rook-verified multi-part layout: part ids 1,3,...; EVERY part gets its
        # own mesh file whose <object id> matches the part id, and the
        # component objectid matches too. Component transform carries z.
        comps = [
            ('/3D/Objects/object_1.model', 1, "1 0 0 0 1 0 0 0 1 0 0 0"),
            ('/3D/Objects/object_3.model', 3, "1 0 0 0 1 0 0 0 1 0 0 2.2"),
        ]
        objs = None
        parts_xml = [(1, "c1.stl", 1, len(c1)), (3, "c2.stl", 2, len(c2))]
        mesh_specs = [('/3D/Objects/object_1.model', 1, v1, t1),
                      ('/3D/Objects/object_3.model', 3, v2, t2)]

    # main model
    R = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<model unit="millimeter" xml:lang="en-US" '
         'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
         'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" '
         'requiredextensions="p">',
         ' <resources>']
    if objs:
        for oid, _, _ in objs:
            R += [f'  <object id="{oid}" p:UUID="{IDENT()}" type="model">',
                  '   <components>',
                  f'    <component p:path="/3D/Objects/m{oid}.model" objectid="1" '
                  f'p:UUID="{IDENT()}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>',
                  '   </components>', '  </object>']
        items = [f'  <item objectid="{oid}" p:UUID="{IDENT()}" '
                 f'transform="1 0 0 0 1 0 0 0 1 {tx} {ty} 0" printable="1"/>'
                 for oid, (tx, ty) in zip([1, 2], [(118, 118), (158, 138)])]
    else:
        R += ['  <object id="1" p:UUID="%s" type="model">' % IDENT(),
              '   <components>']
        for i, (path, _, t) in enumerate(comps):
            R.append(f'    <component p:path="{path}" objectid="1" '
                     f'p:UUID="{IDENT()}" transform="{t}"/>')
        R += ['   </components>', '  </object>']
        items = [f'  <item objectid="1" p:UUID="{IDENT()}" '
                 'transform="1 0 0 0 1 0 0 0 1 128 128 0" printable="1"/>']
    R += [' </resources>', f' <build p:UUID="{IDENT()}">'] + items + [' </build>', '</model>']
    model = "\n".join(R)

    # model_settings
    M = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>']
    if objs:
        for oid, name, ex in objs:
            M += [f'  <object id="{oid}">',
                  f'    <metadata key="name" value="{name}"/>',
                  f'    <metadata key="extruder" value="{ex}"/>',
                  '    <part id="1" subtype="normal_part" uuid="%s">' % IDENT(),
                  f'      <metadata key="extruder" value="{ex}"/>',
                  f'      <metadata key="name" value="{name}"/>',
                  '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>',
                  f'      <mesh_stat face_count="{len(c1) if oid==1 else len(c2)}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>',
                  '    </part>', '  </object>']
        insts = [(1, 0), (2, 0)]
    else:
        M += ['  <object id="1">',
              '    <metadata key="name" value="twocubes"/>',
              '    <metadata key="extruder" value="1"/>',
              f'    <metadata face_count="{len(c1)}"/>']
        for k, (pid, name, ex, fc) in enumerate(parts_xml):
            M += [f'    <part id="{pid}" subtype="normal_part" uuid="{IDENT()}">',
                  f'      <metadata key="extruder" value="{ex}"/>',
                  f'      <metadata key="name" value="{name}"/>',
                  '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>',
                  f'      <mesh_stat face_count="{len(c1) if pid==1 else len(c2)}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>',
                  '    </part>']
        M += ['  </object>']
        insts = [(1, 0)]
    M += ['  <plate>',
          '    <metadata key="plater_id" value="1"/>',
          '    <metadata key="plater_name" value=""/>',
          '    <metadata key="locked" value="false"/>',
          '    <metadata key="filament_map_mode" value="Auto For Flush"/>',
          '    <metadata key="filament_maps" value="1 1"/>',
          '    <metadata key="filament_volume_maps" value="0 0"/>']
    for oid, iid in insts:
        M += ['    <model_instance>',
              f'      <metadata key="object_id" value="{oid}"/>',
              f'      <metadata key="instance_id" value="{iid}"/>',
              f'      <metadata key="identify_id" value="{oid}"/>',
              '    </model_instance>']
    M += ['  </plate>', '  <assemble/>', '</config>']
    ms = "\n".join(M)

    ps = dict(ps_base)
    ps["enable_prime_tower"] = "1"
    ps["enable_support"] = "0"
    ps["elefant_foot_compensation"] = "0"
    # per-filament physical mapping (single-nozzle P1S: every filament -> extruder 1)
    ps["filament_map"] = ["1", "1"]
    ps["filament_nozzle_map"] = ["1", "1"]
    ps["filament_volume_map"] = ["0", "0"]
    for k, v in list(ps.items()):
        if k.startswith("filament_") and isinstance(v, list) and len(v) == 1:
            ps[k] = v * 2
    ps["filament_colour"] = ["#DCF000", "#FF6A00"]
    ps["filament_type"] = ["PLA", "PLA"]
    ps["nozzle_temperature"] = ["220", "220"]
    ps["nozzle_temperature_initial_layer"] = ["220", "220"]
    ps["filament_density"] = ["1.21", "1.21"]
    ps["filament_diameter"] = ["1.75", "1.75"]
    ps["flush_volumes_vector"] = ["140"] * 8
    ps["flush_volumes_matrix"] = ["0", "280", "280", "280",
                                   "280", "0", "280", "280",
                                   "280", "280", "0", "280",
                                   "280", "280", "280", "0"]
    ps = json.dumps(ps)

    nmesh = len(mesh_specs)
    rels_layers = []
    for i in range(nmesh):
        p, oid, _, _ = mesh_specs[i]
        rels_layers.append(
            f' <Relationship Target="{p}" Id="rel-{i+1}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>')
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
                   open(os.path.join(HERE, "refx", "[Content_Types].xml")).read())
        z.writestr("_rels/.rels", open(os.path.join(HERE, "refx", "_rels/.rels")).read())
        z.writestr("3D/_rels/3dmodel.model.rels",
                   '<?xml version="1.0" encoding="UTF-8"?>\n'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                   + "\n".join(rels_layers) + "\n</Relationships>\n")
        z.writestr("3D/3dmodel.model", model)
        for i, (_, oid, v, t) in enumerate(mesh_specs):
            name = os.path.basename(mesh_specs[i][0])
            z.writestr("3D/Objects/" + name, mesh_xml(oid, v, t))
        z.writestr("Metadata/model_settings.config", ms)
        z.writestr("Metadata/project_settings.config", ps)


def read_cube(path):
    with open(path, "rb") as f:
        n = struct.unpack("<I", open(path, "rb").read(84)[80:])[0]
        arr = np.fromfile(path, dtype=DT, count=n, offset=84)
    return arr["v"].reshape(-1, 3, 3).astype(np.float64)


def run(tag):
    out3mf = os.path.join(HERE, "build", f"mmtest_{tag}.3mf")
    outdir = os.path.join(HERE, "build", f"mmtest_out_{tag}")
    r = subprocess.run([BIN, "--slice", "1", "--outputdir", outdir, out3mf],
                       capture_output=True, text=True, timeout=600)
    gcode = os.path.join(outdir, "plate_1.gcode")
    info = ""
    if os.path.exists(gcode):
        head = open(gcode, "r", errors="replace").read(3000)
        fil = re.findall(r"; filament: (\d+)", head)
        lens = re.findall(r"; total filament length \[mm\] : (.*)", head)
        switches = []
        with open(gcode, "r", errors="replace") as f:
            for ln in f:
                if re.match(r"^M620 S\d+A", ln) or re.match(r"^T\d+$", ln) or re.match(r"^T\d+ ", ln):
                    if "T1000" not in ln and "T255" not in ln:
                        switches.append(ln.strip())
                if len(switches) > 8:
                    break
        info = f"filament_count={fil} lengths={lens} switches={switches[:8]}"
    else:
        info = f"NO GCODE rc={r.returncode} err={r.stderr[-400:]}"
    print(f"[{tag}] {info}")


if __name__ == "__main__":
    for tag, layout in (("A_two_objects", "objects"), ("B_one_object_2parts", "parts")):
        compose(os.path.join(HERE, "build", f"mmtest_{tag}.3mf"), layout)
        run(tag)

#!/usr/bin/env python3
"""Build + slice cube variants to isolate which model_settings contract the
Bambu CLI honors for per-part extruder + z offsets.

Variants (single bed item, two stacked cubes 20x20x2 at z=0 and z=2.2):
  B2 : names+per-part extruder, part matrix z offsets, model_instance entries,
       self-closing <assemble/>                        (patched schema, one unknown left)
  C  : B2 + xmlns:BambuStudio + root metadata + source_* part metadata
       + real <assemble> block, NO model_instance      (refx-verbatim style)
  D  : C but part-blocks carry no extruder metadata   (control: default 1)
"""
import json
import os
import re
import struct
import subprocess
import zipfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.expanduser("~/.local/bin/BambuStudio")
DT = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
BUILD = os.path.join(HERE, "build")


def cube_mesh(cx, cy, z0, size=20.0, h=2.0):
    """Return (vertices, triangle-indices) of a welded cube."""
    x0, x1 = cx - size / 2, cx + size / 2
    y0, y1 = cy - size / 2, cy + size / 2
    z1 = z0 + h
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    quads = [(3, 2, 1, 0, (0, 0, -1)), (4, 5, 6, 7, (0, 0, 1)),
             (0, 1, 5, 4, (0, -1, 0)), (1, 2, 6, 5, (1, 0, 0)),
             (2, 3, 7, 6, (0, 1, 0)), (3, 0, 4, 7, (0, -1, 0))]
    tris = []
    for a, b, c, d, _ in quads:
        tris += [(a, b, c), (a, c, d)]
    return v, tris


V1, T1 = cube_mesh(0, 0, 0)
V2, T2 = cube_mesh(0, 0, 0)          # z offset carried by component/matrix
Z2 = 2.2


def mesh_file(objid, verts, tris):
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<model unit="millimeter" xml:lang="en-US" '
         'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
         'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
         'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" '
         'requiredextensions="p">',
         ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
         ' <resources>', f'  <object id="{objid}" type="model">', '   <mesh>',
         '    <vertices>']
    L += ['     <vertex x="%.4f" y="%.4f" z="%.4f"/>' % t for t in verts]
    L += ['    </vertices>', '    <triangles>']
    L += ['     <triangle v1="%d" v2="%d" v3="%d"/>' % tuple(t) for t in tris]
    L += ['    </triangles>', '   </mesh>', '  </object>', ' </resources>', '</model>']
    return "\n".join(L)


def part_block(pid, name, extruder, mesh_stat, matrix_tz, with_extruder=True,
               with_source=True, uuid="{UU}"):
    tz = f"{matrix_tz:.12f}"
    L = [f'    <part id="{pid}" subtype="normal_part" uuid="{uuid}">',
         f'      <metadata key="name" value="{name}"/>']
    if with_extruder:
        L.append(f'      <metadata key="extruder" value="{extruder}"/>')
    L.append(f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 {tz} 0 0 0 1"/>')
    if with_source:
        L += ['      <metadata key="source_file" value="{}"/>'.format(name),
              '      <metadata key="source_object_id" value="0"/>',
              '      <metadata key="source_volume_id" value="0"/>',
              '      <metadata key="source_offset_x" value="0"/>',
              '      <metadata key="source_offset_y" value="0"/>',
              '      <metadata key="source_offset_z" value="{:.12f}"/>'.format(matrix_tz)]
    L.append(f'      <mesh_stat face_count="{mesh_stat}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>')
    L.append('    </part>')
    return "\n".join(L)


def model_settings(spec, with_instance, assemble_full):
    """spec: list of (part_id, name, extruder, mesh_stat, tz, with_extruder)"""
    L = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>',
         '  <object id="1">',
         '    <metadata key="name" value="twocubes"/>',
         '    <metadata key="extruder" value="1"/>',
         '    <metadata face_count="%d"/>' % (12 + 12)]
    for pid, name, ex, fc, tz, wex in spec:
        L.append(part_block(pid, name, ex, fc, tz, with_extruder=wex)
                 .replace("{UU}", "00000001-0000-0000-0000-%012d" % pid))
    L.append('  </object>')
    L.append('  <plate>')
    L += ['    <metadata key="plater_id" value="1"/>',
          '    <metadata key="plater_name" value=""/>',
          '    <metadata key="locked" value="false"/>',
          '    <metadata key="filament_map_mode" value="Auto For Flush"/>',
          '    <metadata key="filament_maps" value="%s"/>' % " ".join("1" for _ in spec),
          '    <metadata key="filament_volume_maps" value="%s"/>' % " ".join("0" for _ in spec),
          '    <metadata key="gcode_file" value=""/>']
    if with_instance:
        L += ['    <model_instance>',
              '      <metadata key="object_id" value="1"/>',
              '      <metadata key="instance_id" value="0"/>',
              '      <metadata key="identify_id" value="1"/>',
              '    </model_instance>']
    L.append('  </plate>')
    if assemble_full:
        L += ['  <assemble>', '  </assemble>']
    else:
        L.append('  <assemble/>')
    L.append('</config>')
    xml = "\n".join(L)
    return xml


def mesh_name(pid):
    # four_mat-style: mesh file object_<pid>.model holding <object id="<pid>">
    return f"/3D/Objects/object_{pid}.model"


def main3mf(spec):
    comps = []
    for pid, name, ex, fc, tz, _ in spec:
        comps.append(
            f'    <component p:path="/3D/Objects/object_{pid}.model" objectid="{pid}" '
            f'transform="1 0 0 0 1 0 0 0 1 0 0 {tz:.12f}"/>')
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<model unit="millimeter" xml:lang="en-US" '
         'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
         'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
         'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" '
         'requiredextensions="p">',
         ' <metadata name="Application">BambuStudio-02.08.02.61</metadata>',
         ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
         ' <metadata name="CreationDate">2026-11-06</metadata>',
         ' <metadata name="Title">twocubes</metadata>',
         ' <resources>',
         '  <object id="1" type="model">',
         '   <components>'] + comps + ['   </components>', '  </object>',
         ' </resources>',
         ' <build>',
         '  <item objectid="1" transform="1 0 0 0 1 0 0 0 1 128 128 0" printable="1"/>',
         ' </build>',
         '</model>']
    return "\n".join(L)


def project_settings(n=4, pla_temp=False):
    """replicates four_mat.3mf contract verified by rook"""
    ps = json.load(open(os.path.join(HERE, "refx-p1s-project_settings.json")))
    ps["enable_prime_tower"] = "1"
    ps["enable_support"] = "0"
    ps["elefant_foot_compensation"] = "0"
    ps["filament_colour"] = ["#DCF000", "#FF6A00", "#0080FF", "#808080"][:n]
    ps["filament_type"] = ["PLA"] * n
    ps["nozzle_temperature"] = ["220"] * n
    ps["nozzle_temperature_initial_layer"] = ["220"] * n
    ps["nozzle_temperature_range_high"] = ["240"] * n
    ps["nozzle_temperature_range_low"] = ["190"] * n
    ps["filament_density"] = ["1.26"] * n
    ps["filament_diameter"] = ["1.75"] * n
    # flush: n x n matrix, diagonal 0, off-diagonals the flush amount
    full = n == 4
    off = "280"
    mat = []
    for i in range(n):
        for j in range(n):
            mat.append("0" if i == j else off)
    ps["flush_volumes_matrix"] = mat
    ps["flush_volumes_vector"] = ["140"] * 8  # matches n=4 reference
    # per-filament physical mapping
    ps["filament_map"] = ["1"] * n
    # filament-domain arrays: pad len-1 lists to n
    for k, v in list(ps.items()):
        if k.startswith("filament_") and isinstance(v, list) and len(v) == 1:
            ps[k] = v * n
    # keys the 4-filament reference does NOT carry (printer-system leftovers)
    for k in ("filament_nozzle_map", "filament_volume_map",
              "extruder_max_nozzle_count", "extruder_nozzle_stats",
              "extruder_nozzle_stats_new", "filament_extruder_compatibility"):
        ps.pop(k, None)
    # pattern-array: repeat the 2 base variants through the filaments
    bev = ps.get("filament_extruder_variant", [])
    if isinstance(bev, list) and 2 <= len(bev) < n:
        ps["filament_extruder_variant"] = (bev * ((n + len(bev) - 1) // len(bev)))[:n]
    # n-sized arrays the reference carries ("Standard" x4)
    for k in ("default_nozzle_volume_type",):
        ps[k] = ["Standard"] * n
    # AMS signature: copy the working file's value (single print-extruder row)
    ps["extruder_ams_count"] = ["1#0|3"] if n == 4 else ps.get("extruder_ams_count", ["1#0|4#0"])
    return json.dumps(ps)


def build(tag, spec, with_instance, assemble_full, n=None):
    out3mf = os.path.join(BUILD, f"mm_{tag}.3mf")
    with zipfile.ZipFile(out3mf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
                   open(os.path.join(HERE, "refx", "[Content_Types].xml")).read())
        z.writestr("_rels/.rels", open(os.path.join(HERE, "refx", "_rels/.rels")).read())
        rels = ['<?xml version="1.0" encoding="UTF-8"?>',
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
        for pid, _, _, _, _, _ in spec:
            rels.append(' <Relationship Target="/3D/Objects/object_%d.model" Id="rel-%d" '
                        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
                        % (pid, pid))
        rels.append('</Relationships>')
        z.writestr("3D/_rels/3dmodel.model.rels", "\n".join(rels))
        z.writestr("3D/3dmodel.model", main3mf(spec))
        for pid, name, ex, fc, tz, _ in spec:
            if name == "c1":
                z.writestr(f"3D/Objects/object_{pid}.model", mesh_file(pid, V1, T1))
            else:
                z.writestr(f"3D/Objects/object_{pid}.model", mesh_file(pid, V2, T2))
        z.writestr("Metadata/model_settings.config", model_settings(spec, with_instance, assemble_full))
        z.writestr("Metadata/project_settings.config", project_settings(n if n else len(spec)))
    return out3mf


def run(tag, out3mf):
    import shutil
    outdir = os.path.join(BUILD, f"out_{tag}")
    shutil.rmtree(outdir, ignore_errors=True)
    r = subprocess.run([BIN, "--slice", "1", "--outputdir", outdir, out3mf],
                       capture_output=True, text=True, timeout=900)
    gcode = os.path.join(outdir, "plate_1.gcode")
    if not os.path.exists(gcode):
        print(f"[{tag}] NO GCODE");  return
    head = open(gcode, "r", errors="replace").read(3000)
    total_layers = re.findall(r"; total layer number: (\d+)", head)
    length = re.findall(r"; total filament length \[mm\] : (.*)", head)
    fil = re.findall(r"; filament: (.*)", head)
    switches = []
    with open(gcode, "r", errors="replace") as f:
        for ln in f:
            m = re.match(r"^M620 S(\d+)A", ln)
            t = re.match(r"^(T\d+)\s*$", ln)
            if m:
                switches.append(f"M620 S{m.group(1)}")
            elif t and t.group(1) not in ("T1000", "T255"):
                switches.append(t.group(1))
            if len(switches) > 12:
                break
    print(f"[{tag}] layers={total_layers} len={length} fil={fil} switch={switches}")


if __name__ == "__main__":
    variants = [
        ("B2", [(1, "c1", 1, 12, 0.0, True), (3, "c2", 2, 12, Z2, True)],
         True, False),
        ("C", [(1, "c1", 1, 12, 0.0, True), (3, "c2", 2, 12, Z2, True)],
         False, True),
    ]
    for tag, spec, wi, af in variants:
        p = build(tag, spec, wi, af)
        run(tag, p)

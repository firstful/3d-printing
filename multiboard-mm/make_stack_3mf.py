#!/usr/bin/env python3
"""Compose a stacked multi-material MultiBoard .3mf project.

Stack design (for N boards of height 6.2, one AMS spool of interface material
"F_iface" printed between boards):

  part 0 : board_0   z = 0             filament slots[i0]
  part 1 : slab 1    z = 6.2           filament iface    (one layer, lh thick)
  part 2 : board_1   z = 6.4           filament slots[i1]
  part 3 : slab 2    z = 12.6          filament iface
  part 4 : board_2   z = 12.8          ...
  ...

The interface slab is EXACTLY one slice layer high (lh must divide 6.2), so
boards stack directly on top of each other with a single interface colour
layer between them.

Verified 3MF contract (Bambu Studio CLI 2.8.2.61, P1S) - this is what the CLI
honours, validated on stacked cubes with real tool changes:
  * ONE <object> + MULTIPLE <part id="odd"> blocks in Metadata/
    model_settings.config, part ids = mesh-file object ids (1,3,5,...)
  * every part carries <metadata key="extruder" value="slot"/> (1-based)
  * part transform lives in the part <metadata key="matrix"> (16 values,
    row-major, tz at value 12); the 3dmodel component transform mirrors it
  * every part has its own mesh file 3D/Objects/object_<pid>.model whose
    <object id> equals the part id; component objectid matches
  * plate block needs <model_instance> (object_id/instance_id/identify_id)
  * model_settings may be roughly paired with a self-closing <assemble/>
  * project_settings: filament count = len(filament_colour); filament-domain
    arrays scaled to n; printer arrays (extruder_type etc.) stay 1/2 entries;
    extruder_max_nozzle_count/extruder_nozzle_stats/extruder_nozzle_stats_new/
    filament_nozzle_map/filament_volume_map/filament_extruder_compatibility
    REMOVED; flush_volumes_matrix is n x n (diag 0)

Usage:
  python3 make_stack_3mf.py --out build/stack.3mf [--boards 3] [--lh 0.2]
      [--slots 1,2,3 --interface-slot 4] [--x 128 --y 128]
      [--board-stl build/board.stl] [--slab-stl build/interface_0.2.stl]
"""
import argparse
import json
import os
import struct
import sys
import uuid
import zipfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD_H = 6.2          # one plate, mm
BED = 256.0            # P1S printable square
DT = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])


def read_stl(path):
    with open(path, "rb") as f:
        data = f.read()
    n = struct.unpack_from("<I", data, 80)[0]
    arr = np.frombuffer(data, dtype=DT, count=n, offset=84)
    return arr["v"].reshape(-1, 3, 3).astype(np.float64)


def weld_mesh(tris):
    """Weld duplicated vertices (Octet-keyed). Return (verts, index-triples)."""
    vbits = tris.astype(np.float32).view(np.uint32).reshape(-1, 3)
    keys = {}
    out = []
    for k in map(tuple, vbits):
        if k not in keys:
            keys[k] = len(keys)
    verts = [None] * len(keys)
    for k, j in keys.items():
        verts[j] = struct.unpack("<fff", struct.pack("<III", *k))
    idx = np.array([keys[k] for k in map(tuple, vbits)]).reshape(-1, 3)
    return verts, idx


def mesh_file(pid, verts, tris, name):
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<model unit="millimeter" xml:lang="en-US" '
         'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
         'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
         'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" '
         'requiredextensions="p">',
         ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
         ' <resources>', f'  <object id="{pid}" type="model">', '   <mesh>',
         '    <vertices>']
    L += ['     <vertex x="%.5f" y="%.5f" z="%.5f"/>' % v for v in verts]
    L += ['    </vertices>', '    <triangles>']
    L += ['     <triangle v1="%d" v2="%d" v3="%d"/>' % tuple(t) for t in tris]
    L += ['    </triangles>', '   </mesh>', '  </object>', ' </resources>',
          '</model>']
    return "\n".join(L)


def part_xml(pid, name, extruder, faces, tz):
    return [
        f'    <part id="{pid}" subtype="normal_part" uuid="{uuid.uuid4()}">',
        f'      <metadata key="name" value="{name}"/>',
        f'      <metadata key="extruder" value="{extruder}"/>',
        f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 {tz:.12f} 0 0 0 1"/>',
        f'      <metadata key="source_file" value="{name}"/>',
        '      <metadata key="source_object_id" value="0"/>',
        '      <metadata key="source_volume_id" value="0"/>',
        '      <metadata key="source_offset_x" value="0"/>',
        '      <metadata key="source_offset_y" value="0"/>',
        f'      <metadata key="source_offset_z" value="{tz:.12f}"/>',
        f'      <mesh_stat face_count="{faces}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>',
        '    </part>']


def user_project_settings(n, lh, colors):
    """project_settings.config payload, following the four_mat.3mf contract
    verbatim distinction between filament-domain (len n) and printer-domain
    (len 1/2, untouched) arrays."""
    ps = json.load(open(os.path.join(HERE, "refx-p1s-project_settings.json")))
    # job overrides
    ps["enable_support"] = "0"
    ps["support_type"] = "normal(auto)"
    ps["elefant_foot_compensation"] = "0"
    ps["enable_prime_tower"] = "1"
    ps["print_sequence"] = "by layer"
    ps["layer_height"] = str(lh)
    ps["initial_layer_print_height"] = str(lh)
    # flush/purge machinery
    mat = []
    for i in range(n):
        for j in range(n):
            mat.append("0" if i == j else "280")
    ps["flush_volumes_matrix"] = mat
    ps["flush_volumes_vector"] = ["140"] * 8
    # filament domain
    ps["filament_colour"] = (colors + ["#7841CE"] * n)[:n]
    ps["filament_type"] = ["PLA"] * n
    ps["nozzle_temperature"] = ["220"] * n
    ps["nozzle_temperature_initial_layer"] = ["220"] * n
    ps["nozzle_temperature_range_high"] = ["240"] * n
    ps["nozzle_temperature_range_low"] = ["190"] * n
    ps["filament_density"] = ["1.26"] * n
    ps["filament_diameter"] = ["1.75"] * n
    ps["filament_map"] = ["1"] * n
    ps["default_nozzle_volume_type"] = ["Standard"] * n
    # pad remaining filament-domain singleton arrays to n
    for k, v in list(ps.items()):
        if k.startswith("filament_") and isinstance(v, list) and len(v) == 1:
            ps[k] = v * n
    bev = ps.get("filament_extruder_variant", [])
    if isinstance(bev, list) and 2 <= len(bev) < n:
        ps["filament_extruder_variant"] = \
            (bev * ((n + len(bev) - 1) // len(bev)))[:n]
    # keys the 4-filament reference does NOT carry
    for k in ("filament_nozzle_map", "filament_volume_map",
              "extruder_max_nozzle_count", "extruder_nozzle_stats",
              "extruder_nozzle_stats_new", "filament_extruder_compatibility"):
        ps.pop(k, None)
    # AMS signature: single print-extruder row, matching the verified file
    ps["extruder_ams_count"] = ["1#0|3"] if n == 4 else ["1#0|4#0"]
    ps["printer_model"] = "Bambu Lab P1S"
    ps["printer_settings_id"] = "Bambu Lab P1S 0.4 nozzle"
    ps["printer_variant"] = "0.4"
    return ps


def build(args):
    out = args.out
    os.makedirs(os.path.dirname(out), exist_ok=True)
    board_tris = read_stl(args.board_stl)
    slab_tris = read_stl(args.slab_stl)
    board_faces = len(board_tris)
    slab_faces = len(slab_tris)
    print(f"board STL: {board_faces} tris; slab STL: {slab_faces} tris")

    lh = args.lh
    assert abs(BOARD_H / lh - round(BOARD_H / lh)) < 1e-6, (
        f"layer height {lh} does not evenly divide board height {BOARD_H}")
    n_b = args.boards
    slots = [int(x) for x in args.slots.split(",")]
    assert len(slots) == n_b, "--slots needs one slot (1-based) per board"
    fi = args.interface_slot
    nf = max(4, fi, max(slots))
    colors = ["#D4E022", "#FF6A00", "#0080FF", "#808080"]  # seat colors demo
    ps = user_project_settings(nf, lh, colors)

    # per-part layout
    parts = []
    for i in range(n_b):
        parts.append(dict(kind="board", z=i * (BOARD_H + lh),
                          extruder=slots[i], faces=board_faces,
                          name=f"board_{i}"))
    for j in range(n_b - 1):
        parts.insert(2 * j + 1,
                     dict(kind="iface", z=BOARD_H + j * (BOARD_H + lh),
                          extruder=fi, faces=slab_faces, name=f"interface_{j+1}"))
    # part ids = odd increments 1,3,5,...; partition into mesh files
    pids = [2 * k + 1 for k in range(len(parts))]
    for k, p in enumerate(parts):
        p["pid"] = pids[k]
        p["mesh"] = f"object_{p['pid']}.model"

    zstep = BOARD_H + lh
    zmax = (n_b - 1) * zstep + BOARD_H
    assert zmax <= 256 and (n_b - 1) * zstep + BOARD_H <= 250, "stack fit"

    # ---- 3dmodel.model ----
    comps = []
    for p in parts:
        comps.append(f'    <component p:path="/3D/Objects/{p["mesh"]}" '
                     f'objectid="{p["pid"]}" '
                     f'transform="1 0 0 0 1 0 0 0 1 0 0 {p["z"]:.12f}"/>')
    model = "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
        'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
        'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" '
        'requiredextensions="p">',
        ' <metadata name="Application">BambuStudio-02.08.02.61</metadata>',
        ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
        ' <metadata name="Title">MultiBoard stacked with single-layer '
        'M_interface between boards</metadata>',
        ' <metadata name="Description">'
        f'{n_b} boards + {n_b-1} single-layer interface slabs, lh={lh}</metadata>',
        ' <resources>',
        '  <object id="1" type="models">'.replace("models", "model"),
        '   <components>',
        ] + comps + [
        '   </components>',
        '  </object>',
        ' </resources>',
        ' <build>',
        f'  <item objectid="1" transform="1 0 0 0 1 0 0 0 1 {args.x:.3f} '
        f'{args.y:.3f} 0" printable="1"/>',
        ' </build>',
        '</model>']) + "\n"

    # ---- model_settings.config ----
    ms = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>',
          '  <object id="1">',
          '    <metadata key="name" value="multiboard_stack"/>',
          f'    <metadata key="extruder" value="{slots[0]}"/>',
          f'    <metadata face_count="{board_faces + slab_faces}"/>']
    for p in parts:
        ms += part_xml(p["pid"], p["name"], p["extruder"], p["faces"], p["z"])
    ms += ['  </object>',
           '  <plate>',
           '    <metadata key="plater_id" value="1"/>',
           '    <metadata key="plater_name" value="plate 1"/>',
           '    <metadata key="locked" value="false"/>',
           '    <metadata key="filament_map_mode" value="Auto For Flush"/>',
           f'    <metadata key="filament_maps" value="{" ".join(["1"] * nf)}"/>',
           f'    <metadata key="filament_volume_maps" value="{" ".join(["0"] * nf)}"/>',
           '    <metadata key="gcode_file" value=""/>',
           '    <model_instance>',
           '      <metadata key="object_id" value="1"/>',
           '      <metadata key="instance_id" value="0"/>',
           '      <metadata key="identify_id" value="1"/>',
           '    </model_instance>',
           '  </plate>',
           '  <assemble/>',
           '</config>']
    ms = "\n".join(ms) + "\n"

    # ---- package ----
    ct = open(os.path.join(HERE, "refx", "[Content_Types].xml")).read()
    rel0 = open(os.path.join(HERE, "refx", "_rels", ".rels")).read()
    rels = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<Relationships '
            'xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    unique_meshes = {}
    for p in parts:
        unique_meshes[p["mesh"]] = p["pid"]
    for m in sorted(unique_meshes):
        rels.append(f' <Relationship Target="/3D/Objects/{m}" '
                    f'Id="rel-{unique_meshes[m]}" '
                    'Type="http://schemas.microsoft.com/3dmanufacturing/'
                    '2013/01/3dmodel"/>')
    rels.append('</Relationships>')

    print(f"stack: {n_b} boards @ lh {lh}: {n_b}x{int(6.2/lh)} board layers + "
          f"{n_b-1} interface layers; total {zmax:.2f} mm")
    print("part map:")
    for p in parts:
        print(f"  part {p['pid']:>2} {p['name']:<12} extruder {p['extruder']} "
              f"z {p['z']:.2f} ({p['faces']} faces)")

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED,
                         compresslevel=6) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rel0)
        z.writestr("3D/_rels/3dmodel.model.rels", "\n".join(rels))
        z.writestr("3D/3dmodel.model", model)
        # cached welds (boar mesh is heavy, keep only unique contents)
        cache = {}
        for p in parts:
            if p["kind"] == "board":
                key = "board"
            else:
                key = "slab"
            if key not in cache:
                cache[key] = weld_mesh(board_tris if key == "board" else slab_tris)
            bverts, btris = cache["board"] if key == "board" else cache["slab"]
            z.writestr("3D/Objects/" + p["mesh"],
                       mesh_file(p["pid"], bverts, btris, p["name"]))
        z.writestr("Metadata/model_settings.config", ms)
        z.writestr("Metadata/project_settings.config",
                   json.dumps(ps, separators=(",", ":")))
    print(f"wrote {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--boards", type=int, default=3)
    ap.add_argument("--lh", type=float, default=0.2)
    ap.add_argument("--slots", default="1,2,3",
                    help="1-based AMS filament slot per board (default 1,2,3)")
    ap.add_argument("--interface-slot", type=int, default=4)
    ap.add_argument("--x", type=float, default=128.0)
    ap.add_argument("--y", type=float, default=128.0)
    ap.add_argument("--board-stl",
                    default=os.path.join(HERE, "build", "board.stl"))
    ap.add_argument("--slab-stl", default="")
    args = ap.parse_args()
    if not args.slab_stl:
        s = ("%0.2f" % args.lh).rstrip("0").rstrip(".")
        args.slab_stl = os.path.join(HERE, "build", f"interface_{s}.stl")
    if not os.path.exists(args.slab_stl):
        alt = os.path.join(HERE, "build", "interface_0.2.stl")
        args.slab_stl = alt if os.path.exists(alt) else args.slab_stl
    if not os.path.exists(args.slab_stl):
        sys.exit("slab STL missing; run make_interface.py first")
    if not os.path.exists(args.board_stl):
        sys.exit("board STL missing")
    build(args)


if __name__ == "__main__":
    main()

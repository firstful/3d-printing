#!/usr/bin/env python3
"""Build a multi-object 3MF assembly from STLs.

Each STL is already in final assembly coordinates, so every build item uses an
identity transform. Vertices are welded before writing; without welding Bambu
Studio sees every triangle as its own floating shell.

Usage:
    python3 tools/build_3mf.py --out fishtank-gantry.3mf \
        "Rail left=stl/asm/asm_rail_left.stl" ...
"""
import argparse
import os
import struct
import zipfile


def read_stl(path):
    data = open(path, "rb").read()
    if len(data) >= 84:
        n = struct.unpack_from("<I", data, 80)[0]
        if 84 + n * 50 == len(data):
            tris = []
            off = 84
            for _ in range(n):
                vals = struct.unpack_from("<12f", data, off)
                tris.append((vals[3:6], vals[6:9], vals[9:12]))
                off += 50
            return tris
    text = data.decode("utf-8", errors="ignore")
    tris, cur = [], []
    for line in text.splitlines():
        s = line.strip()
        if s.lower().startswith("vertex"):
            p = s.split()
            cur.append((float(p[1]), float(p[2]), float(p[3])))
            if len(cur) == 3:
                tris.append(tuple(cur))
                cur = []
    return tris


def weld(tris, q=1e-5):
    idx, verts, faces = {}, [], []
    for tri in tris:
        face = []
        for p in tri:
            key = (round(p[0] / q), round(p[1] / q), round(p[2] / q))
            if key not in idx:
                idx[key] = len(verts)
                verts.append(p)
            face.append(idx[key])
        faces.append(face)
    return verts, faces


def xml_escape(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("parts", nargs="+", help='Name=path.stl')
    args = ap.parse_args()

    parts = []
    for spec in args.parts:
        name, path = spec.split("=", 1)
        parts.append((name, path))

    model = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
             ' <resources>']
    settings = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>']
    build = [' <build>']

    for oid, (name, path) in enumerate(parts, start=1):
        tris = read_stl(path)
        verts, faces = weld(tris)
        model.append(f'  <object id="{oid}" type="model" name="{xml_escape(name)}">')
        model.append('   <mesh>')
        model.append('    <vertices>')
        for x, y, z in verts:
            model.append(f'     <vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>')
        model.append('    </vertices>')
        model.append('    <triangles>')
        for a, b, c in faces:
            model.append(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>')
        model.append('    </triangles>')
        model.append('   </mesh>')
        model.append('  </object>')
        settings.append(f'  <object id="{oid}">')
        settings.append(f'   <metadata key="name" value="{xml_escape(name)}"/>')
        settings.append('  </object>')
        build.append(f'  <item objectid="{oid}"/>')
        print(f"  {oid:2d}  {name:30s} {len(tris):7d} tris, {len(verts):6d} welded verts")

    model += [' </resources>', ' <build>'] + build[1:] + ['</build>', '</model>']
    settings += ['</config>']

    content_types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>
'''
    rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
'''
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", "\n".join(model))
        z.writestr("Metadata/model_settings.config", "\n".join(settings))
    print(f"wrote {args.out} ({os.path.getsize(args.out)//1024} KB)")


if __name__ == "__main__":
    main()

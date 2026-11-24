import numpy as np, trimesh, subprocess, os

proj = "/home/reed/opencode-sessions/hex-ramp-insert"
O = os.path.expanduser("~/opencode-sessions/siphon-strainer/OpenSCAD.AppImage")
subprocess.run([O, "--backend", "Manifold", "-D", 'mode="use"',
                "-o", f"{proj}/build/insert_use.stl",
                f"{proj}/scad/hex_ramp_insert.scad"], check=True, capture_output=True)

ramp = trimesh.load("/home/reed/opencode-sessions/ramp-half-hex/ramp_half_hex.stl")
ins = trimesh.load(f"{proj}/build/insert_use.stl")
print("insert bbox", np.round(ins.bounds, 2).tolist(), "vol", round(ins.volume / 1000, 3))

SLOPE, IC = 0.130691, 13.8003
for x0, z0 in ((16.189, 22.86), (16.189, 114.30), (16.189, 205.74)):
    pos = trimesh.transformations.translation_matrix([x0, SLOPE * x0 + IC, z0])
    c = ins.copy(); c.apply_transform(pos)
    inter = trimesh.boolean.intersection([ramp, c], engine="manifold")
    v = inter.volume if inter is not None else 0
    print(f"hole ({x0}, {z0}): intersection {v:.4f} mm3")

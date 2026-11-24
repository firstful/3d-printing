"""Fit check with both ramp halves present."""
import numpy as np, trimesh, subprocess, os

proj = "/home/reed/opencode-sessions/hex-ramp-clip"
O = os.path.expanduser("~/opencode-sessions/siphon-strainer/OpenSCAD.AppImage")
subprocess.run([O, "--backend", "Manifold", "-D", 'mode="use"',
                "-o", f"{proj}/build/clip_use.stl",
                f"{proj}/scad/hex_ramp_clip.scad"], check=True, capture_output=True)

ramp = trimesh.load("/home/reed/opencode-sessions/ramp-half-hex/ramp_half_hex.stl")
rampB = ramp.copy()
rampB.apply_translation([0, 0, 228.6])
clip = trimesh.load(f"{proj}/build/clip_use.stl")

SLOPE, IC = 0.130691, 13.8003
for x0 in (-43.203, -3.609):
    pos = trimesh.transformations.translation_matrix([x0, SLOPE * x0 + IC, 228.6])
    c = clip.copy(); c.apply_transform(pos)
    tot = 0
    for name, r in (("A", ramp), ("B", rampB)):
        inter = trimesh.boolean.intersection([r, c], engine="manifold")
        v = inter.volume if inter else 0
        tot += v
        print(f"x0={x0} ramp{name}: {v:.4f} mm3")
    print(f"x0={x0} total {tot:.4f} mm3")
    print()

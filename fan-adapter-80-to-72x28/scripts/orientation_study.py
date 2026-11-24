#!/usr/bin/env python3
"""Generate rotated STL variants for print-orientation comparison."""
import re
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "preview" / "fan_adapter.stl"
OUT = ROOT / "build" / "orient"
OUT.mkdir(parents=True, exist_ok=True)


def load_stl(path):
    txt = path.read_text()
    v = [tuple(map(float, t)) for t in re.findall(
        r"vertex\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)", txt)]
    return np.array(v).reshape(-1, 3, 3)


def write_stl(tris, path):
    with path.open("w") as f:
        f.write("solid orient\n")
        for tri in tris:
            f.write("  facet normal 0 0 0\n    outer loop\n")
            for p in tri:
                f.write(f"      vertex {p[0]:.6f} {p[1]:.6f} {p[2]:.6f}\n")
            f.write("    endloop\n  endfacet\n")
        f.write("endsolid orient\n")


def rot_x(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_z(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


D = np.pi / 180
variants = {
    "00_flange_down": np.eye(3),
    "01_outlet_down": rot_y(90 * D),     # -X normal -> -Z (rim faces down)
    "02_outlet_up":   rot_y(-90 * D),    # -X normal -> +Z (rim faces up)
    "03_bendaxis_vertical": rot_x(90 * D),
    "04_bendaxis_vertical_flip": rot_x(-90 * D),
    "05_flange_up": rot_x(180 * D),
}

tris0 = load_stl(SRC)
for name, R in variants.items():
    tris = tris0 @ R.T
    tris[:, :, 2] -= tris[:, :, 2].min()   # sit on bed
    write_stl(tris, OUT / f"{name}.stl")
    print(name)

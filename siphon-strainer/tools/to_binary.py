#!/usr/bin/env python3
"""Convert OpenSCAD ASCII STL to compact binary STL (numpy)."""
import sys
import struct
import numpy as np


def convert(src, dst):
    with open(src, "rb") as f:
        head = f.read(6)
    if not head.lstrip().startswith(b"solid"):
        with open(src, "rb") as f, open(dst, "wb") as g:
            g.write(f.read())
        print(f"{src}: already binary, copied -> {dst}")
        return

    with open(src, "rb") as f:
        lines = f.read().split(b"\n")
    verts = [ln.split()[1:4] for ln in lines
             if ln.lstrip().startswith(b"vertex")]
    del lines
    v = np.array(verts, dtype=np.float64).reshape(-1, 3, 3)
    n = v.shape[0]

    e1 = v[:, 1] - v[:, 0]
    e2 = v[:, 2] - v[:, 0]
    normals = np.cross(e1, e2)
    ln = np.linalg.norm(normals, axis=1)
    ln[ln == 0] = 1.0
    normals /= ln[:, None]

    dt = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    out = np.zeros(n, dtype=dt)
    out["n"] = normals
    out["v"] = v
    out["a"] = 0

    with open(dst, "wb") as f:
        f.write(b"binary STL from " + src.encode()[:64].ljust(64, b" ")[:64])
        f.write(struct.pack("<I", n))
        out.tofile(f)
    print(f"{src}: {n} facets -> {dst}")


if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])

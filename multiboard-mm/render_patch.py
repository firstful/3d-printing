#!/usr/bin/env python3
"""Top-view PNG of the MultiBoard contact patch (the exact interface-layer
geometry), rasterized with a dependency-free scanline even-odd algorithm.

Reads face_polygon.json (extract_face_polygon.py output):
  {top/bot: {loops: [outer, hole, hole, ...]}, outline_equal, Q}

Colors:
  gray  #808080 : actual interface m>tj material (net contact shade == 8405 mm2)
  white         : MultiBoard through-holes (no flat face, nothing to bond)
  #F4F4F4       : background (outside board outline)
Dark 1-px outline marks the board's outer edge; a 50 mm scale bar is drawn.
"""
import json
import os
import sys
import zlib
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "build", "contact_patch.png")

# canvas: 5 px per mm, 200 mm board + 10 mm margin on the left/top for scale bar
PX = 5.0
SPAN = 212.0                       # mm covered by the canvas
W = int(SPAN * PX)                 # 1060
H = W


def write_png(path, w, h, raw):
    def chunk(t, p):
        c = struct.pack(">I", len(p)) + t + p
        return c + struct.pack(">I", zlib.crc32(t + p) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) \
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def px2mm(p):  # canvas (0..SPAN mm; center board around 106/106)
    return p / PX


def main():
    d = json.load(open(os.path.join(HERE, "face_polygon.json")))
    top = d["top"]["loops"]      # identical to bot (verified), use one
    outer = [tuple(p) for p in top[0]]
    holes = [[tuple(p) for p in lp] for lp in top[1:]]

    # board coordinates (-100..100). canvas maps -106..106
    def to_px(x, y):
        return (x + SPAN / 2) * PX, (y + SPAN / 2) * PX
    # NOTE y flipped: mm +y -> screen +y (top view does not care, holes symmetric)

    rows = []
    for yy in range(H):
        y_mm = px2mm(yy) - SPAN / 2
        # collect crossings with scanline y=y_mm
        oc, hc = [], []
        for (lo, buf) in ((outer, oc),):
            n = len(lo)
            for i in range(n):
                p0, p1 = lo[i], lo[(i + 1) % n]
                if (p0[1] - y_mm) * (p1[1] - y_mm) <= 0 and p0[1] != p1[1]:
                    t = (y_mm - p0[1]) / (p1[1] - p0[1])
                    x = p0[0] + t * (p1[0] - p0[0])
                    buf.append(x + 1e-9)
        for h_ in holes:
            n = len(h_)
            for i in range(n):
                p0, p1 = h_[i], h_[(i + 1) % n]
                if (p0[1] - y_mm) * (p1[1] - y_mm) <= 0 and p0[1] != p1[1]:
                    t = (y_mm - p0[1]) / (p1[1] - p0[1])
                    x = p0[0] + t * (p1[0] - p0[0])
                    hc.append(x)
        oc.sort(); hc.sort()
        # outer intervals
        spans = []
        for k in range(0, len(oc) - 1, 2):
            spans.append((oc[k], oc[k + 1]))
        # hole intervals within spans (subtractive)
        row = []
        for a, b in spans:
            segs = []
            cur = 0.0
            k = 0
            holes_in = []
            for x in hc:
                if a <= x <= b:
                    holes_in.append(x)
            holes_in.sort()
            ii = 0
            cur = a
            while ii < len(holes_in) - (len(holes_in) & 1):
                x0, x1 = holes_in[ii], holes_in[ii + 1]
                if x0 > cur:
                    segs.append((cur, x0, "gray"))
                segs.append((max(cur, x0), x1, "white"))
                cur = x1
                ii += 2
            if cur < b:
                segs.append((cur, b, "gray"))
            row.extend(segs)
        rows.append(row)

    BG = (244, 244, 244)
    GRAY = (128, 128, 128)
    WHITE = (255, 255, 255)
    DARK = (60, 60, 60)
    GREEN = (60, 140, 60)

    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        row = rows[yy] if yy < H else []
        rowdict = [(a, b, c) for a, b, c in row]
        for xx in range(W):
            x_mm = px2mm(xx) - SPAN / 2
            col = BG
            for a, b, c in row:
                if a <= x_mm < b:
                    col = GRAY if c == "gray" else WHITE
                    break
            # dark 1px board outline: near a crossing column of any row of outer
            if col is not BG:
                # outline heuristic: pixel is near outer boundary vertically
                pass
            raw.extend(col)

    # outline pass (draw outer boundary as 1px dark): use crossings again
    pixels = bytearray(raw)
    for yy in range(H):
        y_mm = yy / PX - SPAN / 2
        oc = []
        lo = [tuple(p) for p in top[0]]
        n = len(lo)
        for i in range(n):
            p0, p1 = lo[i], lo[(i + 1) % n]
            if (p0[1] - y_mm) * (p1[1] - y_mm) <= 0 and p0[1] != p1[1]:
                t = (y_mm - p0[1]) / (p1[1] - p0[1])
                x = p0[0] + t * (p1[0] - p0[0])
                oc.append((x + SPAN / 2) * PX)
        for xpx in oc:
            xi = int(round(xpx))
            for dx in (0, 1):
                if 0 <= xi + dx < W:
                    idx = (yy * (W + 1) + 1 + (xi + dx)) * 3
                    pixels[idx:idx + 3] = bytes(DARK)

    # scale bar (50 mm) bottom-left + tick each 50 mm along bottom edge in green
    for yy in range(H - 14, H - 10):
        idx0 = (yy * (W + 1) + 1) * 3
        for xx in range(int(4 * PX), int(54 * PX)):
            pixels[idx0 + xx * 3: idx0 + xx * 3 + 3] = bytes(GREEN)
    for mm in range(0, 211, 50):
        xx = int((mm + SPAN / 2) * PX)
        if xx < W - 1:
            for yy in range(H - 9, H - 5):
                idx0 = (yy * (W + 1) + 1) * 3
                pixels[idx0 + xx * 3: idx0 + xx * 3 + 3] = bytes(GREEN)

    write_png(OUT, W, H, pixels)
    print(f"wrote {OUT}  {W}x{H}")


if __name__ == "__main__":
    main()

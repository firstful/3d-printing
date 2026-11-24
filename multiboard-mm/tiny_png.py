#!/usr/bin/env python3
"""Tiny dependency-free PNG exporter (8-bit RGB, one draw call each)."""
import struct
import zlib


def write_png(path, w, h, pixel_fn):
    """pixel_fn(x, y) -> (r, g, b) ints 0..255"""
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # filter none
        for x in range(w):
            raw.extend(pixel_fn(x, y))
    png = bytearray(b'\x89PNG\r\n\x1a\n')
    for chunk_type, payload in (
        (b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)),
        (b'IDAT', zlib.compress(bytes(raw), 6)),
        (b'IEND', b''),
    ):
        png.extend(struct.pack('>I', len(payload)))
        png.extend(chunk_type)
        png.extend(payload)
        png.extend(struct.pack('>I', zlib.crc32(chunk_type + payload)))
    with open(path, 'wb') as f:
        f.write(bytes(png))

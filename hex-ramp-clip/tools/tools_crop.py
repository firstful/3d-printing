"""Crop PNGs to their non-background content and trim empty margins."""
import sys
from PIL import Image, ImageChops
import numpy as np


def crop(path, out, pad=24, scale=1):
    im = Image.open(path).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 253, 231))
    diff = ImageChops.difference(im, bg)
    arr = np.asarray(diff).sum(axis=2)
    ys, xs = np.where(arr > 18)
    if len(xs) == 0:
        print("empty", path)
        return
    box = (max(0, xs.min() - pad), max(0, ys.min() - pad),
           min(im.width, xs.max() + pad), min(im.height, ys.max() + pad))
    out_im = im.crop(box)
    if scale != 1:
        out_im = out_im.resize((int(out_im.width * scale), int(out_im.height * scale)),
                               Image.LANCZOS)
    out_im.save(out)
    print(out, out_im.size)


if __name__ == "__main__":
    crop(sys.argv[1], sys.argv[2],
         int(sys.argv[3]) if len(sys.argv) > 3 else 24,
         float(sys.argv[4]) if len(sys.argv) > 4 else 1)

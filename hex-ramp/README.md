# hex-ramp — tileable hex lightening

Source: `reference/ramp_half.stl` ("Ramp half 18in (no holes)",
137.0 × 17.9 × 228.6 mm, 195 cm³). Holes are cut along **Y**, which is the
part's thickness axis and the print's vertical axis in the supplied project — so
every hole is a straight vertical bore and the part still prints support-free in
the same orientation.

## Result (committed model)

| | original | hex version |
|---|---|---|
| solid volume | 194.9 cm³ | **105.6 cm³** (−45.8 %) |
| bbox | 137.03 × 17.91 × 228.60 | unchanged |
| holes | 0 | **57** through-holes |
| watertight / bodies / degenerate | – | yes / 1 / 0 |
| sliced (their 3MF settings) | 128.6 g, 3.78 h | **109.1 g, 3.50 h** |
| supports | 0 | 0 |

Sliced with the project's own profile (P1S, 0.2 mm, 6 walls, 25 % gyroid), which
is carried inside `mf/` and re-applied by `make_3mf.py`. This revision is
−19.5 g (−15 %) and −0.3 h versus the solid original.

## Pattern

- Flat-top regular hexagons, **15.86 mm across flats**, **7.0 mm ribs**,
  48 % open area on the lattice, 57 holes.
- Lattice pitch p = 228.6/10 = 22.86 mm; rows every `p/2`, alternating
  half-pitch offset → mirror-symmetric about **both** Z edges, so the second half
  of the ramp butts on with an uninterrupted honeycomb and a normal-width rib on
  the joint (seam land = web/2 = 3.5 mm per half).
- Holes are kept wherever the local plate is at least **1.0 mm** thick
  (`--min-t 1.0`). That perforates most of the taper; the last ~20 mm of feather
  edge and the rolled lip (x > 16) stay solid because a hole there would only
  leave a knife edge.
- Holes span x = −82.8 … +16.2 mm, z = 11.4 … 217.2 mm; 57 through-holes.
  Hole centres are `build/coarse_more_hexes.npy` in the working copy (regenerate
  with the command below).

## Rebuild / retune

Run from this directory (needs `numpy` + `trimesh` with the `manifold` boolean
engine):

```bash
python build.py --src reference/ramp_half.stl --web 7 --rows 10 --min-t 1.0 \
                --out ramp_half_hex.stl
python make_3mf.py ramp_half_hex.stl ramp_half_hex.3mf
```

`--web` rib width, `--rows` lattice rows (p = 228.6/rows), `--min-t` thinnest
material that may be perforated. The exact committed STL is reproduced by the
command above (verify with `md5sum`: `bc9025c0f203e2a6451569999c801825`).

`make_3mf.py` patches the user's original Bambu project in `mf/` with the new
mesh, so the plate origin, filament assignment and print profile are preserved.
`./slice.sh` re-slices the result headlessly and prints mass/time.

## Earlier variants (same slicer profile)

| variant | holes | across-flats | rib | solid vol | sliced |
|---|---|---|---|---|---|
| fine | 185 | 7.53 | 4.5 | −36 % | 151.1 g / 7.40 h |
| medium-thin | 167 | 9.53 | 2.5 | −56 % | 103.1 g / 5.08 h |
| **committed** | **57** | **15.86** | **7.0** | **−46 %** | **109.1 g / 3.50 h** |
| mid | 38 | 15.86 | 7.0 | −39 % | 119.4 g / 3.69 h |
| big | 22 | 20.58 | 8.0 | −40 % | 111.3 g / 3.45 h |

Small holes with wide ribs are the *heaviest* print: at 6 wall loops a 4.5 mm rib
is already 100 % wall, so the perforation just adds perimeter. Bigger holes with
thin ribs remove filament; the committed 57-hole lattice is the fastest option
that still cuts mass, because it keeps the same rib width as `mid` while fitting
more holes on the plate.

## Notes

- The 3MF is rebuilt from the committed STL, so the two files always match
  (8190 triangles).
- `mf/` is the unchanged Bambu project template (16 files); `project/` is its
  temporary working copy and is git-ignored.
- Previews in `preview/` were rendered across iterations; `cm_*` are the
  committed revision.

# hex-ramp-clip — seam clip for two ramp halves

Two hex pegs drop into the honeycomb holes either side of the butt seam
between two 228.6 mm ramp halves; a low chamfered bar bridges the seam on top.
Friction fit, glue for a permanent joint. Used in pairs, the result is the full
18 in (457.2 mm) wide ramp.

![clip in print orientation](preview/clip_print_iso.png)

## Fit

| | |
|---|---|
| ramp halves | `hex-ramp/` 57-hole revision (`ramp_half_hex.stl`) |
| hole | regular hexagon, **15.86 mm across flats**, vertices along ramp X, straight through-hole |
| hole depth | through; 8.1 mm of material at the x = −43.2 column, 13.4 mm at x = −3.6 |
| seam rows | holes at z = 11.43 mm in from each half → **22.86 mm c-c** across the joint, same X columns both sides |
| peg span | 22.86 mm |
| peg size | across flats = 15.86 − `clearance`; 0.30 mm total clearance = 0.15 mm/side on the medium variant |
| peg depth | 6.0 mm, 1.2 mm lead-in chamfer at the tip |
| bar | 24 (X) × 40 (Z) × 2.2 mm thick, 41° chamfer on the two X edges |
| ramp top | plane y = 0.130691·x + 13.8003, 7.446°; the bar underside is cut to that plane |

Seam-row hole columns are x = −82.80, −43.20 and −3.61. **Do not use the
−82.80 column** — the plate is only ~3.0 mm thick there and a 6 mm peg would
stick out of the bottom. Use −43.20 and −3.61, one clip each → two clips per
seam.

CSG check against the real ramp mesh: peg/ramp intersection **0.008 mm³**
(numerical noise from the coplanar bar underside) at both columns, with both
halves present.

## Print

Print the STL as exported: **Z up**, bar top face on the bed, pegs pointing up.
No supports (0 support moves with supports enabled in the slicing test).

| variant | peg across flats | clearance | solid vol | slicer mass |
|---|---|---|---|---|
| `hex_ramp_clip_tight.stl` | 15.76 | 0.10 (0.05/side) | 4.50 cm³ | — |
| `hex_ramp_clip_medium.stl` | 15.56 | 0.30 (0.15/side) | 4.43 cm³ | **4.48 g / 0.16 h** |
| `hex_ramp_clip_loose.stl` | 15.36 | 0.50 (0.25/side) | 4.37 cm³ | — |

Sliced with the hex-ramp project's own profile (P1S, 0.2 mm, 6 walls, 25 %
gyroid, supports forced on). Start with the medium; go tighter if the fit is
sloppy on your printer, looser if the prints do not butt cleanly.

Assembly: butt the two halves, drop a clip into each of the two usable hole
columns, press down. A drop of CA or model glue in the holes makes it permanent.
If your prints leave a gap at the seam the pegs will not straddle it; re-render
with `span = 22.86 + gap`.

## Rebuild

```bash
# one STL per fit variant
for v in "tight 0.10" "medium 0.30" "loose 0.50"; do set -- $v
  openscad -D clearance=$2 -o stl/hex_ramp_clip_$1.stl scad/hex_ramp_clip.scad
done

# fit check against the real ramp mesh (needs a trimesh venv)
python tools/fitcheck.py

# slice (wraps the STL in the hex-ramp Bambu project profile)
python tools/make_3mf.py stl/hex_ramp_clip_medium.stl build/clip.3mf
~/Applications/BambuStudio.AppImage --slice 1 --outputdir build/slice build/clip.3mf
```

Previews: `scad/assembly.scad` and `scad/closeup.scad` import the ramp STL
(`ramp_stl` at the top of each file) and are view-only, not printable parts.

![close-up of the seam](preview/closeup_top.png)

![section through the peg](preview/section.png)

![joined halves](preview/assembly.png)

## Provenance

Ramp geometry measured from `hex-ramp/ramp_half_hex.stl` (Reed's 57-hole
revision of "Ramp half 18in (no holes)"). The clip is original. No third-party
mesh is committed here; the preview scripts reference the ramp STL by path.

## Safety

Small parts — keep away from children who mouth objects. Not load-bearing; do
not stand or kneel on the joined ramp.

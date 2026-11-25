# I-beam joiner — 6" (152.4 mm) I-beam, split & screwed

Solid I-beam, 152.4 mm long, split at the middle into two 76.2 mm halves
joined with printed M4 screws through the top and bottom flanges.

## Cross-section

| | |
|---|---|
| flange width | 15 mm |
| flange thickness | 4 mm |
| web width | 11 mm |
| web height | 8 mm |
| total height | 16 mm |

## Parts

- `stl/i_beam_half_a.stl` — threaded half (M4 threads in top/bottom flanges)
- `stl/i_beam_half_b.stl` — clearance half (4.4 mm holes)
- `stl/i_beam_screw.stl` — M4 printed screw (×4 needed)

## Assembly

1. Print 2× half A, 2× half B? No — print 1× A and 1× B.
2. Align the two halves end-to-end at the middle.
3. Insert 2 screws from the top (through top flange of B into A).
4. Insert 2 screws from the bottom (through bottom flange of B into A).
5. Tighten until snug.

## Print

No supports needed. Print with the beam length horizontal (as exported).

## Rebuild

```bash
openscad -D mode='"half_a"' -o stl/i_beam_half_a.stl scad/i_beam.scad
openscad -D mode='"half_b"' -o stl/i_beam_half_b.stl scad/i_beam.scad
openscad -D mode='"screw"'  -o stl/i_beam_screw.stl scad/i_beam.scad
```
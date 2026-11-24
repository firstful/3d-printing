# rocket-toniebox-holder

Replacement magnet discs for plate 7 of the Rocket Toniebox holder. The original
plate holds 3D-printed discs; this replaces them with flat Ø36 mm discs that each
carry a 6 × 2 mm neodymium magnet in a sealed internal pocket, so the magnet does
not need a visible hole or a glued-on cap.

## Disc

| | |
|---|---|
| diameter | 36 mm |
| height | 2.8 mm (0.2 bottom + 2.2 cavity + 0.4 top cover) |
| magnet pocket | Ø6.3 × 2.2 mm (6 mm magnet + 0.3 dia / 0.2 depth clearance) |
| layout | 3 × 3 grid, 40 mm pitch, in `discs_magnet.scad` |

The pocket is fully enclosed: one 0.2 mm layer seals the bottom and two 0.2 mm
layers seal the top. **Insert the magnets at a layer pause** once the pocket floor
is down — you cannot add them after the print. The model relies on the top cover
plus glue; the optional retention lip in the source is disabled.

## Files

| File | Purpose |
|---|---|
| `discs_magnet.scad` | Parametric disc; renders the 3 × 3 print plate |
| `discs_magnet.stl` | Exported plate of 9 discs |
| `rocket-toniebox-holder.3mf` | Original downloaded Bambu project (reference geometry) |
| `analyze_disc.py` | Measures the original disc geometry from the 3MF XML |

The original 3MF is kept as `.3mf` only; its extracted tree was re-zipped so the
repository does not carry thousands of loose model/thumbnail files.

## Printing

- PLA or PETG, 0.2 mm layers so the 0.2/0.4 mm covers land on exact layer lines.
- Print the 3 × 3 plate flat; no supports.
- 36 mm discs are small enough to print quickly; check magnet polarity across the
  whole plate before sealing it in. All discs must face the same way to hold the
  Toniebox.

## Provenance

Original holder model: `Rocket Toniebox Holder` 3MF (downloaded; author/licence
not recorded). `analyze_disc.py` was used to reverse-engineer the disc dimensions
from that file.

# fan-adapter-80-to-72x28

Right-angle duct adapter from an 80 mm case fan (71.5 mm M4 hole pitch, 76 mm
throat) to a 72 × 28 mm outlet. Air enters the fan flange along +Z, turns 70° in
the XZ plane (bend axis Y) and exits along −X. The fan flange has M4 clearance
holes plus zip-tie slots; the outlet has a 10 mm lip for a hose or screen.

## Which file to print

| File | Notes |
|---|---|
| `fixed/fan_adapter_fixed.stl` | **Solid-wall version.** Supersedes `stl/fan_adapter.stl` (see `fixed/FIX.txt` — the older mesh blocked half the inlet throat). 67.2 cm³ / 83.4 g, 2.0 mm wall. |
| `handoff/fan_adapter_light.stl` | **Light version.** Same interfaces, 1.0 mm wall and slimmer flange/rim: 34.0 cm³ / 42.1 g (−50 %). Prints slightly heavier with 3 perimeters. |
| `stl/fan_adapter.stl` | Superseded — do not print (blocked throat). |
| `stl/fan_adapter_bend70.stl` | Bend-70 flow-study variant used to pick the 70° geometry. |
| `stl/print_ready_outlet_rim_down.stl` | Earlier print-orientation variant (outlet rim down). |

## Source

- `scad/fan_adapter.scad` — original parametric model (solid wall).
- `fixed/fan_adapter_fixed.scad` — corrected flange-throat cut; single-line change
  in `fan_flange_base()`. Matches `fixed/fan_adapter_fixed.3mf`.
- `scad/fan_adapter_light.scad` — lightweight oval-outlet redesign
  (`handoff/README.txt` documents the mass/overhang measurements).
- `scad/_t*.scad` — iteration/scratch studies kept for history; not needed to
  build either final part.

## Printing

Print with the fan flange on the bed and the outlet pointing up (the orientation
in the 3MF). The 70° bend keeps the overhang under 30° so no supports are needed;
the light version measures 1.85 % of surface below 30° slope, all on the outlet
rim.

## Studies

`scripts/flow_study.py`, `scripts/orientation_study.py`, `scripts/section_check.py`
and `scripts/section_png.py` produced `preview/flow_*.png` and the section views.
They are analysis helpers, not part of the build.

## Related

`../fan-adapter-to-rook/` is a self-contained handoff bundle of the final solid
and bend-70 files for the Rook host. It duplicates these meshes by design.
